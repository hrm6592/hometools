#!/bin/bash
youtubename=`youtube-dl --get-filename $1`
echo $youtubename

videoname=`echo "$youtubename" | sed -e 's/webm\$/mp4/g'`
#videoname=`basename "$youtubename" .e`.mp4
echo $videoname

audioname=`echo $videoname | sed -e 's/mp4\$/m4a/g'`
#audioname=`basename "$youtubename" .e`.m4a
echo $audioname

muxname=`echo $videoname | sed -e 's/mp4\$/mux.mp4/g'`
#muxname=`basename "$youtubename" .e`.mux.mp4
echo $muxname

youtube-dl -F $1

echo -n "-f option [137,140]: "
read optcodec
if [ "$optcodec" = "" ]; then
   optcodec="137,140"
fi

youtube-dl -f $optcodec $1

ffmpeg -i "$videoname" -i "$audioname" -c:v copy -c:a copy "$muxname" && \
rm "$videoname" && rm "$audioname"
