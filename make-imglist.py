#!/usr/bin/python

import glob
import hashlib
import xml.etree.ElementTree
import os.path
import subprocess
import re

base_directory = "/home/jon/proj/fcomng/"
cgm_directory = base_directory + "ILLUS/"
png_directory = base_directory + "image-library/"
identify_path = "/usr/bin/identify"
output_file = png_directory + "image-list.xml"


def fill_png_attribs(filename, png_attribs):
    png_attribs["href"] = os.path.basename(filename)
    png_attribs["md5"] = hashlib.md5(file(filename).read()).hexdigest()
    identify_output = subprocess.Popen(
        [identify_path, filename],
        stdout = subprocess.PIPE).communicate()[0]
    png_attribs["size"] = re.search(" (\d+x\d+) ", identify_output).group(1)


def create_list_from_filenames():
    cgm_images = glob.glob(cgm_directory + "*.cgm")
    tb = xml.etree.ElementTree.TreeBuilder()
    tb.start("imagelist", {})
    for i in cgm_images:
        print i
        cgm_attribs = {}
        basename = os.path.basename(i)
        cgm_attribs["href"] = basename
        cgm_attribs["md5"] = hashlib.md5(file(i).read()).hexdigest()
        tb.start("cgmfile", cgm_attribs)
        png_filename = png_directory + basename[:-3] + "png"
        if os.path.exists(png_filename):
            png_attribs = {}
            fill_png_attribs(png_filename, png_attribs)
            png_attribs["role"] = "xhtml"
            tb.start("pngfile", png_attribs)
            tb.end("pngfile")
        png_filename = png_directory + basename[:-3] + "hr.png"
        if os.path.exists(png_filename):
            png_attribs = {}
            fill_png_attribs(png_filename, png_attribs)
            png_attribs["role"] = "xhtml.zoom"
            tb.start("pngfile", png_attribs)
            tb.end("pngfile")
        tb.end("cgmfile")
    tb.end("imagelist")
    xml.etree.ElementTree.ElementTree(tb.close()).write(output_file)


create_list_from_filenames()

