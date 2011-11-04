#!/usr/bin/python

import glob
import re
import xml.etree.ElementTree
import os.path
import hashlib
import shutil

base_dir = "/home/jon/proj/fcomng/"
html_dir = base_dir + "html/"
cgm_dir = base_dir + "ILLUS/"
image_library = base_dir + "image-library/"
image_output = base_dir + "images/"



def cgmtopng(matchobj):
    tag =  matchobj.group(0)
    cgm_filename = os.path.basename(re.search('src="([^"]*)"', tag).group(1))
    class_attrib_mo = re.search('class="[^"]*"',tag)
    class_attrib = ""
    if class_attrib_mo:
        class_attrib = class_attrib_mo.group()
    if cgm_filename[-3:] != "cgm":
        return tag
    if not cgm_index.has_key(cgm_filename):
        print "Warning:", cgm_filename, "not in library"
        return tag
    cgm_element = cgm_index[cgm_filename]
    #check md5sum of cgm file
    md5sum = hashlib.md5(file(cgm_dir + cgm_filename).read()).hexdigest()
    if md5sum != cgm_element.get("md5"):
        print "Warning:", cgm_filename, "has incorrect checksum"
    png_elements = cgm_element.findall("pngfile")
    png, pngzoom = None, None
    for p in png_elements:
        if p.get("role") == "xhtml":
            png = p
        elif p.get("role") == "xhtml.zoom":
            pngzoom = p
    if png != None:
        png_filename = png.get("href")
        shutil.copyfile(image_library + png_filename, image_output + png_filename)
        tag = '<img ' + class_attrib + ' src="../images/' + png_filename + '" alt="png"/>'
        if pngzoom != None:
            pngzoom_filename = pngzoom.get("href")
            shutil.copyfile(image_library + pngzoom_filename, image_output + pngzoom_filename)
            tag += '<p><a href="../images/' + pngzoom_filename + '">Zoom</a></p>'
    print "Processed", cgm_filename
    return tag


#get image library index
ili = xml.etree.ElementTree.ElementTree(None, image_library  + "image-list.xml")
cgm_index = {}
for el in ili.findall("cgmfile"):
    cgm_index[el.get("href")] = el
#process html files
html_files = glob.glob(html_dir + "*.html")
html_files.sort()
for f in html_files:
    print "Processing:", f
    #find all the image tags
    infile = open(f)
    original = infile.read()
    infile.close()
    modified = re.sub("<img[^>]*></img>", cgmtopng, original)
    if modified != original:
        outfile = open(f, "w")
        outfile.write(modified)
