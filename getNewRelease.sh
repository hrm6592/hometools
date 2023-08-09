#!/bin/bash
# -*- coding: utf-8 -*-
mastodon=${HOME}/.mastodon
now=$(cat "${mastodon}" 2> /dev/null)
new=$(curl -s https://github.com/tootsuite/mastodon/releases | fgrep css-truncate-target | head -1 | sed -e 's/ //g; s/<.[^>]*>//g')
if [ "x${new}" != "x" ] && [ "${new}" != "${now}" ]; then
     echo "${new}" | tee "${mastodon}" | whisper -b -c '#admin@pkan'
fi
