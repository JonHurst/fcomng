#!/usr/bin/python
# coding=utf-8

import sys
import subprocess
import xml.etree.cElementTree as et
import re
import os
import difflib

lpcbrowser_data_path = '/home/jon/tmp/xhtml/'
project_path = '/home/jon/proj/fcomng/'
hurst_xsl = project_path + 'xsl/autotest_hurst.xsl'
lpcbrowser_xsl = project_path + 'xsl/autotest_lpcbrowser.xsl'


def lpcbrowser_text(ident):
    #try du file
    filename = lpcbrowser_data_path + ident[4:] + ".xhtml"
    if not os.path.exists(filename): return "^"
    page_string= unicode(subprocess.Popen(["xsltproc", "--nonet", "--novalid", lpcbrowser_xsl, '-'],
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                          ).communicate(file(filename).read())[0], 'utf-8')
    return page_string


def main(filename):
    page_string = subprocess.Popen(["xsltproc", "--nonet", "--novalid", hurst_xsl, '-'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                   ).communicate(file(filename).read())[0]
    hurst_xml = et.fromstring(page_string)
    for du in hurst_xml.findall("{http://www.hursts.eclipse.co.uk/dul}du"):
        ident = du.attrib["id"]
        hurst_text = du.text
        if type(du.text) != unicode:
            hurst_text = unicode(du.text, "utf-8")
        hurst_text = re.sub(u"[\=\s \u200B:\u2222\u2022]+", "", hurst_text).upper()
        lpc_text = lpcbrowser_text(ident)
        lpc_text = re.sub(u"[\=\s :\u200B\u2222\u2022]+", "", lpc_text).upper()
        print ident
        print "=" * 30
        if hurst_text == lpc_text:
            print "Identical"
        else:
            print "Different:"
            for c, char in enumerate(hurst_text):
                if char != lpc_text[c]:
                    print hurst_text[c:]
                    print "-" * 30
                    print lpc_text[c:]
                    print
                    break



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage", sys.argv[0], "FILENAME"
    main(sys.argv[1])
