#!/bin/bash
cat $1 | xargs -I {} convert -delay 10 \
    -size 500x400 \
    -background white \
    -bordercolor white \
    -border 75x75 \
    -gravity center \
    -fill 'rgb(57,201,254)' \
    -stroke 'rgb(0,0,170)' \
    -font $2/csmb.ttf \
    caption:{} \
    -flatten \
    -compose Src  \
    -wave 8x150 \
    $3