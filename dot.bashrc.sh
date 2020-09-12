# .bashrc

# User specific aliases and functions
alias ll='ls -l -h --color=auto'
alias lS='ls -l -h -Sr --color=auto [A-Za-z0-9]*.{avi,mp4,wmv,mkv,rmvb} 2> /dev/null'
alias lT='ls -l -h -t --color=auto [A-Za-z]*.{avi,mp4}'
alias llv='ls -F | cut -n -b 1-95 | less'
alias ls15='ls -1tr [0-9A-Z]*.* | grep -v "jpg\|mp3\|added\|incomplete" | head -15 | xargs -n1 -i% printf "mv % '"'"''"'"' ;\\ \n"'

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

function lln () {
    \ls -1 "$@" | sort -d -k4,4;
}
