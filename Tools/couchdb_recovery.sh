#! /bin/bash
cd /var/lib/couchdb
if [ ! -d "1.3.1_backup" ]; then
 mkdir 1.3.1_backup
 echo "1.3.1_backup folder is created"
fi
if [ -d "1.3.1" ]; then
 cd /var/lib/couchdb/1.3.1
 echo "copying files"
 cp * ../1.3.1_backup
 cd ..
 service couchdb stop
 rm -r /var/lib/couchdb/1.3.1
 service couchdb restart
 service couchdb stop
 if [ ! -d "/var/lib/couchdb/1.3.1" ]; then
  mkdir 1.3.1
 fi
 cp ./1.3.1_backup/* ./1.3.1/
 cd /var/lib/couchdb/1.3.1
 chown couchdb *
 chgrp couchdb *
 chmod 664 *.couch
 service couchdb restart
else
 echo "no 1.3.1 folder found"
fi
