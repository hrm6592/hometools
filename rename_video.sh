#!/bin/bash

mi=/usr/local/bin/mediainfo
mi_options='--Output=Video;%Width%'

cd /home/data_02/Movies/Anime/R18 || exit 2
for f in \[Thz.la\]*.* [0-9]*[a-z]*.*
do
    if [ -e "$f" ] && [ -f "$f" ]; then
        bn=${f%.*}
        ext=${f##*.}
        width=$($mi $mi_options "$f")
        chmod 644 "$f"
    else
        continue
    fi

    if [[ $bn =~ ^\[Thz\.la\]([a-z]+)\-([0-9]+)$ ]]; then
        label=$(echo "${BASH_REMATCH[1]}" | tr '[:lower:]' '[:upper:]')
        num=${BASH_REMATCH[2]}
    elif [[ $bn =~ ^[0-9]{4}([a-z]{2,4})([0-9]{3,5})(FHD)?$ ]]; then
        label=$(echo "${BASH_REMATCH[1]}" | tr '[:lower:]' '[:upper:]')
        num=${BASH_REMATCH[2]}
    else
        echo "regex missmatch, ignored : $bn"
        continue
    fi

    # echo "${label}-${num}.${ext}"

    if [ "$width" = "1920" ]; then
        mv "$f" "${label}-${num}.1080p.${ext}"
    else
        mv "$f" "${label}-${num}.${ext}"
    fi

done
exit 0
