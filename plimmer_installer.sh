#! /bin/sh

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters. Please provide a plimmer ID"
    exit
fi

wget https://pypi.python.org/packages/source/r/requests/requests-2.6.0.tar.gz#md5=25287278fa3ea106207461112bb37050 --no-check-certificate
wget https://pypi.python.org/packages/source/w/websocket-client/websocket_client-0.26.0.tar.gz --no-check-certificate

mkdir -p /mnt/sda1/libraries

tar -xf requests-2.6.0.tar.gz -C /mnt/sda1/libraries
tar -xf websocket_client-0.26.0.tar.gz -C /mnt/sda1/libraries

mv /mnt/sda1/libraries/req* /mnt/sda1/libraries/requests
mv /mnt/sda1/libraries/web* /mnt/sda1/libraries/websocket

cp *.py /mnt/sda1/libraries/


# Deleting last exit 0
head -n -1 /etc/rc.local > temp.txt 
mv temp.txt /etc/rc.local

echo "python /mnt/sda1/libraries/process_manager.py $1" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local


echo "**************************"
echo "PLEASE RESTART THE PLIMMER"
echo "**************************"
