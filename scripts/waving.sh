#!/bin/bash

# based off of https://www.imagemagick.org/Usage/warping/animate_flex
command="cat $1 | xargs -I {} convert -delay 10"
command="$command -size 500x400 -background white -bordercolor white -border 75x75 -gravity center -fill 'rgb(57,201,254)' -stroke 'rgb(0,0,170)' -font $2/csmb.ttf caption:{} -flatten -compose Src"
for i in $(seq 18 -2 -24; seq -22 2 16); do
    command="$command \\( -clone 0 -clone 0 -wave ${i}x150 +swap -composite \\)"
done

command="$command -delete 0 -loop 0 $3"

eval $command
