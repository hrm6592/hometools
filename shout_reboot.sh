#!/bin/sh

SHOUT=/usr/bin/shout
PGREP=/usr/bin/pgrep

# Stop current working shout.
PID=`${PGREP} -P 1 shout`
RETVAL=$?

if [ ${RETVAL} -eq "0" ]
then
  kill -9 ${PID}
else
  echo "shout is NOT running. Start shout anyway."
fi

# Restarting shout.
sleep 1
${PGREP} -P 1 shout > /dev/null 2>&1
RETVAL=$?

if [ $RETVAL -eq "1" ]
then
  $SHOUT --private &
  /sbin/service httpd restart
fi

exit 0
