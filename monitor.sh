#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2
#
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)
HTTPD_STATUS=$(systemctl status httpd | grep Active | awk '{print $2}')
HTTPD_PORT=$(netstat -tulpn | grep httpd | awk '{print $4}' | cut -d: -f2)
HTTPD_ROOT=$(grep DocumentRoot /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_CONF=$(grep Include /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_LOG=$(grep ErrorLog /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_USER=$(grep User /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_GROUP=$(grep Group /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_PID=$(grep PidFile /etc/httpd/conf/httpd.conf | awk '{print $2}')
HTTPD_SITES=$(ls /etc/httpd/conf.d/ | grep -c .)
HTTPD_SITES_ENABLED=$(ls /etc/httpd/conf.d/ | grep -c .)
HTTPD_SITES_DISABLED=$(ls /etc/httpd/conf.d/ | grep -c .)
HTTPD_SITES_AVAILABLE=$(ls /etc/httpd/conf.d/ | grep -c .)


echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
echo "No of httpd processes: $HTTPD_PROCESSES"
echo "httpd status: $HTTPD_STATUS"
echo "httpd port: $HTTPD_PORT"
echo "httpd version: $HTTPD_VERSION"
echo "httpd root: $HTTPD_ROOT"
echo "httpd conf: $HTTPD_CONF"
echo "httpd log: $HTTPD_LOG"
echo "httpd user: $HTTPD_USER"
echo "httpd group: $HTTPD_GROUP"
echo "httpd pid: $HTTPD_PID"
echo "httpd modules: $HTTPD_MODULES"
echo "httpd sites: $HTTPD_SITES"
echo "httpd sites enabled: $HTTPD_SITES_ENABLED"
echo "httpd sites disabled: $HTTPD_SITES_DISABLED"
echo "httpd sites available: $HTTPD_SITES_AVAILABLE"


if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi
