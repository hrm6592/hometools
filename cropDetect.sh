#!/bin/bash
#
SOURCE="$1"
CROP="1"
TOTAL_LOOPS="10"
NICE_PRI="10"
VF_OPTS="pp=lb,"
LOG="nohup.out"

######### CROP Settings #############
if [ "$CROP" == "1" ]; then
  echo "Please wait.  It make take a couple minutes to detect crop parameters."
  A=0
  
  while [ "$A" -lt "$TOTAL_LOOPS" ] ; do
    A="$(( $A + 1 ))"
    SKIP_SECS="$(( 35 * $A ))"
  
    nice -n $NICE_PRI nohup mplayer "$SOURCE" \
        -ss ${SKIP_SECS} \
        -identify \
        -frames 20 \
        -vo md5sum \
        -ao null \
        -nocache \
        -vf ${VF_OPTS}cropdetect=20:16 2>&1 > $LOG < /dev/null

    # echo DEBUG ; cat $LOG
  
    CROP[$A]=`awk -F 'crop=' '/crop/ {print $2}' < $LOG \
     | awk -F ')' '{print $1}' | tail -n 1`

  done
  rm md5sums $LOG

  B=0
  while [ "$B" -lt "$TOTAL_LOOPS" ] ; do
    B="$(( $B + 1 ))"
  
    C=0
    while [ "$C" -lt "$TOTAL_LOOPS" ] ; do
      C="$(( $C + 1 ))"
  
      if [ "${CROP[$B]}" == "${CROP[$C]}" ] ; then
        COUNT_CROP[$B]="$(( ${COUNT_CROP[$B]} + 1 ))"
      fi
    done  
  done
  
  HIGHEST_COUNT=0
  
  D=0
  while [ "$D" -lt "$TOTAL_LOOPS" ] ; do
     D="$(( $D + 1 ))"
  
       if [ "${COUNT_CROP[$D]}" -gt "$HIGHEST_COUNT" ] ; then
         HIGHEST_COUNT="${COUNT_CROP[$D]}"
         GREATEST="$D"
       fi
  done
  
  CROP="crop=${CROP[$GREATEST]}"
  
  echo -e "\n\nCrop Setting is: $CROP ... \n\n" 

fi
