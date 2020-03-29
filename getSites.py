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



DORK_LIST_FILE=os.getenv("DORK_LIST_FILE")
SITES_FILE=os.getenv("SITES_FILE")
RECURSIVE_SITES_FILE=os.getenv("RECURSIVE_SITES_FILE")



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
	append_sites_on_file(liste, SITES_FILE)
	append_sites_on_file(liste,RECURSIVE_SITES_FILE)
	browser.close()

def append_sites_on_file(l, file):
	files = open(file, "a")
	files.writelines('\n'.join(l))
	files.close()

def append_site_on_file(site, file_name):
	file = open(file_name, "a")
	file.write('%s' % site)
	file.close()

def get_sites(file_name):
	files = open(file_name, "r")
	sites = files.readlines()
	return sites

def get_site(file_name):
	files = open(file_name, "r")
	sites = files.readlines()
	files.close()
	site = sites[0]
	del sites[0]

	files = open(file_name, "w")
	if len(sites) > 0:
		files.writelines(sites)
	files.close()
	return site

def get_sites_by_dork(dork):
	dork = dork.replace('&', '%26')
	dork = dork.replace(' ', '+')
	extract_sites(dork)

def get_number(file_name):
	files = open(file_name, "r")
	sites = files.readlines()
	files.close()
	return len(sites)

def main():

	

	if DORK_LIST_FILE==None:
		print("Error : You need to set DORK_LIST_FILE\nTry : export DORK_LIST_FILE=\"dorks.txt\"")
		exit_err=True
	if SITES_FILE==None:
		print("Error : You need to set SITES_FILE\nTry : export SITES_FILE=\"sites.txt\"")
		exit_err=True
	if RECURSIVE_SITES_FILE==None:
		print("Error : You need to set RECURSIVE_SITES_FILE\nTry : export RECURSIVE_SITES_FILE=\"googleRecursive.txt\"")
		exit_err=True
	try:
		test_selenium=webdriver.Firefox()
		test_selenium.close()
	except selenium.common.exceptions.WebDriverException:
		print("Error : Firefox Selenium driver needs to be in path")
		exit_err=True
		pass

	if exit_err:
		exit(-1)
		

	dorks_number = get_number(DORK_LIST_FILE)
	while dorks_number == 0:
		print("Waiting for new dorks")
		time.sleep(60)
		dorks_number = get_number(DORK_LIST_FILE)
	while dorks_number > 0:
		dork = get_site(DORK_LIST_FILE)
		get_sites_by_dork(dork)
		dorks_number = get_number(DORK_LIST_FILE)
		while dorks_number == 0:
			print("Waiting for new dorks")
			time.sleep(60)
			dorks_number = get_number(DORK_LIST_FILE)
	print("End get dorks")



if __name__ == '__main__':
	main()
