#!/bin/bash
echo "$(free | awk '/Mem:/{printf  "%3.1f", $3/($3+$4)*100}')"'%'
