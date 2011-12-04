#!/usr/bin/python
# coding=utf-8

import sys
import subprocess
import xml.etree.cElementTree as et
import re
import os
import difflib
import meta
import factory
from globals import g_paths
import glob


hurst_xsl = 'autotest_hurst.xsl'
lpcbrowser_xsl = 'autotest_lpcbrowser.xsl'
chunk_depth = 3
lpcbrowser_data_path = 'lpc_browser_xhtml/'


def _recursive_process_nodes(m, f, ident):
    if m.get_type(ident) == meta.TYPE_SECTION:
        for c in m.get_children(ident):
            _recursive_process_nodes(m, f, c,)
    elif m.get_type(ident) == meta.TYPE_GROUP:
        filelist = []
        for duc in m.get_children(ident):
            for c in m.get_children(duc):
                href = f._make_href(c)
                if href[-2:] == "NA": continue
                filelist.append(href)
        compare(filelist, ident + ".xhtml", m.get_title(ident))
    elif m.get_type(ident) == meta.TYPE_DUCONTAINER:
        for c in m.get_children(ident):
            href = f._make_href(c)
            if href[-2:] == "NA": continue
            compare([f._make_href(c)], c + ".xhtml")


def compare(hurst_list, lpcbrowser_file, grouptitle=""):
    hurst_text = transform_hurst_list(hurst_list, grouptitle)
    lpc_text = transform_lpcbrowser_file(lpcbrowser_file)
    if hurst_text != lpc_text:
        print hurst_list, lpcbrowser_file
        print "=" * 30
        c = index_of_first_difference(hurst_text, lpc_text)
        print hurst_text[c:][:100].encode("utf8")
        print "-" * 30
        print lpc_text[c:][:100].encode("utf8")
        print


def transform_hurst_list(hurst_list, grouptitle):
    source_filename = g_paths.html_output + hurst_list[0].split("#")[0]
    idents = [X.split("#")[1] for X in hurst_list]
    xml_string = subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + hurst_xsl, '-'],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(file(source_filename).read())[0]
    hurst_xml = et.fromstring(xml_string)
    retval = unicode(grouptitle)
    for du in hurst_xml.findall("{http://www.hursts.eclipse.co.uk/dul}du"):
        ident = du.attrib["id"]
        if ident in idents:
            hurst_text = du.text
            if type(du.text) != unicode:
                hurst_text = unicode(du.text, "utf-8")
            retval += hurst_text

    return re.sub(u"[\=\s \u200B:\u2222\u2022]+", "", retval).upper()


def transform_lpcbrowser_file(lpcbrowser_file):
    filename = lpcbrowser_data_path + lpcbrowser_file
    if not os.path.exists(filename): return "^"
    lpc_text = unicode(subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + lpcbrowser_xsl, '-'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                        ).communicate(file(lpcbrowser_file).read())[0], 'utf-8')
    lpc_text = re.sub(u"[\=\s :\u200B\u2222\u2022]+", "", lpc_text).upper()
    return lpc_text



def index_of_first_difference(hurst_text, lpc_text):
    pos = 0
    for c, char in enumerate(hurst_text):
        pos = c
        if (c == len(lpc_text) or
            lpc_text[c] != char): break
    return pos




def compare_dus(filename, lpcbrowser_dus, counts):
    global identical, different
    source_filename = g_paths.html_output + filename
    xml_string = subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + hurst_xsl, '-'],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(file(source_filename).read())[0]
    hurst_xml = et.fromstring(xml_string)
    for du in hurst_xml.findall("{http://www.hursts.eclipse.co.uk/dul}du"):
        ident = du.attrib["id"][4:]
        if ident.split(".")[1] == "NA": continue
        if not du.text: du.text = u""
        if type(du.text) != unicode:
            du.text = unicode(du.text, "utf-8")
        hurst_text = re.sub(u"[\=\s \u200B:\u2222\u2022]+", "", du.text).upper()
        if hurst_text == lpcbrowser_dus.get(ident):
            print ident, "identical", counts
            counts[0] += 1
        else:
            print filename
            if not lpcbrowser_dus.has_key(ident):
                print ident, "not found in LPC browser\n", counts
                counts[2] += 1
                continue
            counts[1] += 1
            print ident, counts
            print "=" * 30
            c = index_of_first_difference(hurst_text, lpcbrowser_dus[ident])
            print hurst_text[c:][:100].encode("utf8")
            print "-" * 30
            print lpcbrowser_dus[ident][c:][:100].encode("utf8")
            print



def _process_lpcbrowser_file(filename, dus):
    xml_string = subprocess.Popen(["xsltproc", "--nonet", "--novalid", g_paths.xsldir + lpcbrowser_xsl, '-'],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                  ).communicate(file(filename).read())[0]
    lpc_xml = et.fromstring(xml_string)
    for du in lpc_xml.findall("{http://www.hursts.eclipse.co.uk/dul}du"):
        duid = re.search(r"(\d{8}.\d{7})", du.attrib["id"]).group(1)
        if not du.text: du.text = u""#guard against empty DU
        if type(du.text) != unicode:
            du.text = unicode(du.text, "utf-8")
        dus[duid] = re.sub(u"[\=\s :\u200B\u2222\u2022]+", "", du.text).upper()
        if dus[duid][-5:] == "//END":
            dus[duid] = dus[duid][:-5]


def _process_lpcbrowser_group(ident, dus):
    candidate_files = glob.glob(lpcbrowser_data_path + ident + "*.xhtml")
    for filename in candidate_files:
        _process_lpcbrowser_file(filename, dus)


def _process_lpcbrowser_du(ident, dus):
    candidate_files = glob.glob(lpcbrowser_data_path + ident + "*.xhtml")
    if not candidate_files:
        dus[ident] = "^"
        return
    candidate_files.sort()
    _process_lpcbrowser_file(candidate_files[-1], dus)


def get_lpcbrowser_dus(m, ident):
    dus = {}
    def _recursive_add_lpcbrowser_du(ident):
        if m.get_type(ident) == meta.TYPE_SECTION:
            for c in m.get_children(ident):
                _recursive_add_lpcbrowser_du(c)
        elif m.get_type(ident) == meta.TYPE_GROUP:
            _process_lpcbrowser_group(ident, dus)
        elif m.get_type(ident) == meta.TYPE_DUCONTAINER:
            for c in m.get_children(ident):
                _process_lpcbrowser_du(c, dus)
    _recursive_add_lpcbrowser_du(ident)
    return dus



def make_page_list(m):
    pages = []
    def _recursive_add_page(ident):
        if ident and (m.get_section_depth(ident) == chunk_depth or
                      m.get_type(m.get_children(ident)[0]) != meta.TYPE_SECTION):
            pages.append(ident)
        else:
            for c in m.get_children(ident):
                _recursive_add_page(c)
    _recursive_add_page(None)
    return pages


def main():
    m = meta.FCOMMeta(True)
    f = factory.FCOMFactory(m)
    counts = [0, 0, 0]
    for c, p in enumerate(make_page_list(m)):
        filename = f._make_href(p)
        print c , filename
        if filename[:11] == "PRO.NOR.SOP": continue
        lpcbrowser_dus = get_lpcbrowser_dus(m, p)
        compare_dus(filename, lpcbrowser_dus, counts)
    print zip(["Identical", "Different", "Not found"], counts)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage", sys.argv[0], "STARTPATH OUTPUTPATH"
    global g_paths
    g_paths.initialise(*sys.argv)
    main()
