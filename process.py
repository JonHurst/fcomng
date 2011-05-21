#!/usr/bin/python
# coding=utf-8

import html_templates
import xml.etree.ElementTree
et = xml.etree.ElementTree
import subprocess

control_file = "fcom/DATA/XML_N_FCOM_EZY_TF_N_EU_CA_20110407.xml"
msn = "2412"
output_dir = "html/"
data_dir= "fcom/DATA/"
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


        def applies(self, msnlist):
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


        def dump(self):
            for k in self.fleets.keys():
                print "\n", k, "fleet: "
                for a in self.fleets[k]:
                    if self.aircraft[a]:
                        print self.aircraft[a]
                    else:
                        print a


    class DUMetaQuery:

        def __init__(self, fnd):
            self.du_filename = ""
            self.msns = []
            self.filename_dict = fnd
            self.tdu = False


        def get_ac_list(self, filename):
            if filename != self.du_filename:
                self.scan_dumeta(filename)
            return self.msns

        def is_tdu(self, filename):
            if filename != self.du_filename:
                self.scan_dumeta(filename)
            return self.tdu


        def scan_dumeta(self, filename):
            e = et.ElementTree(None, data_dir + self.filename_dict[filename])
            self.tdu = False
            if e.getroot().attrib["tdu"] == "true":
                self.tdu = True
            m = e.find("effect").find("aircraft-ranges").find("effact").find("aircraft-range")
            if not et.iselement(m):
                self.msns = None
            else:
                self.msns = []
                for msn in m.text.split(" "):
                    while len(msn) != 4:
                        self.msns.append(msn[:4])
                        msn = msn[4:]
                    self.msns.append(msn)


    def __init__(self, control_file):
        self.sections = {}
        self.du_titles = {}
        self.du_meta_filenames = {}
        self.top_level_sids = []
        self.control = et.ElementTree(None, control_file)
        self.global_meta = et. ElementTree(None, control_file.replace(".xml", "_mdata.xml"))
        self.aircraft = self.Aircraft(self.global_meta.find("aat"))
        self.du_metaquery = self.DUMetaQuery(self.du_meta_filenames)
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
                self.__process_duinv__(e, section)
            elif e.tag == "group":
                self.__process_group__(e, section)
            elif e.tag == "psl":
                self.__process_psl__(e, i)


    def __process_duinv__(self, elem, section):
        retval = []
        data_files = []
        for s in elem.findall("du-sol"):
            data_file = s.find("sol-content-ref").attrib["href"]
            self.du_meta_filenames[data_file] = s.find("sol-mdata-ref").attrib["href"]
            data_files.append(data_file)
            self.du_titles[data_file] = elem.find("title").text
        section.add_du(tuple(data_files))


    def __process_group__(self, elem, section):
        #note: groups don't nest, and they only contain du-inv sections
        for s in elem.findall("du-inv"):
            self.__process_duinv__(s, section)


    def get_title(self, sid):
        return self.sections[sid].title


    def get_du_title(self, du_filename):
        return self.du_titles[du_filename]


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


    def affected(self, msn, du_filename):
        ac_list = self.du_metaquery.get_ac_list(du_filename)
        if not ac_list or msn in ac_list:
            return True
        return False


    def applies(self, du_filename):
        ac_list = self.du_metaquery.get_ac_list(du_filename)
        if not ac_list:
            return "Whole fleet"
        else:
            return self.aircraft.applies(ac_list)


    def is_tdu(self, du_filename):
        return self.du_metaquery.is_tdu(du_filename)


    def dump(self):
        print "Sections:\n==========\n"
        for s in self.get_all_sids():
            section = self.sections[s]
            indent = " " * ((len(s) - 1) * 4)
            print indent, ".".join(s), ": ", section.title
            for du in self.get_dus(s):
                print indent, " ", du
        print "\n\nLeaves:\n=======\n"
        for l in self.get_leaves():
            print ".".join(l), ": ", self.get_title(l)
        print "\n\nMeta:\n=====\n"
        du_keys = self.du_meta_filenames.keys()
        du_keys.sort()
        for k in du_keys:
            print k, self.du_meta_filenames[k]
        print "\n\nAircraft:\n=========\n"
        self.aircraft.dump()
        print "\n\nAircraft list test\n"
        print self.affected("4556", "./DU/00000284.0001001.xml")
        print self.applies("./DU/00000284.0001001.xml")
        print self.applies("./DU/00000879.0002001.xml")
        print "\n\nDU titles:\n==========\n"
        du_titles_keys = self.du_titles.keys()
        du_titles_keys.sort()
        for k in du_titles_keys:
            print k, self.du_titles[k]


class FCOMFactory:

    def __init__(self, fcm):
        self.fcm = fcm #instance of FCOMMeta


    def build_fcom(self, msn):
        self.pagelist = self.fcm.get_leaves(3)
        self.make_index(self.pagelist)
        for c, sid in enumerate(self.pagelist):
            prevsid, nextsid = None, None
            if c > 0:
                prevsid = self.pagelist[c - 1]
            if c < len(self.pagelist) - 1:
                nextsid = self.pagelist[c + 1]
            self.make_page(c, sid ,prevsid, nextsid, msn)


    def __build_sid_list__(self, sid):
        return [sid, ] + self.fcm.get_descendants(sid)


    def make_page(self, c, sid, prevsid, nextsid, msn):
        filename = self.__make_filename__(sid)
        print "Creating:", filename
        tb = et.TreeBuilder()
        page_attributes = {"title": "[" + ".".join(sid) + "] " +self.fcm.get_title(sid[:1]) + ": " + self.fcm.get_title(sid[:2]),
                           "acft": self.fcm.aircraft.msn_to_reg(msn)}
        if len(sid) > 2: page_attributes["subtitle"] = self.fcm.get_title(sid[:3])
        if prevsid: page_attributes["prev"] = ".".join(prevsid) + ".html"
        if nextsid: page_attributes["next"] = ".".join(nextsid) + ".html"
        tb.start("page", page_attributes)
        for s in self.__build_sid_list__(sid):
            tb.start("section", {"sid": ".".join(s),
                                 "title": self.fcm.get_title(s)})
            for dul in self.fcm.get_dus(s):
                main_du = 0
                while not self.fcm.affected(msn, dul[main_du]):
                    main_du += 1
                    if main_du == len(dul): break
                if main_du == len(dul):
                    du_attrib = {"href": "",
                                 "title": self.fcm.get_du_title(dul[0])}
                    if self.fcm.is_tdu(dul[0]):
                        du_attrib["tdu"] = "tdu"
                    tb.start("du", du_attrib)
                else:
                    du_attrib = {"href": data_dir + dul[main_du],
                                 "title": self.fcm.get_du_title(dul[main_du])}
                    if self.fcm.is_tdu(dul[main_du]):
                        du_attrib["tdu"] = "tdu"
                    tb.start("du", du_attrib)
                    if self.fcm.applies(dul[main_du]) != "Whole fleet":
                        tb.start("applies", {})
                        tb.data(self.fcm.applies(dul[main_du]))
                        tb.end("applies")
                for adu in (dul[:main_du] + dul[main_du+1:]):
                    tb.start("adu", {"href": data_dir + adu,
                                     "title": self.fcm.get_du_title(adu)})
                    tb.start("applies", {})
                    tb.data(self.fcm.applies(adu))
                    tb.end("applies")
                    tb.end("adu")
                tb.end("du")
            tb.end("section")
        tb.end("page")
        page = et.tostring(tb.close(), "utf-8")
        of = open(output_dir + filename, "w")
        of.write(subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "page.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(page)[0])


    def make_index(self, pagelist):
        tb = et.TreeBuilder()
        tb.start("index", {})
        tb.start("book", {"title": self.fcm.get_title(pagelist[0][:1]),
                          "id": pagelist[0][0]})
        prev_section = pagelist[0][:1]
        title_level = 3
        for p in pagelist:
            if p[:1] != prev_section[:1]:
                tb.end("book")
                tb.start("book", {"title": self.fcm.get_title(p[:1]),
                                  "id": p[0]})
                title_level = 3
            if len(p) > 2 and p[:2] != prev_section[:2]:
                tb.start("h1", {})
                tb.data(self.fcm.get_title(p[:2]))
                tb.end("h1")
            if len(p) == 2 and (title_level == 2 or len(prev_section) == 3):
                tb.start("h1", {})
                tb.data(self.fcm.get_title(p))
                tb.end("h1")
                title_level = 2
            tb.start("a", {"href": self.__make_filename__(p)})
            tb.data(".".join(p) + ": " + self.fcm.get_title(p))
            tb.end("a")
            prev_section = p
        tb.end("book")
        tb.end("index")
        page = et.tostring(tb.close(), "utf-8")
        of = open(output_dir + "index.html", "w")
        of.write(subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "index.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(page)[0])


    def __make_filename__(self, sid):
        retval = ""
        if sid:
            retval = ".".join(sid) + ".html"
        return retval


def main():
    fcm = FCOMMeta(control_file)
    ff = FCOMFactory(fcm)
    ff.build_fcom(msn)


main()


