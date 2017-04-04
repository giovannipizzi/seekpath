#!/bin/bash
## To install:
## npm install clean-css-cli -g
## npm install uglifyjs -g


for cssfile in css/orig/*.css
do
    cleancss $cssfile -o css/`basename ${cssfile%.css}`.min.css
done

for jsfile in js/orig/*.js
do
    uglifyjs $jsfile > js/`basename ${jsfile%.js}`.min.js
done
