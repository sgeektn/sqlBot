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



branch separateThreads

getSites.py ( get sites from google )
testSites.py ( test if sites in VAR are sql vulnerable )
exploit.py ( test sqlmap)
filter.py ( filter results )
recursiveSearch.py ( activate recursive search )
utils.py ( util functinos )

Usage : utils.py action
	action :
		filter : filter results
		clean_sites_file : remove non injectable sites from list
		threads : print all sqlmap threads
		getenv : print all env variables


ENV variables :

RECURSIVE_SITES_FILE : file where are stored the sites to do recursive search
RECUSIVE_SEARCH : recursive search deep ( 0 for disable )
SITES_FILE : file where are stored sites to be tested if there are sql injectable
BANNED_KEYWORDS_FILE : file where will be stored each failed injection site that will be banned after 5 attempts
DORK_LIST_FILE : file where stored dorks to be searched from google
ANTI_CAPTCHA_API_KEY : API KEY FOR ANTI-CAPTCHA.com to bypass google captcha ( set to DISABLED if you want to manually do the captcha )
TOR : if you want to make sqlmap request with tor set to "True" else set to "False"
MAX_THREADS : number of parallel sqlmap threads
PRIORITY_FILE : sites that explicitly shows sql error 
ERROR_FILE : sites that change content when bot tries to test sql injection

You can set all the variables by executing the command that will be printed if you execute:
python3 utils.py setenv

