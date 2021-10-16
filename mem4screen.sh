#!/bin/bash
echo "$(free | awk '/buffers\/cache/{printf  "%3.1f", $3/($3+$4)*100}')"'%'
