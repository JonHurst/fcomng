#!/usr/bin/python

import html_templates
import xml.etree.ElementTree
et = xml.etree.ElementTree
import subprocess

control_file = "fcom/DATA/XML_N_FCOM_EZY_TF_N_EU_CA_20110407.xml"
output_dir = "html/"
data_dir= "fcom/DATA/"
xsl_dir = "xsl/"

class ProcessList:

    def __init__(self, rootelement):
        self.__dict__ = {}
        for psl in rootelement.findall("psl"):
            # if psl.attrib["pslcode"] in ("FCB", "GEN"):
            self.__process_psl__(psl, ())
        self.orderedkeys = self.__dict__.keys()
        self.orderedkeys.sort()


    def __process_psl__(self, elem, sec_id):
        i = sec_id + (elem.attrib["pslcode"],)
        self.__dict__[i] = [[], ]
        pl = [elem.findtext("title"),]
        for e in elem:
            if e.tag == "du-inv":
                pl.append(self.__process_duinv__(e))
            elif e.tag == "group":
                pl += self.__process_group__(e)
            elif e.tag == "psl":
                self.__process_psl__(e, i)
        self.__dict__[i].append(pl)
        #add this psl to parent's list of children
        if self.__dict__.has_key(i[:-1]):
            self.__dict__[i[:-1]][0].append(i)


    def __process_duinv__(self, elem):
        retval = []
        for s in elem.findall("du-sol"):
            retval.append((s.findtext("title"),
                           s.find("sol-content-ref").attrib["href"],
                           s.find("sol-mdata-ref").attrib["href"]))
        return tuple(retval)


    def __process_group__(self, elem):
        #note: groups don't nest, and they only contain du-inv sections
        pl = []
        for s in elem.findall("du-inv"):
            pl.append(self.__process_duinv__(s))
        return tuple(pl)


    def level_list(self, level):
        retval = []
        for k in self.orderedkeys:
            if len(k) == level or (
                len(k) < level and len(self.__dict__[k][0]) == 0):
                retval.append(k)
        return retval


    def get_title(self, sid):
        return self.__dict__[sid][1][0]


    def get_dus(self, sid):
        retval = []
        sidlist = [sid,] + self.__offspring__(sid)
        for s in sidlist:
            retval += [X[0][1] for X in self.__dict__[s][1][1:]]
        return retval


    def __offspring__(self, sid):
        offspring = []
        for o in self.__dict__[sid][0]:
            offspring.append(o)
            offspring += self.__offspring__(o)
        return offspring


    def dump(self):
        keys = self.__dict__.keys()
        keys.sort()
        for k in keys:
            print k
            for p in self.__dict__[k]:
                print "   ", p


    def get_sids(self):
        return self.orderedkeys[:]


    def get_children(self, sid):
        return self.__dict__[sid][0][:]


class PageFactory:

    def __init__(self, pl):
        self.pl = pl


    def build_fcom(self):
        self.pagelist = self.pl.level_list(3)
        self.make_index(self.pl)
        for c, sid in enumerate(self.pagelist):
            self.make_page(c, sid)


    def make_page(self, c, sid):
        filename = self.__make_filename__(sid)
        print "Creating:", filename
        title = self.pl.get_title(sid)
        if len(sid) > 1:
            title = self.pl.get_title(sid[:-1])
        next = sid
        if (c + 1) < len(self.pagelist):
            next = self.pagelist[c + 1]
        page = html_templates.titleblock % {"sid": ".".join(sid),
                                            "title": title,
                                            "subtitle": self.pl.get_title(sid),
                                            "next": self.__make_filename__(next)}
        sidfrag = ""
        for du in self.pl.get_dus(sid):
            sidfrag += "<p class='du'>" + du + "</p>"
            sidfrag += self.__create_fragment__(du)
        if sidfrag:
            page += '<div class="sidfrag">' + sidfrag + "</div>"
        page += html_templates.footerblock % {"next": self.__make_filename__(next)}
        of = open(output_dir + filename, "w")
        of.write(html_templates.page % {"title": ".".join(sid) + " " + self.pl.get_title(sid),
                                        "fragments": page})


    def make_index(self, pl):
        sid_list = pl.get_sids()
        page = "<div class='index'>"
        for s in sid_list:
            if len(s) == 1:
                page += "<h1>" + pl.get_title(s) + "</h1>"
                if not pl.get_children(s):
                    page += ('<p><a href="' +
                             self.__make_filename__(s) +
                             '">' + pl.get_title(s) +
                             '</a></p>')
            elif len(s) == 2 and pl.get_children(s):
                page += "<h2>" + pl.get_title(s) + "</h2>"
            elif len(s)<=3:
                page += ('<p><a href="' +
                         self.__make_filename__(s) +
                         '">' + pl.get_title(s) +
                         '</a></p>')
        page += "</div>"
        of = open(output_dir + "index.html", "w")
        of.write(html_templates.page % {"title": "Index",
                                        "fragments": page})



    def __create_fragment__(self, filename):
        return subprocess.Popen(["xsltproc", "--nonet", "--novalid", xsl_dir + "fragment.xsl", data_dir + filename],
                                stdout=subprocess.PIPE).communicate()[0].replace('xmlns="http://www.w3.org/1999/xhtml" ', "", 1)


    def __make_filename__(self, sid):
        retval = ""
        if sid:
            retval = ".".join(sid) + ".html"
        return retval


def main():
    t = et.ElementTree(None, control_file)
    pl = ProcessList(t.getroot())
    pf = PageFactory(pl)
    pf.build_fcom()


main()


