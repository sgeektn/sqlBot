import os
import sys
from extractSites import FIREFOX_DRIVER,PRIORITY_FILE , ERROR_FILE,SITES_FILE,DORK_LIST_FILE ,BANNED_KEYWORDS_FILE ,RECURSIVE_SITES_FILE, BANNING_FILE,SQLMAP_PATH


tor=False
vnc=False
clean_bot=False

if sys.argv.index("--vnc") != -1:
	vnc=True
if sys.argv.index("--tor") != -1:
	tor=True
if sys.argv.index("--clean") != -1:
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
    os.system("apt install python3-pip")
    os.system("pip3 install selenium")
    os.system("apt install python")

    os.system("echo \"alias clean='python3 clean.py'\" >> ~/.bashrc ")
    os.system("echo \"alias filter='zeb ; python3 extractSites.py filter'\" >> ~/.bashrc ")
    os.system("echo \"alias lss='ls -lia'\" >> ~/.bashrc ")
    if vnc:
    	os.system("echo \"alias revnc='vncserver -kill :1 ; vncserver ; webvnc'\" >> ~/.bashrc ")
    os.system("echo \"alias sites='ps aux | grep sqlmap | sed -E \'/sh -c/d\' | sed -E \'/grep/d\' '\" >> ~/.bashrc ")
    if vnc:
    	os.system("echo \"alias webvnc='websockify -D --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 6080 localhost:5901'\" >> ~/.bashrc ")
    os.system("echo \"alias zeb='cd /root/Desktop/sqlBot'\" >> ~/.bashrc ")
    os.system("echo \"export PATH=$PATH:\"%s >> ~/.bashrc " %(FIREFOX_DRIVER,))
    os.system("touch " +PRIORITY_FILE +" " +ERROR_FILE +" " +SITES_FILE +" " +DORK_LIST_FILE +" " +BANNED_KEYWORDS_FILE +" " +RECURSIVE_SITES_FILE +" " +BANNING_FILE)
    if vnc:
    	os.system("apt -y install vnc4server")
    	os.system("vncpasswd")
    	os.system("apt -y install novnc websockify python-numpy")
    	os.system("/etc/ssl/openssl req -x509 -nodes -newkey rsa:2048 -keyout novnc.pem -out novnc.pem -days 365")
    	os.system("vncserver -kill :1 ; vncserver")
    	os.system("websockify -D --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 6080 localhost:5901")


if __name__ == '__main__':
	if clean_bot:
		clean()
	setup()