#!/bin/bash
for cssfile in css/orig/*.css
do
    echo cleancss $cssfile -o css/`basename ${cssfile%.css}`.min.css
done

for jsfile in js/orig/*.js
do
    echo uglifyjs $jsfile -o js/`basename ${jsfile%.js}`.min.js
done
