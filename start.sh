#!/bin/bash


#export DAEMONIZE=yes

export BIND_ADDRESS=0.0.0.0
export BIND_PORT=1025

export RELAY_HOST=smtp.yandex.com
export RELAY_HOST_PORT=587
export RELAY_HOST_TLS=yes
export RELAY_USER=test@yandex.com
export RELAY_PASSWD=test_passwd

export WORKING_DIRECTORY=`pwd`
export PIDFILE=$WORKING_DIRECTORY/smtp.pid
export LOG_FILE=$WORKING_DIRECTORY/log.txt


python simplerelay.py
