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
#from config import PRIORITY_FILE,ERROR_FILE,SITES_FILE,DORK_LIST_FILE,RECURSIVE_SITES_FILE,SQLMAP_PATH,FIREFOX_DRIVER,BANNING_FILE,BANNED_KEYWORDS_FILE


FALSE = 0
SQL_ERROR = 1
SIZE_CHANGE = 2

BANNED_KEYWORDS = []


SITES_FILE=os.getenv("SITES_FILE")
BANNED_KEYWORDS_FILE=os.getenv("BANNED_KEYWORDS_FILE")
PRIORITY_FILE=os.getenv("BANNED_KEYWORDS_FILE")
ERROR_FILE=os.getenv("ERROR_FILE")


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


def check_ext(url):
	banned_exts = [".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
	for banned_ext in banned_exts:
		if url.find(banned_ext + "?") != -1:

			return False
		elif url[len(url) - len(banned_ext):] == banned_ext:

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




def append_site_on_file(site, file_name):#

	#while lock:
	#	print("waiting for %s To be Unlocked" % (file))
	#lock = True

	file = open(file_name, "a")

	file.write('%s' % site)
	file.close()

	#lock = False

def get_sites(file_name):
	files = open(file_name, "r")
	sites = files.readlines()
	return sites

def get_site(file_name):#

	#while lock:
	#	print("waiting for %s To be Unlocked" % (file_name))
	#lock = True

	files = open(file_name, "r")
	sites = files.readlines()
	files.close()
	site = sites[0]
	del sites[0]

	files = open(file_name, "w")
	if len(sites) > 0:
		files.writelines(sites)
	files.close()

	#lock = False

	return site



def get_number(file_name):#

	files = open(file_name, "r")
	sites = files.readlines()
	files.close()

	#lock = False

	return len(sites)



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
	test_sites()

if __name__ == '__main__':
	main()