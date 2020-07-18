#!/bin/bash
rotate_interval=10
max_rotation=50
command="cat $1 | xargs -I {} convert -delay 10"
command="$command -size 500x400 -background white -bordercolor white -border 75x75 -gravity center -fill 'rgb(255,127,0)' -stroke white -font $2/imperfect.ttf  caption:{} -flatten -compose Src"
for i in $(seq 0 1 3); do
    mod=$(( $i % 2 ))
    [ $i -gt 1 ] && mult="-1" || mult="1"
    for j in $(seq 0 $rotate_interval $max_rotation); do
        [ $mod -eq "0" ] && \
            rotate=$(( $mult*$j )) || \
            rotate=$(( $mult*($max_rotation - $j) ))
        command="$command \\( -clone 0 -rotate $rotate -clone 0 +swap -composite \\)"
    done
done

command="$command -delete 0 -loop 5 $3"

# echo $command
eval $command
