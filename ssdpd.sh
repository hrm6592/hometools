#!/bin/sh
#
# ssdpd SSDP Responder for Linux/UNIX
#
# chkconfig:   2345 95 95
# description: SSDP Responder for Linux/UNIX

### BEGIN INIT INFO
# Provides:       ssdpd
# Required-Start: $network
# Required-Stop:
# Should-Start:
# Should-Stop:
# Default-Start: 2 3 4 5
# Default-Stop:  0 1 6
# Short-Description: start and stop SSDP daemon
# Description: SSDP Responder for Linux/UNIX
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

prog=ssdpd
lockfile=/var/lock/subsys/$prog

start() {
        [ "$EUID" != "0" ] && exit 4
        [ "$NETWORKING" = "no" ] && exit 1
        [ -x /usr/local/sbin/ssdpd ] || exit 5

        # Start daemons.
        echo -n $"Starting $prog: "
        daemon $prog -l info -s eth0
        RETVAL=$?
        echo
        [ $RETVAL -eq 0 ] && touch $lockfile
        return $RETVAL
}

stop() {
        [ "$EUID" != "0" ] && exit 4
        echo -n $"Shutting down $prog: "
        killproc $prog
        RETVAL=$?
        echo
        [ $RETVAL -eq 0 ] && rm -f $lockfile
        return $RETVAL
}

restart() {
    stop
    start
}

case "$1" in
    start)
        status $prog && exit 0
        $1
        ;;
    stop)
        status $prog || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    status)
        status $prog
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 2
esac
exit $?
