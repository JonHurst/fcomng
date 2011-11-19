#!/usr/bin/python
# coding=utf-8

import xml.etree.ElementTree
et = xml.etree.ElementTree
import subprocess
import re

control_file = "fcom/DATA/XML_N_FCOM_EZY_TF_N_EU_CA_20111007.xml"
output_dir = "html/"
data_dir= "fcom/DATA/"
fleet_script_file = "scripts/fleet.js"
xsl_dir = "xsl/"

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

        def __init__(self,  mu_filename, parent_sid, title, groupid):
            self.parent_sid = parent_sid
            self.title = title
            self.groupid = groupid
            #parse metadata file
            e = et.ElementTree(None, data_dir + mu_filename)
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


    def __init__(self, control_file):
        self.sections = {}
        self.dus = {}
        self.group_titles = {}
        self.top_level_sids = []
        self.revdict = {}
        print "Scanning metadata"
        self.control = et.ElementTree(None, control_file)
        self.global_meta = et. ElementTree(None, control_file.replace(".xml", "_mdata.xml"))
        self.__build_revdict__(self.global_meta.find("revisions"))
        self.aircraft = self.Aircraft(self.global_meta.find("aat"))
        for psl in self.control.getroot().findall("psl"):
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
        data_files = []
        for s in elem.findall("du-sol"):
            data_file = s.find("sol-content-ref").attrib["href"]
            meta_file = s.find("sol-mdata-ref").attrib["href"]
            title = elem.find("title").text
            self.dus[data_file] = self.DU(meta_file, sec_id, title, groupid)
            data_files.append(data_file)
        self.sections[sec_id].add_du(tuple(data_files))


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


    def get_du_title(self, du_filename):
        return self.dus[du_filename].title


    def get_du_parent(self, du_filename):
        return self.dus[du_filename].parent_sid


    def get_du_group(self, du_filename):
        return self.dus[du_filename].groupid


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


    def applies(self, du_filename):
        return self.dus[du_filename].msns


    def notcovered(self, msnlist):
        return list(set(self.aircraft.all()) - set(msnlist))


    def applies_string(self, msnlist):
        return self.aircraft.applies_string(msnlist)



    def is_tdu(self, du_filename):
        return self.dus[du_filename].tdu


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
        print self.affected("4556", "./DU/00000284.0003001.xml")
        print self.applies("./DU/00000284.0003001.xml")
        print self.applies("./DU/00000879.0004001.xml")


class FCOMFactory:

    def __init__(self, fcm, version):
        self.fcm = fcm #instance of FCOMMeta
        self.versionstring = version
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
                    duref = self.__du_to_duref__(du_list[0])[0]
                    self.duref_lookup[duref] = (
                        self.__make_filename__(sid) + "#duid" + duref,
                        ".".join(s) + ": " + self.fcm.get_du_title(du_list[0]))


    def __du_to_duref__(self, du):
        #this is dependent on the intrinsic link between du filenames and durefs
        # - it may be brittle
        return du[5:].split(".")[:-1]


    def __build_sid_list__(self, sid):
        return [sid, ] + self.fcm.get_descendants(sid)


    def make_page(self, c, sid, prevsid, nextsid):
        filename = self.__make_filename__(sid)
        print "Creating:", filename
        tb = et.TreeBuilder()
        page_attributes = {"title": self.__make_page_title__(sid),
                           "version": self.versionstring}
        if prevsid:
            page_attributes["prev"] = self.__make_filename__(prevsid)
            page_attributes["prevtitle"] = ".".join(prevsid) + ": " + self.fcm.get_title(prevsid)
        if nextsid:
            page_attributes["next"] = self.__make_filename__(nextsid)
            page_attributes["nexttitle"] = ".".join(nextsid) + ": " + self.fcm.get_title(nextsid)
        tb.start("page", page_attributes)
        javascript_list = []
        for s in self.__build_sid_list__(sid):
            #process each section required for the page
            tb.start("section", {"sid": ".".join(s),
                                 "title": self.fcm.get_title(s)})
            last_groupid = None
            for dul in self.fcm.get_dus(s):
                #get_dus returns a list of the form [(du_filename, ...), (du_filename, ...), ...]
                #so dul is each (du_filename, ...) tuple, each tuple entry representing alternative
                #versions of the DU. Alternative versions are neccessarily of the same group if applicable.
                msnlist = []
                groupid = self.fcm.get_du_group(dul[0])
                if groupid != last_groupid:
                    if last_groupid:
                        tb.end("group")
                    if groupid:
                        tb.start("group", {"id": groupid,
                                           "title": self.fcm.get_group_title(groupid)})
                    last_groupid = groupid
                tb.start("du_container", {"id": self.__du_to_duref__(dul[0])[0],
                                          "title": self.fcm.get_du_title(dul[0])})
                for c, du in enumerate(dul):
                    du_attrib = {"href": data_dir + du,
                                 "title": self.fcm.get_du_title(du),
                                 "id": ".".join(self.__du_to_duref__(du))}
                    if self.fcm.is_tdu(du):
                        du_attrib["tdu"] = "tdu"
                    tb.start("du", du_attrib)
                    applies = self.fcm.applies(du)
                    if applies:
                        tb.start("applies", {})
                        applies_string = self.fcm.applies_string(applies)
                        msnlist.append((du_attrib["id"], applies, applies_string[:100]))
                        tb.data(applies_string)
                        tb.end("applies")
                    tb.end("du")
                if msnlist:
                    javascript_list.append(msnlist)
                    # if dul does not cover the entire fleet, we need to add a fake extra du
                    msns = []
                    for msnentry in msnlist:
                        msns.extend(msnentry[1])
                    nc = self.fcm.notcovered(msns)
                    if nc:
                        du_attrib = {"href": "",
                                     "title": self.fcm.get_du_title(dul[0]),
                                     "id": self.__du_to_duref__(dul[0])[0] + ".na"}
                        if self.fcm.is_tdu(du):
                            du_attrib["tdu"] = "tdu"
                        tb.start("du", du_attrib)
                        tb.start("applies", {})
                        applies_string = self.fcm.applies_string(nc)
                        msnlist.append((du_attrib["id"], nc, applies_string[:100]))
                        tb.data(applies_string)
                        tb.end("applies")
                        tb.end("du")
                tb.end("du_container")
            if last_groupid: #if last_groupid hasn't been set to None, we were in a group at the end of the section
                tb.end("group")
            tb.end("section")
        tb.end("page")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "page.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        #create javascript variables for controlling folding
        javascript_string = ""
        for folding_section in javascript_list:
            javascript_string += "["
            for dusection in folding_section:
                javascript_string += "['%s',%s,'%s']," % dusection
            javascript_string = javascript_string[:-1] + "],"
        javascript_string = javascript_string[:-1] + "];\n"
        javascript_string = "var folding = [" + javascript_string
        page_string = page_string.replace("<!--jsvariable-->", javascript_string)
        #replace xml links with xhtml links
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
        page_string = "".join(page_parts)
        #insert link bar
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(sid))
        of = open(output_dir + filename, "w")
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
        tb = et.TreeBuilder()
        tb.start("index", {"title": self.__make_page_title__(ident),
                          "ident": ".".join(ident),
                           "version": self.versionstring})
        for i in children:
            self.__recursive_add_section__(i, tb)
        tb.end("index")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(ident))
        print "Creating node page", ident
        of = open(output_dir + self.__make_filename__(ident), "w")
        of.write(page_string)


    def make_index(self):
        tb = et.TreeBuilder()
        tb.start("index", {"title": "Contents",
                           "version": self.versionstring})
        for s in self.fcm.get_leaves(1):
            self.__recursive_add_section__(s, tb)
        tb.end("index")
        page_string= subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(et.tostring(tb.close(), "utf-8"))[0]
        page_string = page_string.replace("<!--linkbar-->", self.__build_linkbar__(()))
        of = open(output_dir + "index.html", "w")
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
        open(fleet_script_file, "w").write(
            ("var fleet = { \n" +
             ",".join(["'%s':'%s'" % X for X in self.fcm.get_fleet()]) +
             "};\n"))



def main():
    fcm = FCOMMeta(control_file)
    ff = FCOMFactory(fcm, "October 2011")
    ff.build_fcom()


if __name__ == "__main__":
    main()


