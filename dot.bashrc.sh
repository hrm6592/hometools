#!/bin/bash
# .bashrc
# -----------------------------------------------------------------------------
unset LC_ALL
export LC_ALL=ja_JP.UTF-8

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
if [ "$TERM" != "dumb" ]; then
    eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias ll='ls --color=auto -alF'
    alias la='ls --color=auto -A'
    alias l='ls --color=auto -CF'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'

    # Set a terminal prompt style (default is fancy color prompt)
    PS1="\[\e]2;\u@\h \W\a\]\[\e[1;31m\][\u@\h \W]\\$\[\e[0m\] "
else
    alias ls="ls -F"
    alias ll='ls -alF'
    alias la='ls -A'
    alias l='ls -CF'
fi

export PATH=/usr/local/cuda/bin:${PATH:+:${PATH}}
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# don't put duplicate lines in the history. See bash(1) for more options
# ... or force ignoredups and ignorespace
HISTCONTROL=ignoreboth:erasedups
HISTTIMEFORMAT='%F %T '

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=16384
HISTFILESIZE=16384

# # ignore some command to keeping list more clean
HISTIGNORE=history:ls:ll:'ls -la':st:se

# pkg-config path
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib64/pkgconfig:/usr/local/lib/pkgconfig

# Useful but Miscellaneous aliases
alias l1u='ls -1 *.1080p.mp4 | cut -n -b 1-4 | sort | uniq -c | sort -rn | head'
alias lS='ls -l -h -Sr --color=auto [A-Za-z0-9]*.{avi,mp4,wmv,mkv,rmvb} 2> /dev/null | tail -10'
alias ll='ls -l -h --color=auto'
alias llv='ls -F | cut -n -b 1-95 | less'
alias ls15='ls -1tr [0-9A-Z]*.* | grep -v "jpg\|mp3\|added\|incomplete" | head -15 | xargs -i% printf "mv % '\'''\'' ;\\ \n"'
alias lu='ls -1d [A-Z]* | cut -n -b 1-4 | sort | uniq -c | sort -rn | head'
alias mif='mediainfo --Output="Video;%FrameRate_Mode%,%FrameRate%\n"'
alias psV='ps -ef | grep "mencoder\|ffmpeg" | grep -v grep'
alias vh='history | grep "menc\|ffmpeg" | grep -v grep | tail -12'
alias vsinfo="mediainfo --Output=$'General;%FileName%\r\nVideo;\t%Width%x%Height%\t%Format%:%CodecID%\t%FrameRate_Mode%:%FrameRate% fps\n'"
alias st='~hrm/bin/sulvage_mp4.plx -h $(pwd) -t'
alias se='~hrm/bin/sulvage_mp4.plx -h $(pwd)'
