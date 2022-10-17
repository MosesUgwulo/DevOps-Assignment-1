#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2
#
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)
HTTPD_STATUS=$(systemctl status $1 | awk 'NR == 3')

HTTPD_UPTIME=$(uptime | awk '{print $3,$4}' | cut -d, -f1)


HTTPD_SITES=$(ls /etc/httpd/conf.d/ | grep -v default)
HTTPD_USERS=$(cat /etc/passwd | grep httpd | awk -F: '{print $1}')







echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
echo "No of httpd processes: $HTTPD_PROCESSES"
echo "httpd status: $HTTPD_STATUS"


echo "httpd uptime: $HTTPD_UPTIME"


echo "httpd sites: $HTTPD_SITES"
echo "httpd users: $HTTPD_USERS"






if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi
