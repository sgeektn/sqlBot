import time
import os
from urllib import request
from functions import get_site,append_site_on_file,get_sites,get_number

SQL_ERROR = 1
SIZE_CHANGE = 2

BANNED_KEYWORDS = []


SITES_FILE=os.getenv("SITES_FILE")
BANNED_KEYWORDS_FILE=os.getenv("BANNED_KEYWORDS_FILE")
PRIORITY_FILE=os.getenv("PRIORITY_FILE")
ERROR_FILE=os.getenv("ERROR_FILE")



def valid(link):#
	if link[-1] == '/':
		link = link[:-1]
	BANNED_KEYWORDS = get_sites(
		BANNED_KEYWORDS_FILE)
	queue = get_sites(PRIORITY_FILE) + \
		get_sites(ERROR_FILE)
	banned_ext = [".html", ".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
	# print(link+'\n')
	for ext in banned_ext:
		if link[len(link) - len(ext):] == ext:
			print("NO : extention " + ext + " banned\n")
			return False
	if link[link.find('//') + 2:].find('/') == -1:
		print("NO : site without parameters\n")
		return False
	for keyword in BANNED_KEYWORDS:
		if keyword == '' or keyword == "\n":
			continue
		if keyword[len(keyword) - 1] == '\n':
			keyword = keyword[:len(keyword) - 1]
		if get_domain_name(link).find(keyword) != -1:
			print("NO : " + keyword + "domain banned\n")
			return False
	for keyword in queue:
		if keyword[len(keyword) - 1] == '\n':
			keyword = keyword[:len(keyword) - 1]
		if get_domain_name(link).find(get_domain_name(keyword)) != -1:
			print("NO : " + keyword + "domain already in queue\n")
			return False

	return True




def check_ext_for_injection(url):#
	banned_exts = [".jpg", ".html", ".jpeg", ".png", ".pdf", ");", ".js"]
	for banned_ext in banned_exts:
		if url.find(banned_ext + "?") != -1:
			print("no ext banned")
			return False
		elif url[len(url) - len(banned_ext):] == banned_ext:
			print("no ext banned")
			return False

	return True



def test_char(source, size_of_original):
	keywords = ['mysql', 'syntax']
	for keyword in keywords:
		if source.lower().find(keyword) != -1:
			print(keyword + " keyword found")
			return SQL_ERROR
	if abs(size_of_original - len(source)) > 100:
		print("size change")
		return SIZE_CHANGE
	else:
		print("not vulnerable")
		return False


def test_site(site):#
	if site[-1] == '\n':
		site = site[0:-1]

	sql_chars = ['\'']

	headers = {
		'Referer': 'http://www.google.com/bot.html',
		'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
	}

	try:
		req = request.Request(site, headers=headers)
		response = request.urlopen(req)
		page_source = response.read().decode("utf-8")
		site_len = len(page_source)
	except BaseException:
		print("error opening site")
		return False

	for sql_char in sql_chars:

		result = False
		try:
			req = request.Request(site + sql_char, headers=headers)
			response = request.urlopen(req)
			page_source = response.read().decode("utf-8")
			result = test_char(page_source, site_len)

		except Exception:
			print("error opening site with injection char")

			return False

		if result == SQL_ERROR or result == SIZE_CHANGE:

			return result

	return False


def test_sites():#

	l_sql = []
	l_error = []
	i = 0

	sites_num = get_number(SITES_FILE)


	while True:

		while sites_num == 0:
			print("Waiting for vulnerable sites to come\n" )
			time.sleep(60)
			sites_num = get_number(SITES_FILE)
	
		
		site = get_site(SITES_FILE)
		sites_num = get_number(SITES_FILE)
		if site[len(site) - 1] == '/':
			site = site[0:len(site) - 1]
		i += 1
		print(( "Testing site %s of %s %s" ) % (sites_num, str(i), site))

		if site[-1] == '\n':
			site = site[0:-1]

		if check_ext_for_injection(site) and valid(site):

			res = test_site(site)
			if res == SQL_ERROR:
				print( "sql" )
				l_sql.append(site)
				append_site_on_file(site + "\n",PRIORITY_FILE,)
			elif res == SIZE_CHANGE:
				print( "maybe" )
				l_error.append(site)
				append_site_on_file(site + "\n", ERROR_FILE)
	


	return (l_sql, l_error)







def main():
	exit_err=False
	if BANNED_KEYWORDS_FILE==None:
		print("Error : You need to set BANNED_KEYWORDS_FILE\nTry : export BANNED_KEYWORDS_FILE=\"banned.txt\"")
		exit_err=True
	if PRIORITY_FILE==None:
		print("Error : You need to set PRIORITY_FILE\nTry : export PRIORITY_FILE=\"sqlVulnerable.txt\"")
		exit_err=True
	if ERROR_FILE==None:
		print("Error : You need to set ERROR_FILE\nTry : export ERROR_FILE=\"maybeVulnerable.txt\"")
		exit_err=True
	if SITES_FILE==None:
		print("Error : You need to set SITES_FILE\nTry : export SITES_FILE=\"sites.txt\"")
		exit_err=True

	if exit_err:
		exit(-1)

	if not os.path.isfile(BANNED_KEYWORDS_FILE):
		with open(BANNED_KEYWORDS_FILE,mode="w") as new_file:
			new_file.close() 
	if not os.path.isfile(PRIORITY_FILE):
		with open(PRIORITY_FILE,mode="w") as new_file:
			new_file.close() 
	if not os.path.isfile(ERROR_FILE):
		with open(ERROR_FILE,mode="w") as new_file:
			new_file.close() 
	if not os.path.isfile(SITES_FILE):
		with open(SITES_FILE,mode="w") as new_file:
			new_file.close() 
			
	test_sites()

if __name__ == '__main__':
	if len(sys.argv)==2 and (sys.argv[1]=="-d" or sys.argv[1]=="--daemon") :
		pid=os.fork()
		
		if pid!=0:
			exit(0)		
	print(os.getpid())
	main()
