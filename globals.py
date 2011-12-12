#!/usr/bin/python
# coding=utf-8

import os
import xml.etree.cElementTree as et


class Paths:

    def initialise(self, scriptpath, startfile, outputdir):
        basedir = os.path.dirname(os.path.abspath(startfile))
        print basedir
        path_tree = et.parse(startfile)
        paths = {}
        for cp in path_tree.findall("components-path/component-path"):
            paths[cp.attrib["type"]] = cp.text
        self.control = os.path.join(basedir, path_tree.find("starter").text)
        self.global_meta = os.path.join(basedir, paths["product-metadata"])
        self.dus = os.path.join(basedir, paths["du-content"])
        self.mus = os.path.join(basedir, paths["du-metadata"])
        self.illustrations = os.path.join(basedir, paths["illustration"]) + "/"
        self.html_output = os.path.join(os.path.abspath(outputdir), "html/")
        self.image_output = os.path.join(os.path.abspath(outputdir), "images/")
        self.js_output = os.path.join(os.path.abspath(outputdir), "scripts/")
        self.xsldir = os.path.join(os.path.dirname(os.path.abspath(scriptpath)), "xsl/")
        self.pickles = os.path.join(os.path.dirname(os.path.abspath(scriptpath)), "pickles/")
        self.image_library = os.path.join(os.path.dirname(os.path.abspath(scriptpath)), "image-library/")


g_paths = Paths()


