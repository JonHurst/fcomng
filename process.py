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


        def add_du(self, du_filename):
            self.du_list.append(du_filename)

    class Aircraft:

        def __init__(self, aat):
            self.aircraft = {}
            self.fleets = {}
            for a in aat.findall("aircraft-item"):
                self.aircraft[a.attrib["msn"]] = a.attrib["acn"]
                m = a.attrib["aircraft-model"]
                if not self.fleets.has_key(m):
                    self.fleets[m] = set()
                self.fleets[m].add(a.attrib["msn"])


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


        def get_ac_list(self, filename):
            if filename != self.du_filename:
                self.scan_dumeta(filename)
            return self.msns


        def scan_dumeta(self, filename):
            e = et.ElementTree(None, data_dir + self.filename_dict[filename])
            m = (e.find("effect").
                 find("aircraft-ranges").
                 find("effact").
                 find("aircraft-range").
                 text.split(" "))
            self.msns = []
            for msn in m:
                while len(msn) != 4:
                    self.msns.append(msn[:4])
                    msn = msn[4:]
                self.msns.append(msn)


    def __init__(self, control_file):
        self.sections = {}
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
        section.add_du(tuple(data_files))


    def __process_group__(self, elem, section):
        #note: groups don't nest, and they only contain du-inv sections
        for s in elem.findall("du-inv"):
            self.__process_duinv__(s, section)


    def get_title(self, sid):
        return self.sections[sid].title


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
        if msn in ac_list:
            return True
        return False


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
        root_element = et.Element("page", {"title": self.fcm.get_title(sid[:1])})
        if prevsid: root_element.set("prev", ".".join(prevsid) + ".html")
        if nextsid: root_element.set("next", ".".join(nextsid) + ".html")
        if len(sid) > 1: root_element.set("subtitle", self.fcm.get_title(sid[:2]))
        for s in self.__build_sid_list__(sid):
            current = et.SubElement(root_element, "section", {"sid": ".".join(s),
                                                              "title": self.fcm.get_title(s)})
            for du in self.fcm.get_dus(s):
                if len(du) == 1:
                    et.SubElement(current, "filename", {"href": data_dir + du[0],
                                                        "type": "main"})
                else:
                    for c, f in enumerate(du):
                        if self.fcm.affected(msn, f):
                            break
                    et.SubElement(current, "filename", {"href": data_dir + du[c],
                                                        "type": "main"})
                    alternates = du[:c] + du[c+1:]
                    for a in alternates:
                        et.SubElement(current, "filename", {"href": data_dir + a,
                                                            "type": "alt"})
        page = et.tostring(root_element, "utf-8")
        of = open(output_dir + filename, "w")
        of.write(subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "page.xsl", "-"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(page)[0])
        return


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


