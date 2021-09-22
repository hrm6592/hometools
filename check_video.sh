#!/bin/bash
# Convert file extension to correct video type.
#
mi=/usr/local/bin/mediainfo
optFormat='--Output=General;%Format%'
optWidth='--Output=Video;%Width%'
pattern=".*[\.\-]1080p\..*"

cd /var/spool/torrent || exit 2

for f in [0-9A-Za-z]*.{mp4,mkv,wmv}
do
    if [[ $f =~ $pattern ]]; then
        continue
    elif [ -e "$f" ]; then
        ext=$(echo "${f##*.}" | tr '[:lower:]' '[:upper:]')
        type=$($mi $optFormat "$f")
        width=$($mi $optWidth "$f")
        chmod 644 "$f"
    else
        continue
    fi

    # Basename of file.
    bn=${f%.*}

    # remove unwanted index number from file name.
    # 259LUXU-1117.mp4
    # 326NKR-008.mp4
    if [[ $bn =~ ^([0-9]{3})([A-Z].*)$ ]]; then
        idx=${BASH_REMATCH[1]}
        if [ $idx == "420" ]; then
            # Exclude "420POW" series.
            bn=${BASH_REMATCH[0]}
        else
            bn=${BASH_REMATCH[2]}
        fi
    fi

    # remove unwanted prefix string
    if [[ $bn =~ _TEST[0-9]$ ]]; then
        # My encording test files.
        continue
    elif [[ $bn =~ (10mu|1pon|carib|paco)$ ]]; then
        # Uncencored movies
        # 012321-001.carib.mp4
        # 051420_01.10mu.mp4
        continue
    elif [[ $bn =~ ^hhd000.*内容_(.*)$ ]]; then
        # hhd000.com_免翻#墙免费访问全球最大情#色网站P#ornhub,可看收费内容_FSDSS-027.1080p.mp4
        bn=${BASH_REMATCH[1]}
    elif [[ $bn =~ ^(xxfhd|hhd800)\.com?_原版首发_(.*)$ ]]; then
        # xxfhd.com_原版首发_SSNI-652.mp4
        # hhd800.com_原版首发_JUL-190.mp4
        bn=${BASH_REMATCH[2]}
    elif [[ $bn =~ ^(xxfhd\.com|独家首发)_(.*)$ ]]; then
        # xxfhd.com_IPX-416.mp4
        # 独家首发_FSDSS-007.1080p.mp4
        bn=${BASH_REMATCH[2]}
    elif [[ $bn =~ ^([0-9A-Z\-]+)[_@].* ]]; then
        # PPPD-842_hhd000.com_免翻_墙免费访问全球最大情_色网站P_ornhub_可看收费内容.mp4
        # HND-808@hhd000.com_免翻#墙免费访问全球最大情#色网站P#ornhub,可看收费内容.1080p.mp4
        bn=${BASH_REMATCH[1]}
    fi

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
            if [ "$f" != "$bn.mp4" ]; then
                mv "$f" "${bn}.mp4"
            fi
        elif [ "$type" == "AVI" ]; then
            mv "$f" "${bn}.avi"
        elif [ "$type" == "Windows Media" ]; then
            mv "$f" "${bn}.wmv"
        elif [ "$type" == "MPEG-TS" ]; then
            mv "$f" "${bn}.ts"
        elif [ "$type" == "BDAV" ]; then
            mv "$f" "${bn}.m2ts"
        elif [ "$type" == "Matroska" ]; then
            mv "$f" "${bn}.mkv"
        fi
    else
        echo "$f is formatted as $ext"
    fi
done
