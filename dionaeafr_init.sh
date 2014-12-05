#!/bin/bash

# DionaeaFR Startup script
# Koen Van Impe

. /lib/lsb/init-functions

BASEDIR="/opt/DionaeaFR"
PIDFILE="/var/run/dionaeafr.pid"
LOGFILE="/var/log/dionaeafr.log"
NAME="dionaeafr"
DAEMON="dionaeafr"
IP=127.0.0.1
PORT=8000

case $1 in
  start)
    cd $BASEDIR
    python manage.py runserver $IP:$PORT > $LOGFILE 2>> $LOGFILE &
    log_daemon_msg "$DAEMON started ..."
    log_end_msg 0
  ;;
  stop)
    if [ -e $PIDFILE ]; then
        kill `cat $PIDFILE`
        rm $PIDFILE
        log_daemon_msg "$DAEMON stopped ..."
        log_end_msg 0
    else
        log_daemon_msg "$DAEMON is *NOT* running"
        log_end_msg 1
    fi
  ;;
  collectstatic)
    cd $BASEDIR
    python manage.py collectstatic
  ;;
  logs)
    cat $LOGFILE
  ;;
  status)
    if [ -e $PIDFILE ]; then
        status_of_proc -p $PIDFILE $DAEMON "$NAME process" && exit 0 || exit $?
    else
        log_daemon_msg "$DAEMON is not running ..."
        log_end_msg 0
    fi
  ;;
  *)
  # For invalid arguments, print the usage message.
  echo "Usage: $0 {start|stop|collectstatic|logs|status}"
  exit 2
  ;;
esac

