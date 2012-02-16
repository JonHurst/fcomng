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
chunk_depth = 4
lpcbrowser_data_path = 'lpc_browser_xhtml/'


def _factory_error_reason():
    error_reason = {}
    for line in file("error-reasons"):
        duid, reason = line.split(" ", 1)
        error_reason[duid] = reason
    def _error_reason(duid):
        return error_reason.get(duid, "")
    return _error_reason
error_reason = _factory_error_reason()


def display_differences(a, b):
    context = 20
    sm = difflib.SequenceMatcher(None, a, b)
    matching_blocks = sm.get_matching_blocks()
    apos, bpos = 0, 0
    for block in matching_blocks:
        adiff = a[apos:block[0]]
        bdiff = b[bpos:block[1]]
        if adiff or bdiff:
            astr =  "A %s | %s | %s" % (a[max(0, apos - context):apos],
                                  adiff,
                                  a[block[0]: min(len(a), block[0] + context)])
            bstr =  "B %s | %s | %s" % (b[max(0, bpos - context):bpos],
                                  bdiff,
                                  b[block[1]: min(len(a), block[1] + context)])
            print astr.encode("utf8")
            print "-" * 30
            print bstr.encode("utf-8")
            print
        apos = block[0] + block[2]
        bpos = block[1] + block[2]


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
            # print ident, "identical", counts
            counts[0] += 1
        else:
            if not lpcbrowser_dus.has_key(ident):
                print filename, ident, "not found in LPC browser\n", counts
                counts[2] += 1
                continue
            print "\n", filename, ident
            known_error = error_reason(ident)
            if known_error:
                print "+ Known error:", known_error
                counts[3] += 1
            else:
                counts[1] += 1
            display_differences(hurst_text, lpcbrowser_dus[ident])
            print counts, "\n"


def _process_lpcbrowser_file(filename, dus, synthesis_group=False):
    extra_args = []
    if synthesis_group:
        extra_args = ["--stringparam", "synthesis", "True"]
    xml_string = subprocess.Popen(["xsltproc", "--nonet", "--novalid"] + extra_args + [g_paths.xsldir + lpcbrowser_xsl, '-'],
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


def _process_lpcbrowser_group(ident, dus, m):
    #If we're processing a group, it may be a group of DUs containing synthesisitem,
    #in which case we need to ignore footnotes and footnote refs. Thus, check the first
    #DU of the first DU_Container of the group for the phrase <!DOCTYPE synthesisitem.
    duident = m.get_children(m.get_children(ident)[0])[0]
    idstr = open(g_paths.dus + m.get_filename(duident)).read(200)
    synthesis_group = False
    if idstr.find("<!DOCTYPE synthesisitem") != -1:
        synthesis_group = True
    candidate_files = glob.glob(lpcbrowser_data_path + ident + "*.xhtml")
    for filename in candidate_files:
        _process_lpcbrowser_file(filename, dus, synthesis_group)


def _process_lpcbrowser_du(ident, dus):
    candidate_files = glob.glob(lpcbrowser_data_path + ident + "*.xhtml")
    if not candidate_files: return
    candidate_files.sort()
    _process_lpcbrowser_file(candidate_files[-1], dus)


def get_lpcbrowser_dus(m, ident):
    dus = {}
    def _recursive_add_lpcbrowser_du(ident):
        if m.get_type(ident) == meta.TYPE_SECTION:
            for c in m.get_children(ident):
                _recursive_add_lpcbrowser_du(c)
        elif m.get_type(ident) == meta.TYPE_GROUP:
            _process_lpcbrowser_group(ident, dus, m)
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
    counts = [0, 0, 0, 0]
    for c, p in enumerate(make_page_list(m)):
        filename = f._make_href(p)
        print c , filename
        lpcbrowser_dus = get_lpcbrowser_dus(m, p)
        compare_dus(filename, lpcbrowser_dus, counts)
    print zip(["Identical", "Different", "Not found", "Known error"], counts)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage", sys.argv[0], "STARTPATH OUTPUTPATH"
    global g_paths
    g_paths.initialise(*sys.argv)
    main()
