import os
import sys
from config import PRIORITY_FILE,ERROR_FILE,SITES_FILE,DORK_LIST_FILE,RECURSIVE_SITES_FILE,SQLMAP_PATH,FIREFOX_DRIVER,BANNING_FILE,BANNED_KEYWORDS_FILE



tor=False
vnc=False
clean_bot=False

if "--vnc" in sys.argv :
	vnc=True
if "--tor" in sys.argv :
	tor=True
if "--clean" in sys.argv :
	clean_bot=True


def clean():
	os.system("touch " +PRIORITY_FILE +" " +ERROR_FILE +" " +SITES_FILE +" " +DORK_LIST_FILE  +" " +RECURSIVE_SITES_FILE)
	os.system("rm -rf working finished dbs maybe")
	os.system("rm -rf " + SQLMAP_PATH + "/sqlmap")

def setup():
	try:
		os.makedirs(SQLMAP_PATH + "/sqlmap")
	except BaseException:
		pass
	os.system('git clone https://github.com/sqlmapproject/sqlmap.git ' + SQLMAP_PATH + "/sqlmap")
	try:
		os.makedirs("dbs")
	except BaseException:
		pass
	try:
		os.makedirs("maybe")
	except BaseException:
		pass
	os.system("apt -y install python3-pip")
	os.system("pip3 install selenium")
	os.system("apt -y install python")
	os.system("echo \"alias clean='python3 clean.py'\" >> ~/.bashrc ")
	os.system("echo \"alias filter='zeb ; python3 extractSites.py filter'\" >> ~/.bashrc ")
	os.system("echo \"alias lss='ls -lia'\" >> ~/.bashrc ")	
	os.system("echo \"alias sites='zeb; python3 extractSites.py filter") 
	os.system("echo \"alias zeb='cd /root/sqlBot'\" >> ~/.bashrc ")
	os.system("echo \"export PATH=$PATH:\"%s >> ~/.bashrc " %(FIREFOX_DRIVER,))
	os.system("touch " +PRIORITY_FILE +" " +ERROR_FILE +" " +SITES_FILE +" " +DORK_LIST_FILE +" " +BANNED_KEYWORDS_FILE +" " +RECURSIVE_SITES_FILE +" " +BANNING_FILE)
	if vnc:
		os.system("apt -y install firefox")
		os.system("apt -y install vnc4server")
		os.system("apt -y install xfce4 xfce4-goodies")
		os.system("apt install -y tightvncserver")
		os.system("apt -y install tigervnc-common")
		os.system("apt-get -y install dbus-x11")
		os.system("apt -y install novnc websockify python-numpy")
		os.system("openssl req -x509 -nodes -newkey rsa:2048 -keyout novnc.pem -out /etc/ssl/novnc.pem -days 365")
		os.system("chmod 644 /etc/ssl/novnc.pem")
		os.system("vncserver -kill :1 ; vncserver")
		os.system("websockify -D --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 6080 localhost:5901")
		os.system("echo \"alias webvnc='websockify -D --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 6080 localhost:5901'\" >> ~/.bashrc ")
		os.system("echo \"alias revnc='vncserver -kill :1 ; vncserver ; webvnc'\" >> ~/.bashrc ")
	if tor:
		os.system("apt -y install tor")
	os.system("source ~/.bashrc")


if __name__ == '__main__':
	if len(sys.argv) > 4 : 
		exit(0)
	if clean_bot:
		clean()
	setup()




