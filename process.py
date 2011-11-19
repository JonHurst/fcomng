#!/usr/bin/python
# coding=utf-8

import xml.etree.ElementTree
et = xml.etree.ElementTree
import subprocess
import re
import sys
import os

class Paths:

    def initialise(self, scriptpath, startfile, outputdir):
        basedir = os.path.dirname(os.path.abspath(startfile))
        print basedir
        path_tree = et.parse(startfile)
        paths = {}
        for cp in path_tree.findall("components-path/component-path"):
            paths[cp.attrib["type"]] = cp.text
        self.control = os.path.join(basedir, path_tree.find("starter").text)
        self.global_meta = os.path.join(basedir, paths["product-metadata"])
        self.dus = os.path.join(basedir, paths["du-content"])
        self.mus = os.path.join(basedir, paths["du-metadata"])
        self.html_output = os.path.join(os.path.abspath(outputdir), "html/")
        self.js_output = os.path.join(os.path.abspath(outputdir), "scripts/")
        self.xsldir = os.path.join(os.path.dirname(os.path.abspath(scriptpath)), "xsl/")

g_paths = Paths()


class FCOMMeta:

    class Section:

        def __init__(self, title):
            self.title = title
            self.children = []
            self.du_list = []


        def add_child(self, sid):
            self.children.append(sid)


        def add_du(self, du_filename_tuple):
            self.du_list.append(du_filename_tuple)


    class Aircraft:

        def __init__(self, aat):
            self.aircraft = {}
            self.fleets = {}
            self.pseudofleets = {}
            for a in aat.findall("aircraft-item"):
                if a.attrib["acn"]:
                    self.aircraft[a.attrib["msn"]] = a.attrib["acn"]
                    if not self.pseudofleets.has_key(a.attrib["acn"][:-1] + "*"):
                        self.pseudofleets[a.attrib["acn"][:-1] + "*"] = set()
                    self.pseudofleets[a.attrib["acn"][:-1] + "*"].add(a.attrib["msn"])
                else:
                    self.aircraft[a.attrib["msn"]] = a.attrib["msn"]
                m = a.attrib["aircraft-model"]
                if not self.fleets.has_key(m):
                    self.fleets[m] = set()
                self.fleets[m].add(a.attrib["msn"])


        def applies_string(self, msnlist):
            msnset = set(msnlist)
            fleets = []
            for f in self.fleets.keys():
               if self.fleets[f] <= msnset:
                    fleets.append(f + " fleet")
                    msnset = msnset.difference(self.fleets[f])
            pseudofleets = []
            for p in self.pseudofleets.keys():
                if self.pseudofleets[p] <= msnset:
                    pseudofleets.append(p)
                    msnset = msnset.difference(self.pseudofleets[p])
            remaining = pseudofleets + [self.aircraft[X] for X in list(msnset)]
            remaining.sort()
            fleets.sort()
            return ", ".join(fleets + remaining)


        def msn_to_reg(self, msn):
            return self.aircraft[msn]


        def all(self):
            return self.aircraft


        def dump(self):
            for k in self.fleets.keys():
                print "\n", k, "fleet: "
                for a in self.fleets[k]:
                    if self.aircraft[a]:
                        print self.aircraft[a]
                    else:
                        print a


    class DU:

        def __init__(self,  data_filename, mu_filename, parent_sid, title, groupid):
            global g_paths
            self.data_filename = data_filename
            self.parent_sid = parent_sid
            self.title = title
            self.groupid = groupid
            #parse metadata file
            e = et.ElementTree(None, g_paths.mus + mu_filename)
            if data_filename:
                self.msns = self.__get_msns__(e)
            self.tdu = False
            if e.getroot().attrib["tdu"] == "true":
                self.tdu = True
            self.linked_du = e.getroot().attrib["linked-du-ident"]
            self.affected_by = None


        def __get_msns__(self, e):
            m = e.find("effect").find("aircraft-ranges").find("effact").find("aircraft-range")
            if not et.iselement(m):
                msns = None
            else:
                msns = []
                for msn in m.text.split(" "):
                    #supposition: a pair of numbers together indicates all aircraft with MSNs between
                    #[:4] and [4:]
                    if len(msn) == 8:
                        for rangemsn in range(int(msn[:4]), int(msn[4:]) + 1):
                            msns.append(str(rangemsn))
                    else:
                        msns.append(msn)
            return msns


        def set_msns(self, msnlist):
            self.msns = msnlist


    class RevisionRecord:

        def __init__(self, revclass, change, anchor):
            self.revclass = revclass
            self.change = change
            self.anchor = anchor


        def __str__(self):
            return "Class: %s Change: %s Anchor: %s" % (
                self.revclass,
                self.change,
                self.anchor)


    def __init__(self):
        global g_paths
        self.sections = {}
        self.dus = {}
        self.group_titles = {}
        self.top_level_sids = []
        self.revdict = {}
        print "Scanning metadata"
        self.control = et.ElementTree(None, g_paths.control)
        self.global_meta = et. ElementTree(None, g_paths.global_meta)
        self.__build_revdict__(self.global_meta.find("revisions"))
        self.aircraft = self.Aircraft(self.global_meta.find("aat"))
        for psl in self.control.getroot().findall("psl"):
            print "Scanning", psl.attrib["pslcode"]
            self.top_level_sids.append((psl.attrib["pslcode"],))
            self.__process_psl__(psl, ())


    def __process_psl__(self, elem, sec_id):
        i = sec_id + (elem.attrib["pslcode"],)
        self.sections[i] = []
        section = self.Section(elem.findtext("title"))
        self.sections[i] = section
        if self.sections.has_key(i[:-1]):
            self.sections[i[:-1]].add_child(i)
        for e in elem:
            if e.tag == "du-inv":
                self.__process_duinv__(e, i)
            elif e.tag == "group":
                self.__process_group__(e, i)
            elif e.tag == "psl":
                self.__process_psl__(e, i)


    def __process_duinv__(self, elem, sec_id, groupid=None):
        global g_paths
        duids = []
        msnlist = []
        for s in elem.findall("du-sol"):
            data_file = os.path.basename(s.find("sol-content-ref").attrib["href"])
            meta_file = os.path.basename(s.find("sol-mdata-ref").attrib["href"])
            title = elem.find("title").text
            #find duid - unfortunately only available in du file as root element code
            s = open(g_paths.dus + data_file).read(200)
            duid = s[s.find("code="):][6:22]
            self.dus[duid] = self.DU(data_file, meta_file, sec_id, title, groupid)
            msns = self.dus[duid].msns
            if msns:
                msnlist.extend(msns)
            duids.append(duid)
        #we may have to create a fake du if we have a set if dus that only cover part of the fleet
        if msnlist:
            nc = self.notcovered(msnlist)
            if nc:
                duid = duid.split(".")[0] + ".NA"
                self.dus[duid] = self.DU("", meta_file, sec_id, title, groupid)
                self.dus[duid].set_msns(nc)
                duids.append(duid)
        self.sections[sec_id].add_du(tuple(duids))


    def __process_group__(self, elem, sec_id):
        #note: groups don't nest, and they only contain du-inv sections
        groupid = elem.attrib["id"]
        self.group_titles[groupid] = elem.find("title").text
        for s in elem.findall("du-inv"):
            self.__process_duinv__(s, sec_id, groupid)


    def __build_revdict__(self, rev_elem):
        content_revisions = rev_elem.find("content-revisions")
        highlights = content_revisions.find("highlights")
        rev_marks = content_revisions.find("rev-marks")
        path_reo = re.compile(r"//([^\[]*)[^']*'([^']*)")
        for rev in rev_marks.findall("rev"):
            mo = path_reo.match(rev.attrib["path"])
            if not mo: print "regexp error"; continue
            self.revdict[mo.group(2)] = self.RevisionRecord(
                mo.group(1),
                rev.attrib["chg"],
                True if rev.attrib["anchor"] == "true" else False)



    def get_title(self, sid):
        return self.sections[sid].title


    def get_du_title(self, duid):
        return self.dus[duid].title


    def get_du_parent(self, duid):
        return self.dus[duid].parent_sid


    def get_du_group(self, duid):
        return self.dus[duid].groupid


    def get_du_filename(self, duid):
        return self.dus[duid].data_filename
    def get_group_title(self, groupid):
        return self.group_titles.get(groupid)


    def get_dus(self, sid):
        return self.sections[sid].du_list


    def get_children(self, sid):
        return self.sections[sid].children


    def get_all_sids(self):
        retval = []
        for s in self.top_level_sids:
            retval.append(s)
            retval += self.get_descendants(s)
        return retval


    def get_descendants(self, sid):
        retval = []
        for c in self.get_children(sid):
            retval.append(c)
            retval += self.get_descendants(c)
        return retval


    def get_leaves(self, prune=3):
        retval = []
        for s in self.get_all_sids():
            if len(s) > prune: continue
            if len(s) == prune or not self.get_children(s):
                retval.append(s)
        return retval


    def get_fleet(self):
        return [(X, self.aircraft.aircraft[X]) for X in self.aircraft.aircraft]


    def affected(self, msn, du_filename):
        ac_list = self.dus[du_filename].msns
        if not ac_list or msn in ac_list:
            return True
        return False


    def applies(self, duid):
        return self.dus[duid].msns


    def notcovered(self, msnlist):
        return list(set(self.aircraft.all()) - set(msnlist))


    def applies_string(self, msnlist):
        return self.aircraft.applies_string(msnlist)



    def is_tdu(self, duid):
        return self.dus[duid].tdu


    def dump(self):
        print "Sections:\n==========\n"
        for s in self.get_all_sids():
            section = self.sections[s]
            indent = " " * ((len(s) - 1) * 4)
            print indent, ".".join(s), ": ", section.title
            for du in self.get_dus(s):
                print indent, " ", du
        print "DUs:\n============\n"
        for du in sorted(self.dus):
            print du, self.dus[du].parent_sid, self.dus[du].msns, self.dus[du].tdu
        print "\n\nLeaves:\n=======\n"
        for l in self.get_leaves():
            print ".".join(l), ": ", self.get_title(l)
        print "\n\nAircraft:\n=========\n"
        self.aircraft.dump()
        print "\n\nAircraft list test\n"
        print self.affected("4556", "00000284.0003001")
        print self.applies("00000284.0003001")
        print self.applies("00000879.0004001")


class FCOMFactory:

    def __init__(self, fcm):
        global g_paths
        self.fcm = fcm #instance of FCOMMeta
        versiondate = g_paths.control[-12:-4]
        self.versionstring = versiondate[:4] + "-" + versiondate[4:6] + "-" + versiondate[6:]
        self.pagelist = self.fcm.get_leaves(3)
        self.pageset = set(self.pagelist)
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
                     "id": du}
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
        for s in section_list:
            #process each section required for the page
            tb.start("section", {"sid": ".".join(s),
                                 "title": self.fcm.get_title(s)})
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
                        tb.start("group", {"id": groupid,
                                           "title": self.fcm.get_group_title(groupid)})
                    last_groupid = groupid
                tb.start("du_container", {"id": dul[0].split(".")[0],
                                          "title": self.fcm.get_du_title(dul[0])})
                for du in dul:
                    self.__process_du__(tb, du)
                tb.end("du_container")
            if last_groupid: #if last_groupid hasn't been set to None, we were in a group at the end of the section
                tb.end("group")
            tb.end("section")
        tb.end("page")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + "page.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        #create javascript variables for controlling folding
        page_string = page_string.replace("<!--jsvariable-->",
                                          self.__build_javascript_folding_code__(section_list))
        #replace xml links with xhtml links
        page_string = self.__process_links(page_string, sid)
        # #insert link bar
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(sid))
        of = open(g_paths.html_output + filename, "w")
        of.write(page_string)


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



def main():
    global g_paths
    if len(sys.argv) != 3:
        print "Usage: ", sys.argv[0], "start_file output_dir"
        sys.exit(1)
    g_paths.initialise(*sys.argv)
    fcm = FCOMMeta()
    ff = FCOMFactory(fcm)
    ff.build_fcom()


if __name__ == "__main__":
    main()


