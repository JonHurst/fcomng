#!/bin/bash

cd /home/jon/proj/fcomng/html
echo Checking for IMPLWARNINGs
grep -l IMPLWARNING *
echo Checking for valid XHTML strict
xmllint --noout --dtdvalid /usr/share/xml/xhtml/schema/dtd/1.0/xhtml1-strict.dtd --valid *.html
