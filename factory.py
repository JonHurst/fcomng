#!/usr/bin/python
# coding=utf-8

from globals import *

import xml.etree.cElementTree as et
import subprocess
import re
import tempfile

class FCOMFactory:

    def __init__(self, fcm):
        global g_paths
        self.fcm = fcm #instance of FCOMMeta
        versiondate = g_paths.control[-12:-4]
        self.versionstring = versiondate[:4] + "-" + versiondate[4:6] + "-" + versiondate[6:]
        self.pagelist = self.fcm.get_leaves(3)
        self.pageset = set(self.pagelist)
        self.hrefs = {}
        self.revisions = []
        self.duref_lookup = {}
        self.__build_duref_lookup__()


    def build_fcom(self):
        self.errorlog = open("build-error.log", "w")
        self.write_fleet_js()
        self.make_index()
        for c, sid in enumerate(self.pagelist):
            prevsid, nextsid = None, None
            if c > 0:
                prevsid = self.pagelist[c - 1]
            if c < len(self.pagelist) - 1:
                nextsid = self.pagelist[c + 1]
            self.make_page(c, sid ,prevsid, nextsid)
        self.make_revision_list() # this must be done last since make_page populates hrefs


    def __build_duref_lookup__(self):
        for sid in self.pagelist:
            sid_list = self.__build_sid_list__(sid)
            for s in sid_list:
                for du_list in self.fcm.get_dus(s):
                    duref = du_list[0].split(".")[0]
                    self.duref_lookup[duref] = (
                        self.__make_filename__(sid) + "#duid" + duref,
                        ".".join(s) + ": " + self.fcm.get_du_title(du_list[0]))


    def __build_sid_list__(self, sid):
        return [sid, ] + self.fcm.get_descendants(sid)



    def __start_page__(self, tb, sid, prevsid, nextsid):
        """Starts a page using TreeBuilder object TB.

        SID is the section ID of the page to start e.g. ('DSC', '20', '20').
        PREVSID is the section ID of the previous section in "book order"
        NEXTSID is the section ID of the next section in "book order"
        """
        page_attributes = {"title": self.__make_page_title__(sid),
                           "version": self.versionstring}
        if prevsid:
            page_attributes["prev"] = self.__make_filename__(prevsid)
            page_attributes["prevtitle"] = ".".join(prevsid) + ": " + self.fcm.get_title(prevsid)
        if nextsid:
            page_attributes["next"] = self.__make_filename__(nextsid)
            page_attributes["nexttitle"] = ".".join(nextsid) + ": " + self.fcm.get_title(nextsid)
        tb.start("page", page_attributes)


    def __process_du__(self, tb, du):
        """Create DU in TreeBuilder TB.

        DU is the duid of the du to build.
        """
        filename = self.fcm.get_du_filename(du)
        if filename: filename = g_paths.dus + filename
        du_attrib = {"title": self.fcm.get_du_title(du),
                     "href": filename,
                     "id": "duid" + du,
                     "revdate": self.fcm.get_du_revdate(du) }
        code = self.fcm.get_revision_code(du)
        revs = self.fcm.get_du_revs(du)
        if code:
            du_attrib["revcode"] = code
            #only add to revision list if there are some revision paths in dumdata
            if code[-1:] != "R" or revs: self.revisions.append(du)
        if self.fcm.is_tdu(du):
            du_attrib["tdu"] = "tdu"
        tb.start("du", du_attrib)
        applies = self.fcm.applies(du)
        if applies:
            tb.start("applies", {})
            tb.data(self.fcm.applies_string(applies))
            tb.end("applies")
        tb.end("du")


    def __build_javascript_folding_code__(self, section_list):
        """Returns a string that is a valid javascript variable definition to enable javascript folding.

        The string is of the form:
           var folding =
              [ [ [ duid, [msn, msn, ...], applies_string], ... ], ...];

        i.e it specifies an array of du_containers with each du_container being defined by an array of dus.
        """
        js_array = []
        for s in section_list:
            for ducontainer in self.fcm.get_dus(s):
                js_array.append([])
                for du in ducontainer:
                    applies = self.fcm.applies(du)
                    if applies:
                        js_array[-1].append([du, applies, self.fcm.applies_string(applies)[:100]])
                if js_array[-1] == []:
                    del js_array[-1]
        return "var folding = " + str(js_array) + ";"


    def __process_links(self, page_string, sid):
        page_parts = re.split('<a class="duref" href="(\d+)">', page_string)
        duref_index = 1
        while duref_index < len(page_parts):
            duinfo = self.duref_lookup.get(page_parts[duref_index])
            if not duinfo: #protect against bad links in source
                print >> self.errorlog, "Reference to unknown DU", page_parts[duref_index], "whilst processing", ".".join(sid)
                duinfo = ("", "!!!DU REFERENCE ERROR!!!")
            page_parts[duref_index] = ('<a class="duref" href="' +
                                       duinfo[0] +
                                       '">')
            if page_parts[duref_index + 1][:2] == "</":
                page_parts[duref_index] += duinfo[1]
            else:
                page_parts[duref_index] += duinfo[1].split()[0]
            duref_index += 2
        return "".join(page_parts)



    def make_page(self, c, sid, prevsid, nextsid):
        global g_paths
        filename = self.__make_filename__(sid)
        print "Creating:", filename
        tb = et.TreeBuilder()
        self.__start_page__(tb, sid, prevsid, nextsid)
        section_list = self.__build_sid_list__(sid)
        revs = []
        for s in section_list:
            #process each section required for the page
            section_attribs = {"sid": "sid" + ".".join(s),
                               "title": ".".join(s) + ": " + self.fcm.get_title(s)}
            tb.start("section", section_attribs)
            self.hrefs[self.fcm.get_npid(s)] = filename + "#" + section_attribs["sid"]
            last_groupid = None
            for dul in self.fcm.get_dus(s):
                #get_dus returns a list of the form [(duid, ...), (duid, ...), ...]
                #so dul is each (duid, ...) tuple, each tuple entry representing alternative
                #versions of the DU. Alternative versions are neccessarily of the same group if applicable.
                groupid = self.fcm.get_du_group(dul[0])
                if groupid != last_groupid:
                    if last_groupid:
                        tb.end("group")
                    if groupid:
                        group_attribs = {"id": "gid" + groupid,
                                         "title": self.fcm.get_group_title(groupid)}
                        tb.start("group", group_attribs)
                        self.hrefs[groupid] = filename + "#gid" + groupid
                    last_groupid = groupid
                containerid = dul[0].split(".")[0]
                tb.start("du_container", {"id": "duid" + containerid,
                                          "title": self.fcm.get_du_title(dul[0])})
                self.hrefs[containerid] = filename + "#duid" + containerid
                for du in dul:
                    self.__process_du__(tb, du)
                    self.hrefs[du] = filename + "#duid" + containerid
                    revs.extend(self.fcm.get_du_revs(du))
                tb.end("du_container")
            if last_groupid: #if last_groupid hasn't been set to None, we were in a group at the end of the section
                tb.end("group")
            tb.end("section")
        tb.end("page")
        stylesheet_name = g_paths.xsldir + "page.xsl"
        tf = None
        if revs:
            tf = self.__make_temporary_stylesheet(stylesheet_name, revs)
            stylesheet_name = tf.name
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", stylesheet_name, "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        if tf: os.unlink(tf.name)
        #create javascript variables for controlling folding
        page_string = page_string.replace("<!--jsvariable-->",
                                          self.__build_javascript_folding_code__(section_list))
        #replace xml links with xhtml links
        page_string = self.__process_links(page_string, sid)
        # #insert link bar
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(sid))
        of = open(g_paths.html_output + filename, "w")
        of.write(page_string)

    def __make_temporary_stylesheet(self, stylesheet_name, revs):
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



    def __make_page_title__(self, sid):
        titleparts = []
        for c in range(1, len(sid) + 1):
            titleparts.append(self.fcm.get_title(sid[:c]))
        return "[%s] %s" % (".".join(sid), " : ".join(titleparts))


    def __recursive_add_section__(self, ident, tb):
        if ident not in self.pageset:
            children = self.fcm.get_children(ident)
            self.__make_node_page__(ident, children)
            tb.start("section", {"title": self.fcm.get_title(ident),
                                 "ident": ".".join(ident),
                                 "href": self.__make_filename__(ident)})
            for s in children:
                self.__recursive_add_section__(s, tb)
            tb.end("section")
        else:
            tb.start("page", {"href": self.__make_filename__(ident)})
            tb.data(".".join(ident) + ": " + self.fcm.get_title(ident))
            tb.end("page")


    def __make_node_page__(self, ident, children):
        global g_paths
        tb = et.TreeBuilder()
        tb.start("index", {"title": self.__make_page_title__(ident),
                          "ident": ".".join(ident),
                           "version": self.versionstring})
        for i in children:
            self.__recursive_add_section__(i, tb)
        tb.end("index")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(ident))
        print "Creating node page", ident
        of = open(g_paths.html_output + self.__make_filename__(ident), "w")
        of.write(page_string)


    def make_index(self):
        global g_paths
        tb = et.TreeBuilder()
        tb.start("index", {"title": "Contents",
                           "version": self.versionstring})
        tb.start("page", {"href": "revisions.html"})
        tb.data("Revision list")
        tb.end("page")
        for s in self.fcm.get_leaves(1):
            self.__recursive_add_section__(s, tb)
        tb.end("index")

        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(()))
        of = open(g_paths.html_output + "index.html", "w")
        of.write(page_string)


    def __make_filename__(self, sid):
        retval = ""
        if sid:
            retval = ".".join(sid) + ".html"
        return retval


    def __build_linkbar__(self, sid):
        title_crop = 30
        tb = et.TreeBuilder()
        tb.start("div", {"class": "linkbar"})
        tb.start("p", {})
        if sid: #contents page passes in empty list
            tb.start("a", {"title": "Contents",
                           "href": "index.html"})
            tb.data("Contents")
            tb.end("a")
            for c in range(1, len(sid)):
                tb.data(" >> ")
                ident = sid[:c]
                title = ".".join(ident) + ": " + self.fcm.get_title(ident)
                tb.start("a", {"title": title,
                               "href": self.__make_filename__(ident)})
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



    def make_revision_list(self):
        global g_paths
        print "Writing revision list"
        #split dus into lists within the same section
        sectioned_dus = [[self.fcm.get_du_parent(self.revisions[0]), self.revisions[0]]]
        for duid in self.revisions[1:]:
            du_section = self.fcm.get_du_parent(duid)
            if du_section == sectioned_dus[-1][0]:
                sectioned_dus[-1].append(duid)
            else:
                sectioned_dus.append([du_section, duid])
        tb = et.TreeBuilder()
        tb.start("revisions", {"title": "Revision list",
                               "version": self.versionstring})
        for section in sectioned_dus:
            section_title = []
            for c in range(1, len(section[0])):
                section_title.append(self.fcm.get_title(section[0][:c]))
            section_title = " : ".join(section_title)
            tb.start("section", {"title": ".".join(section[0]) + " " + section_title})
            for duid in section[1:]:
                tb.start("rev", {"code": self.fcm.get_revision_code(duid)[-1:],
                                 "duid": duid,
                                 "href": self.hrefs[duid],
                                 "title": self.fcm.get_du_title(duid)})
                tb.end("rev")
            tb.end("section")
        tb.end("revisions")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "revisions.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(("REV",)))
        of = open(g_paths.html_output + "revisions.html", "w")
        of.write(page_string)
