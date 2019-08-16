# sqlBot

I-Setup


	python3 setup.py
	arguments --vnc : to setup the bot in a vps ( adding vnc server that connects in web browser )
			  --tor : to setup tor with the bot
			  --clean : to clean before setting up ( for now just remove files , TODO later uninstall dependencies )


II-Bot
	python3 extractSites.py
	arguments --tor : to make the google search and sqlmap work with tor
			  --rc N : to configure recursive search ( if not defined rc will be 0 )
			  --threads N : to configure sqlmap parralel threads ( if not defined thrads will be 1)
	python3 extractSites.py filter ( or only filter )
			  filter the results and make all sqlmap commands to mannually execute in [PATH]/dbs/* , 
			  sites that are vulnerable but cannot extract dbs in [PATH]/maybe/*
			  remove others and puts them in banning ia ( site will be banned after 5 tests )
	python3 extractSites.py sites  ( or only sites )
		      get sites that are in sqlmap threads


#obsolete

Install vnc like this :

sudo apt-get install --no-install-recommends ubuntu-desktop gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal gnome-core

sudo apt-get install vnc4server

 sudo apt-get install tigervnc-common
 
 root@dlp:~# apt -y install novnc websockify python-numpy
 root@dlp:~# cd /etc/ssl 
 root@dlp:/etc/ssl# openssl req -x509 -nodes -newkey rsa:2048 -keyout novnc.pem -out novnc.pem -days 365 
