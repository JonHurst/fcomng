#!/usr/bin/python
# coding=utf-8

from globals import *

import xml.etree.cElementTree as et
import subprocess
import re
import tempfile
import meta

class FCOMFactory:

    def __init__(self, fcm):
        global g_paths
        self.fcm = fcm #instance of FCOMMeta
        versiondate = g_paths.control[-12:-4]
        self.versionstring = versiondate[:4] + "-" + versiondate[4:6] + "-" + versiondate[6:]
        self.revisions = []
        self.chunk_depth = 3


    def build_fcom(self):
        self.errorlog = open("build-error.log", "w")
        self.write_fleet_js()
        content_pages = []
        for ident in self.fcm.get_root_nodes():
            self._recursive_process_section(ident, content_pages)
        self.make_node_page(None)#make contents page
        for make_page_args in zip(content_pages,
                                  [None] + content_pages[:-1],
                                  content_pages[1:] + [None]):
            self.make_page(*make_page_args)
        self.make_revision_list() # this must be done last - self.revisions is filled in by make_page


    def _recursive_process_section(self, ident, content_pages):
        if (self.fcm.get_section_depth(ident) == self.chunk_depth or
            self.fcm.get_type(self.fcm.get_children(ident)[0]) != meta.TYPE_SECTION):
            content_pages.append(ident)
        else:
            self.make_node_page(ident)
            for ident in self.fcm.get_children(ident):
                self._recursive_process_section(ident, content_pages)


    def _process_links(self, page_string):
        page_parts = re.split('<a class="duref" href="(\d+)">', page_string)
        duref_index = 1
        while duref_index < len(page_parts):
            ident = page_parts[duref_index]
            if not self.fcm.is_valid(ident):
                print >> self.errorlog, "Reference to unknown DU", page_parts[duref_index], "whilst processing", ident
                page_parts[duref_index] = "<a class='duref' href='#'>!!!DU REFERENCE ERROR:%s!!!" % ident
            else:
                parent = self.fcm.get_parent(ident)
                if self.fcm.get_type(parent) == meta.TYPE_GROUP:
                    ident = parent
                href = self._make_href(ident)
                anchor_string = self._make_title(ident)
                if page_parts[duref_index + 1][:2] != "</":
                    anchor_string = ""
                page_parts[duref_index] = '%s<a class="duref" href="%s">%s' % (
                    "refer to " if anchor_string else "",
                    href,
                    anchor_string)
            duref_index += 2
        return "".join(page_parts)


    def _recursive_build_node(self, tb, ident, **other):
        node_type = self.fcm.get_type(ident)
        if  node_type == meta.TYPE_SECTION:
            section_attribs = {"sid": self._make_html_identifier(ident),
                               "title": self._make_title(ident)}
            tb.start("section", section_attribs)
            if self.fcm.get_type(self.fcm.get_children(ident)[0]) == meta.TYPE_SECTION:
                #this causes the sections to be layed out flat rather than in a hierarchy
                tb.end("section")
                for c in self.fcm.get_children(ident):
                    self._recursive_build_node(tb, c, **other)
            else:
                for c in self.fcm.get_children(ident):
                    self._recursive_build_node(tb, c, **other)
                tb.end("section")
        elif node_type == meta.TYPE_GROUP:
            group_attribs = {"id": self._make_html_identifier(ident),
                             "title": self.fcm.get_title(ident)}
            tb.start("group", group_attribs)
            for c in self.fcm.get_children(ident):
                self._recursive_build_node(tb, c, **other)
            tb.end("group")
        elif node_type == meta.TYPE_DUCONTAINER:
            du_container_attrib = {"id": self._make_html_identifier(ident),
                                   "title": self.fcm.get_title(ident)}
            overriding_tdu = self.fcm.get_overriding(ident)
            if overriding_tdu:
                du_container_attrib["overridden_by"] = self.fcm.get_parent(overriding_tdu)
            tb.start("du_container", du_container_attrib)
            jsarray = other['jsarray']
            jsarray.append([])
            for c in self.fcm.get_children(ident):
                self._process_du(tb, c, **other)
            if jsarray[-1] == []: del jsarray[-1]
            tb.end("du_container")


    def _process_du(self, tb, ident, **other):
        """Create DU in TreeBuilder TB.

        DU is the duid of the du to build.
        """
        filename = self.fcm.get_filename(ident)
        if filename: filename = g_paths.dus + filename
        du_attrib = {"title": self.fcm.get_title(ident),
                     "href": filename,
                     "id": self._make_html_identifier(ident),
                     "revdate": self.fcm.get_revdate(ident)}
        code = self.fcm.get_revision_code(ident)
        if code: du_attrib["revcode"] = code
        if self.fcm.is_tdu(ident): du_attrib["tdu"] = "tdu"
        tb.start("du", du_attrib)
        applies = self.fcm.applies(ident)
        if applies:
            tb.start("applies", {})
            tb.data(self.fcm.applies_string(applies))
            tb.end("applies")
            other['jsarray'][-1].append([ident, applies, self.fcm.applies_string(applies)[:100]])
        tb.end("du")
        other['revs'].extend(self.fcm.get_du_revs(ident))


    def make_page(self, sid, prevsid, nextsid):
        global g_paths
        filename = self._make_href(sid)
        print "Creating:", filename
        tb = et.TreeBuilder()
        revs = []
        jsarray = []
        page_attributes = {"title": self._make_title(sid, True),
                           "version": self.versionstring}
        if prevsid:
            page_attributes["prev"] = self._make_href(prevsid)
            page_attributes["prevtitle"] = self._make_title(prevsid)
        if nextsid:
            page_attributes["next"] = self._make_href(nextsid)
            page_attributes["nexttitle"] = self._make_title(nextsid)
        tb.start("page", page_attributes)
        self._recursive_build_node(tb, sid, jsarray=jsarray, revs=revs)
        tb.end("page")
        stylesheet_name = g_paths.xsldir + "page.xsl"
        tf = None
        if revs:
            tf = self._make_temporary_stylesheet(stylesheet_name, revs)
            stylesheet_name = tf.name
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", stylesheet_name, "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        if tf: os.unlink(tf.name)
        #create javascript variables for controlling folding
        page_string = page_string.replace(
            "<!--jsvariable-->",
            "var folding = " + str(jsarray) + ";")
        #replace xml links with xhtml links
        page_string = self._process_links(page_string)
        #insert link bar
        page_string = page_string.replace("<!--linkbar-->", self._build_linkbar(sid))
        #write the file
        of = open(g_paths.html_output + filename, "w")
        of.write(page_string)


    def _make_temporary_stylesheet(self, stylesheet_name, revs):
        stylesheet = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:import href="%s"/>
<xsl:template match="%s"><xsl:call-template name="revised_text"/></xsl:template>
</xsl:stylesheet>""" % (stylesheet_name, " | ".join([r[2:] for r in revs]))
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.write(stylesheet)
        tf.close()
        return tf


    def _recursive_add_index_section(self, ident, tb):
        if (self.fcm.get_section_depth(ident) < self.chunk_depth and
            self.fcm.get_type(self.fcm.get_children(ident)[0]) == meta.TYPE_SECTION):
            tb.start("section", {"title": self.fcm.get_title(ident),
                                 "ident": ".".join(self.fcm.get_pslcode(ident)),
                                 "href": self._make_href(ident)})
            for s in self.fcm.get_children(ident):
                self._recursive_add_index_section(s, tb)
            tb.end("section")
        else:
            tb.start("page", {"href": self._make_href(ident)})
            tb.data(self._make_title(ident))
            tb.end("page")


    def make_node_page(self, ident):
        global g_paths
        tb = et.TreeBuilder()
        if ident:
            index_attribs = {"title": self._make_title(ident, True),
                             "ident": ".".join(self.fcm.get_pslcode(ident)),
                             "version": self.versionstring}
            filename = self._make_href(ident)
        else: #contents page
            index_attribs =  {"title": "Contents",
                              "version": self.versionstring}
            filename = "index.html"
        tb.start("index", index_attribs)
        if not ident:#inject revisions list link into index.html
            tb.start("page", {"href": "revisions.html"})
            tb.data("Revision list")
            tb.end("page")
        for i in self.fcm.get_children(ident):
            self._recursive_add_index_section(i, tb)
        tb.end("index")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self._build_linkbar(ident))
        print "Creating", filename
        of = open(g_paths.html_output + filename, "w")
        of.write(page_string)


    def _build_linkbar(self, ident):
        title_crop = 30
        tb = et.TreeBuilder()
        tb.start("div", {"class": "linkbar"})
        tb.start("p", {})
        if ident: #contents page passes in empty list
            tb.start("a", {"title": "Contents",
                           "href": "index.html"})
            tb.data("Contents")
            tb.end("a")
            if ident == "REV":
                ident_list = []
            else:
                ident_list = self.fcm.get_ancestors(ident)
            for i in ident_list:
                tb.data(" >> ")
                title = self._make_title(i)
                tb.start("a", {"title": title,
                               "href": self._make_href(i)})
                tb.data(title[:title_crop])
                if len(title) > title_crop:
                    tb.data("...")
                tb.end("a")
        else:
            tb.data(u" ")
        tb.end("p")
        tb.start("div", {"class": "otherlinks"})
        tb.start("p", {})
        tb.data(u"| ")
        tb.start("a", {"href": "search.html"})
        tb.data("Search")
        tb.end("a")
        tb.end("p")
        tb.end("div")
        tb.end("div")
        return et.tostring(tb.close(), "utf-8")


    def write_fleet_js(self):
        global g_paths
        open(os.path.join(g_paths.js_output, "fleet.js"), "w").write(
            ("var fleet = { \n" +
             ",".join(["'%s':'%s'" % X for X in self.fcm.get_fleet()]) +
             "};\n"))


    def _recursive_add_revision_node(self, tb, ident):
        if self.fcm.get_type(ident) == meta.TYPE_DU:
            code = self.fcm.get_revision_code(ident)
            if code:
                code = code[-1:] # strip E from 2 letter codes
                revs = self.fcm.get_du_revs(ident)
                #only add (R) to revision list if there are some real revision paths in dumdata
                if code != "R" or revs:
                    tb.start("rev", {"code": code,
                                     "duid": ident,
                                     "href": self._make_href(self.fcm.get_parent(ident)),#href is for container
                                     "title": self.fcm.get_title(ident)})
                    tb.end("rev")
        elif (self.fcm.get_type(ident) == meta.TYPE_SECTION and
              self.fcm.get_type(self.fcm.get_children(ident)[0]) != meta.TYPE_SECTION):
            tb.start("section", {"title": self._make_title(ident, True)})
            for c in self.fcm.get_children(ident):
                self._recursive_add_revision_node(tb, c)
            tb.end("section")
        else:
            for c in self.fcm.get_children(ident):
                self._recursive_add_revision_node(tb, c)


    def make_revision_list(self):
        global g_paths
        print "Writing revision list"
        tb = et.TreeBuilder()
        tb.start("revisions", {"title": "Revision list",
                               "version": self.versionstring})
        self._recursive_add_revision_node(tb, None)
        tb.end("revisions")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "revisions.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self._build_linkbar("REV"))
        of = open(g_paths.html_output + "revisions.html", "w")
        of.write(page_string)


    def _make_href(self, ident):
        """Convert IDENT to an href.

        If the ident is of a section that references a page or node
        page, returns the relative filename (e.g. 'DSC.20.html").

        Otherwise returns a link with a hash part
        (e.g. 'GEN.html#duid00014071') which can be used in an <a> tag
        to jump to the section"""
        section = ident
        if self.fcm.get_type(ident) != meta.TYPE_SECTION:
            section = self.fcm.get_parent_section(ident)
        if self.fcm.get_section_depth(section) > self.chunk_depth:
            section = self.fcm.get_ancestors(section)[self.chunk_depth - 1]
        href = ".".join(self.fcm.get_pslcode(section)) + ".html"
        if ident != section:
            href += "#" + self._make_html_identifier(ident)
        return href


    def _make_html_identifier(self, ident):
        """Creates an identifier suitable for an html id attribute
        from IDENT"""
        node_type = self.fcm.get_type(ident)
        prefixes = {meta.TYPE_DU: "duid",
                    meta.TYPE_DUCONTAINER: "duid",
                    meta.TYPE_GROUP: "gid",
                    meta.TYPE_SECTION: "sid"}
        if node_type == meta.TYPE_SECTION:
            ident = ".".join(self.fcm.get_pslcode(ident))
        return prefixes[node_type] + ident


    def _make_title(self, ident, all_sections=False):
        sections = [X for X in self.fcm.get_ancestors(ident) + [ident]
                    if self.fcm.get_type(X) == meta.TYPE_SECTION]
        prefix = ".".join(self.fcm.get_pslcode(sections[-1]))
        if all_sections:
            titleparts = [self.fcm.get_title(X) for X in sections]
            return "[%s] %s" % (prefix, " : ".join(titleparts))
        else:
            return "%s: %s" % (prefix, self.fcm.get_title(ident))




if __name__ == "__main__":
    global g_paths
    import sys
    import meta
    if len(sys.argv) != 2:
        print "Usage: ", sys.argv[0], "start_file"
        sys.exit(1)
    g_paths.initialise(*sys.argv + ["."])
    fcm = meta.FCOMMeta(True)
    f = FCOMFactory(fcm)
    print f._make_href("00014071")
    print f._make_href("NG01223")
    print f._make_href(('GEN',))
    print f._make_href(('DSC','21','20'))



