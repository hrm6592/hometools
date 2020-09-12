#!/bin/bash
#
# marimo-counter
#
# chkconfig: 345 96 5
# description: starts the Access counter daemon.
#
# processname: counter
# pidfile: /var/run/counter.pid
#
### BEGIN INIT INFO
# Provides:          marimo-counter
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: starts the access counter daemon
# Description:       
### END INIT INFO

# source function library
. /etc/rc.d/init.d/functions

# pull in sysconfig settings
[ -f /etc/sysconfig/counter ] && . /etc/sysconfig/counter

# Initialize variables.
[ -z $RUNUSER ] && exit 2
NAME=""

rhstatus() {
  status -p $PIDFILE $prog $exec
}

start() {
}

stop() {
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
