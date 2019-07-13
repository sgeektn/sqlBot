# sqlBot
Install vnc like this :

sudo apt-get install --no-install-recommends ubuntu-desktop gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal gnome-core

sudo apt-get install vnc4server

 sudo apt-get install tigervnc-common
 
 root@dlp:~# apt -y install novnc websockify python-numpy
 root@dlp:~# cd /etc/ssl 
 root@dlp:/etc/ssl# openssl req -x509 -nodes -newkey rsa:2048 -keyout novnc.pem -out novnc.pem -days 365 
