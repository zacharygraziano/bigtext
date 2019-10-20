#!/bin/bash
echo $2
cat $1 | xargs -I {} \
convert \
    -size 500x400 \
    -background white \
    -font $2/csmb.ttf \
    -gravity Center \
    caption:{} \
    -flatten \
    -bordercolor white \
    -border 50x50 \
    $3