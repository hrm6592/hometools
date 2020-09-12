#!/bin/bash
# Convert file extension to correct video type.
#
mi=/usr/local/bin/mediainfo
optFormat='--Output=General;%Format%'
optWidth='--Output=Video;%Width%'
pattern=".*[\.\-]1080p\..*"

cd /var/spool/torrent

for f in [A-Z]*.{mp4,mkv,wmv}
do
    if [[ $f =~ $pattern ]]; then
        continue
    elif [ -e "$f" ]; then
        ext=`echo ${f##*.} | tr '[:lower:]' '[:upper:]'`
        type=`$mi $optFormat "$f"`
        width=`$mi $optWidth "$f"`
        chmod 644 "$f"
    else
        continue
    fi

    # Basename of file.
    bn=${f%.*}

    # check width of video and add basename to "1080p"
    # if needed.
    if [ "$width" == "1920" ]; then
        bn="${bn}.1080p"
        echo "$f has 1920px width."
    fi

    # Check video format.
    if [ "$ext" == "MP4" ]; then

        # rename to properly exts.
        if [ "$type" == "MPEG-4" ]; then
            # add size identifier
            if [ $f != "$bn.mp4" ]; then
                mv $f ${bn}.mp4
            fi
        elif [ "$type" == "AVI" ]; then
            mv $f ${bn}.avi
        elif [ "$type" == "Windows Media" ]; then
            mv $f ${bn}.wmv
        elif [ "$type" == "MPEG-TS" ]; then
            mv $f ${bn}.ts
        elif [ "$type" == "BDAV" ]; then
            mv $f ${bn}.m2ts
        fi
    else
        echo "$f is formatted as $ext"
    fi
done
