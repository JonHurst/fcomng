#!/usr/bin/python

import glob
import hashlib
import xml.etree.ElementTree
import os.path
import subprocess
import re
import optparse

base_directory = "/home/jon/proj/fcomng/"
cgm_directory = base_directory + "ILLUS/"
png_directory = base_directory + "image-library/"
identify_path = "/usr/bin/identify"


def fill_png_attribs(filename, png_attribs):
    png_attribs["href"] = os.path.basename(filename)
    png_attribs["md5"] = hashlib.md5(file(filename).read()).hexdigest()
    identify_output = subprocess.Popen(
        [identify_path, filename],
        stdout = subprocess.PIPE).communicate()[0]
    png_attribs["size"] = re.search(" (\d+x\d+) ", identify_output).group(1)


# def create_list_from_filenames():
#     cgm_images = glob.glob(cgm_directory + "*.cgm")
#     tb = xml.etree.ElementTree.TreeBuilder()
#     tb.start("imagelist", {})
#     for i in cgm_images:
#         print i
#         cgm_attribs = {}
#         basename = os.path.basename(i)
#         cgm_attribs["href"] = basename
#         cgm_attribs["md5"] = hashlib.md5(file(i).read()).hexdigest()
#         tb.start("cgmfile", cgm_attribs)
#         png_filename = png_directory + basename[:-3] + "png"
#         if os.path.exists(png_filename):
#             png_attribs = {}
#             fill_png_attribs(png_filename, png_attribs)
#             png_attribs["role"] = "xhtml"
#             tb.start("pngfile", png_attribs)
#             tb.end("pngfile")
#         png_filename = png_directory + basename[:-3] + "hr.png"
#         if os.path.exists(png_filename):
#             png_attribs = {}
#             fill_png_attribs(png_filename, png_attribs)
#             png_attribs["role"] = "xhtml.zoom"
#             tb.start("pngfile", png_attribs)
#             tb.end("pngfile")
#         tb.end("cgmfile")
#     tb.end("imagelist")
#     xml.etree.ElementTree.ElementTree(tb.close()).write(output_file)

def add_image(cgmfile, library_path):
    tb = xml.etree.ElementTree.TreeBuilder()
    cgm_attribs = {}
    basename = os.path.basename(cgmfile)
    cgm_attribs["href"] = basename
    cgm_attribs["md5"] = hashlib.md5(file(cgmfile).read()).hexdigest()
    tb.start("cgmfile", cgm_attribs)
    png_filename = library_path + basename[:-3] + "png"
    if os.path.exists(png_filename):
        print "Adding", png_filename
        png_attribs = {}
        fill_png_attribs(png_filename, png_attribs)
        png_attribs["role"] = "xhtml"
        tb.start("pngfile", png_attribs)
        tb.end("pngfile")
    else:
        print png_filename, "not found. Aborting."
        return
    png_filename = png_directory + basename[:-3] + "hr.png"
    if os.path.exists(png_filename):
        print "Adding", png_filename
        png_attribs = {}
        fill_png_attribs(png_filename, png_attribs)
        png_attribs["role"] = "xhtml.zoom"
        tb.start("pngfile", png_attribs)
        tb.end("pngfile")
    tb.end("cgmfile")
    filename = library_path + "image-list.xml"
    image_list = xml.etree.ElementTree.parse(filename)
    for cgm in image_list.findall("cgmfile"):
        if cgm.get('href') == basename:
            image_list.getroot().remove(cgm)
            break
    image_list.getroot().append(tb.close())
    image_list.write(filename)




if __name__ == "__main__":
    parser = optparse.OptionParser(description="Edit the image library",
                                   usage="%prog add|rm [options] CGMFILE")
    parser.add_option("--library-path", dest="library_path", default=png_directory)
    options, args = parser.parse_args()
    if args[0] == "add":
        if len(args) >= 2:
            add_image(args[1], options.library_path)
        else:
            print "CGMFILE must be specified"
    elif args[0] == "rm":
        print "Not implemented yet!"
    else:
        print "Action must be add or rm"
