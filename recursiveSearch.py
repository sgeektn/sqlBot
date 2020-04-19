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


RECURSIVE_SITES_FILE=os.getenv("RECURSIVE_SITES_FILE")
RECUSIVE_SEARCH=os.getenv("RECUSIVE_SEARCH")

def get_domain_name(link):#
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


def check_ext(url):#
	banned_exts = [".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
	for banned_ext in banned_exts:
		if url.find(banned_ext + "?") != -1:

			return False
		elif url[len(url) - len(banned_ext):] == banned_ext:

			return False
	return True



def get_recursive_urls(link, recurive_search):#
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
	append_sites_on_file(urls_filtered, SITES_FILE)

	for url in urls_filtered:
		get_recursive_urls(url, recurive_search - 1)




def append_sites_on_file(l, file):#

	#while lock:
	#	print("Waiting for %s To be unlocked" % (file))
	#lock = True

	files = open(file, "a")

	files.writelines('\n'.join(l))
	files.close()

	#lock = False






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

	#while lock:
	#	print("waiting for %d To be Unlocked" % (file_name))
	#lock = True
#
	files = open(file_name, "r")
	sites = files.readlines()
	files.close()

	#lock = False

	return len(sites)


def recursive_search(number):

	print("recurive_search")
	#ready_to_check_number = get_number(SITES_FILE)
	sites_number = get_number(RECURSIVE_SITES_FILE)
	while sites_number == 0:
		print("Waiting for new sites for recursive_search")
		time.sleep(60)
		sites_number = get_number(RECURSIVE_SITES_FILE)
#	while ready_to_check_number > 1000:
#		print("proirity to readyToCheck_sites")
#		time.sleep(60)
#		ready_to_check_number = get_number(SITES_FILE)

	while sites_number > 0:

		link = get_site(RECURSIVE_SITES_FILE)

		get_recursive_urls(link, number)

#		ready_to_check_number = get_number(SITES_FILE)
		sites_number = get_number(RECURSIVE_SITES_FILE)

		while sites_number == 0:
			print("Waiting for new sites for recursive_search")
			time.sleep(60)
			sites_number = get_number(RECURSIVE_SITES_FILE)
#		while ready_to_check_number > 1000:
#			print("proirity to readyToCheck_sites")
#			time.sleep(60)
#			ready_to_check_number = get_number(SITES_FILE)

	print("end recurive_search")


def main():
	exit_err=False
	RECUSIVE_SEARCH=os.getenv("RECUSIVE_SEARCH")
	if RECUSIVE_SEARCH==None:
		print("Error : You need to set RECUSIVE_SEARCH\nTry : export RECUSIVE_SEARCH=\"0\"")
		exit_err=True
	elif RECUSIVE_SEARCH=="0":
		print("Error : You need to set RECUSIVE_SEARCH > 0")
	else:
		RECUSIVE_SEARCH=int(RECUSIVE_SEARCH)
	if RECURSIVE_SITES_FILE==None:
		print("Error : You need to set RECURSIVE_SITES_FILE\nTry : export RECURSIVE_SITES_FILE=\"googleRecursive.txt\"")
		exit_err=True
	
	if exit_err:
		exit(-1)
	recursive_search(RECUSIVE_SEARCH)

if __name__ == '__main__':
	main()
