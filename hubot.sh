#!/bin/bash
#
# hubot        Hubot is your friendly robot sidekick. Install him in
#              your company to dramatically improve employee 
#              efficiency.
#
# chkconfig: 345 96 5
# description: starts the Hubot bot for IRC@haun.jp
#
# processname: hubot
# pidfile: /var/run/hubot.pid
#
### BEGIN INIT INFO
# Provides:          hubot
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: starts the hubot service
# Description:       starts the Hubot bot for IRC@haun.jp
### END INIT INFO

# source function library
. /etc/rc.d/init.d/functions

# pull in sysconfig settings
[ -f /etc/sysconfig/hubot ] && . /etc/sysconfig/hubot

# Initialize variables.
[ -z $RUNUSER ] && exit 6
NAME="Hubot"
HOME="/home/${RUNUSER}/hubot_${RUNUSER}/"
LOGFILE="/var/log/hubot/hubot.log"
PIDFILE="/var/run/hubot.pid"
RETVAL=0
prog="hubot"
lockfile="/var/lock/subsys/$prog"
exec="/home/${RUNUSER}/hubot_${RUNUSER}/node_modules/hubot/bin/hubot"
DAEMON="$exec"

# set PATH
export PATH=/home/${RUNUSER}/hubot_${RUNUSER}/node_modules/hubot/bin:\
/home/${RUNUSER}/hubot_${RUNUSER}/node_modules/.bin:\
${PATH}

start () {
  [ -x $exec ] || exit 5
  umask 077
  cd $HOME
  echo -n $"Starting $NAME: "
  daemon --pidfile="$PIDFILE" \
         --user="$RUNUSER" \
         "nohup $DAEMON $OPTIONS >/dev/null 2>&1 &"
  RETVAL=$?
  echo
  if [ $RETVAL -eq 0 ]; then
    touch $lockfile
    procid="$(pgrep -f $prog)"
    echo $procid > $PIDFILE
  fi
  return $RETVAL
}

stop () {
  echo -n $"Stopping $NAME: "
  killproc -p "$PIDFILE" $exec
  RETVAL=$?
  echo
  [ $RETVAL -eq 0 ] && rm -f $lockfile $PIDFILE
  return $RETVAL
}

rhstatus() {
  status -p $PIDFILE $prog $exec
}

case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  restart)
        stop
        start
        ;;
  status)
        rhstatus
        ;;
  *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|status}" >&2
        exit 1
        ;;  
    esac
exit
