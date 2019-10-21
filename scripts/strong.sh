#!/bin/bash
cat $1 | xargs -I {} convert -delay 10 \
    -size 500x400 \
    -background white \
    -bordercolor white \
    -border 75x75 \
    -gravity center \
    -fill 'rgb(255,127,0)' \
    -stroke black -font $2/imperfect.ttf \
    -strokewidth 2 \
    caption:{} \
    -flatten \
    -compose Src  \
    -rotate -8 \
    $3
