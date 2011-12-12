#!/bin/bash

cd /home/jon/proj/fcomng/html
xmllint --noout --dtdvalid /usr/share/xml/xhtml/schema/dtd/1.0/xhtml1-strict.dtd --valid *.html
