#!/bin/bash
# covert to AVI format from other.

vid="/usr/local/bin/avidemux3_cli"

# Audio setting.
case "$1" in
    mp3)
        ae="--audio-codec MP3"
        of="--output-format AVI"
        ;;
    faac)
        ae="--audio-codec FAAC"
        of="--output-format MP4v2"
        ;;
    copy)
        ae="--audio-codec COPY"
        of="--output-format AVI"
        ;;
    *)
        echo "Usage: $0 (mp3|faac|copy) (x264|xvid) File1 [File2]..."
        RETVAL=1
        exit $RETVAL
        ;;
esac

# Video Setting.
case "$2" in
    x264)
        ve="--video-codec x264"
        # vc="--video-conf \"cq=24\""
        vc=""
        ;;
    xvid)
        ve="--video-codec xvid"
        vc=""
        ;;
    *)
        echo "Usage: $0 (mp3|faac|copy) (x264|xvid) File1 [File2]..."
        RETVAL=2
        exit $RETVAL
        ;;
esac

# ----------------------------------------------------------

if [ -e $3 ]; then
    echo "INPUT: $3"
    input="--force-alt-h264 --load $3"
    target=`basename $3 .flv`
    if [ $1 == "faac" ]; then
        output="--save $target.mp4"
    else
        output="--save $target.avi"
    fi
else
    echo "Usage: $0 (mp3|copy) (x264|xvid) File1 [File2]..."
    RETVAL=3
    exit $RETVAL
fi

echo "$vid $input $of $ae $ve $vc $output"
$vid $input $of $ae $ve $vc $output > "$target.log" 2>&1
