# sqlBot

I-Setup


	1 - pip install -r requirements.txt
	2 - install firefox
	3 - download geckodriver https://github.com/mozilla/geckodriver/releases/tag/v0.26.0
	4 - set geckodriver in PATH
	5 - if you want to use tor , install it
	


II-Bot
	This application is an automated bot for searching sql injection vulnerable sites via sqlmap, all you need to do is to install it , add dorks in a file and launch it 
	it is composed by 5 python scripts :
		1 - getSites.py : will open file specified in DORK_LIST_FILE environement variable and loop all dorks on it
		2 - testSites.py : will test if sites reterived by getSites.py are sql injectable
		3 - exploit.py : will launch sqlmap on each vulnerable site
		4 - recursiveSearch.py : will search sites on the sites reterived by getSites.py with specified deep
		5 - utils.py : utils functions to manipulate bot
		Usage : utils.py action
			action :
				filter : filter results
				clean_sites_file : remove non injectable sites from list
				threads : print all sqlmap threads
				getenv : print all env variables
				clean : clean bot files


III-ENV variables :

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

IV-Usage

	1 first setup ( See I )
	2.a You can launch each service alone by executing the python script and following instruction .
							OR
	2.b.1 Launch command "python3 utils.py setenv" copy the result and execute it or edit the params that you want
	2.b.2 Launch command "python3 getSites.py -d & python3 testSites.py -d & python3 exploit.py -d & python3 recursiveSearch.py -d"
	3. Add dorks or sites to recursiveSearch or sites to exploit 
	4. Enjoy
Please note : if you dont want to detach the threads from terminal and make them stop when you exit terminal or close ssh session juste remove the "-d"'s from 2.b.2