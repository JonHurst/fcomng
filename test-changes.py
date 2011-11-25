#!/usr/bin/python
# coding=utf-8

import glob
import re

test_html = "html/"
target_html = "unit-test-target/"

def main():
    identical_count, differ_count = 0, 0
    for test_html_filename in glob.iglob("html/*.html"):
        target_html_filename = target_html + test_html_filename[len(test_html):]
        test = open(test_html_filename).read()
        test = re.sub(r"fnidid\d+", "", test)
        target = open(target_html_filename).read()
        target = re.sub(r"fnidid\d+", "", target)
        if test == target:
            identical_count += 1
        else:
            differ_count += 1
            print test_html_filename, target_html_filename, "differ"
    print identical_count, "files are identical"
    print differ_count, "files differ"


if __name__ == "__main__":
    main()


