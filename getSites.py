import time
import os
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from functions import get_site,get_number,append_sites_on_file,myprint
import sys

DORK_LIST_FILE=os.getenv("DORK_LIST_FILE")
SITES_FILE=os.getenv("SITES_FILE")
RECURSIVE_SITES_FILE=os.getenv("RECURSIVE_SITES_FILE")
ANTI_CAPTCHA_API_KEY=os.getenv("ANTI_CAPTCHA_API_KEY")
ANTI_CAPTCHA_RESPONSE_FILE=os.getenv("ANTI_CAPTCHA_RESPONSE_FILE")

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
			myprint("Network error")
		except BaseException:
			browser.close()
			browser = webdriver.Firefox()
			browser.get(url)
			source = browser.page_source.find('g-recaptcha-response')

		while source != -1:
			if ANTI_CAPTCHA_API_KEY=="DISABLED":
				myprint("You need to solve a captcha and add the response hash to "+ANTI_CAPTCHA_RESPONSE_FILE+" file")
				ANTI_CAPTCHA_RESPONSE=None
				while(ANTI_CAPTCHA_RESPONSE==None):
					with open(ANTI_CAPTCHA_RESPONSE_FILE,"r") as captcha_file:
						ANTI_CAPTCHA_RESPONSE=captcha_file.read()
						captcha_file.close()
					if ANTI_CAPTCHA_RESPONSE=="":
						ANTI_CAPTCHA_RESPONSE=None
					myprint("Waiting for captcha hash")
					time.sleep(30)
				#RESET FILE
				with open(ANTI_CAPTCHA_RESPONSE_FILE,"w") as captcha_file:
					captcha_file.close()
				ANTI_CAPTCHA_RESPONSE=None
			else:
				myprint("Auto solving captcha")
				api_key = ANTI_CAPTCHA_API_KEY
				site_key = browser.find_element_by_id("recaptcha").get_attribute("data-sitekey")
				url = 'https://www.google.com'
				client = AnticaptchaClient(api_key)
				task = NoCaptchaTaskProxylessTask(url, site_key)
				job = client.createTask(task)
				job.join()
				ANTI_CAPTCHA_RESPONSE = job.get_solution_response()
			browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML="'+ANTI_CAPTCHA_RESPONSE+'"')
			browser.execute_script('document.getElementById("captcha-form").submit()')
			myprint("captcha ok")
			time.sleep(60)
			try:
				source = browser.page_source.find('g-recaptcha-response')
			except TimeoutException:
				myprint("Network error")
			except NoSuchWindowException:
				browser.close()
				browser = webdriver.Firefox()
				browser.get(url)
				source = browser.page_source.find('g-recaptcha-response')

		else:
			for site in browser.find_elements_by_class_name('r'):
				try:
					link = site.find_element_by_tag_name(
						'a').get_attribute('href')
				except BaseException:
					link = "https://www.google.fr/"
				if link[len(link) - 1] == '/':
					link = link[0:len(link) - 1]
				# GET SITES ON SITE

				liste.append(link)

			results = len(browser.find_elements_by_class_name('r'))
			page += 10

	myprint("%s sites extracted \n" % str(len(liste)))
	append_sites_on_file(liste, SITES_FILE)
	append_sites_on_file(liste,RECURSIVE_SITES_FILE)
	browser.close()




def get_sites_by_dork(dork):
	dork = dork.replace('&', '%26')
	dork = dork.replace(' ', '+')
	extract_sites(dork)


	return len(sites)

def main():

	
	exit_err=False
	if DORK_LIST_FILE==None:
		myprint("Error : You need to set DORK_LIST_FILE\nTry : export DORK_LIST_FILE=\"dorks.txt\"")
		exit_err=True
	if SITES_FILE==None:
		myprint("Error : You need to set SITES_FILE\nTry : export SITES_FILE=\"sites.txt\"")
		exit_err=True
	if RECURSIVE_SITES_FILE==None:
		myprint("Error : You need to set RECURSIVE_SITES_FILE\nTry : export RECURSIVE_SITES_FILE=\"googleRecursive.txt\"")
		exit_err=True
	if ANTI_CAPTCHA_API_KEY==None:
		myprint("Error : You need to set ANTI_CAPTCHA_API_KEY\nTry : export ANTI_CAPTCHA_API_KEY=\"DISABLED\"")
		exit_err=True
	if ANTI_CAPTCHA_API_KEY=="DISABLED" and ANTI_CAPTCHA_RESPONSE_FILE==None:
		myprint("Error : You need to set ANTI_CAPTCHA_RESPONSE_FILE\nTry : export ANTI_CAPTCHA_RESPONSE_FILE=\"captcha.txt\"")
		exit_err=True

	if exit_err:
		exit(-1)
		
	if ANTI_CAPTCHA_RESPONSE_FILE!=None and not os.path.isfile(ANTI_CAPTCHA_RESPONSE_FILE):
		with open(ANTI_CAPTCHA_RESPONSE_FILE,mode="w") as new_file:
			new_file.close() 
	if not os.path.isfile(DORK_LIST_FILE):
		with open(DORK_LIST_FILE,mode="w") as new_file:
			new_file.close() 

	if not os.path.isfile(SITES_FILE):
		with open(SITES_FILE,mode="w") as new_file:
			new_file.close() 

	if not os.path.isfile(RECURSIVE_SITES_FILE):
		with open(RECURSIVE_SITES_FILE,mode="w") as new_file:
			new_file.close() 


	try:
		test_selenium=webdriver.Firefox()
		test_selenium.close()
	except selenium.common.exceptions.WebDriverException:
		myprint("Error : Firefox Selenium driver needs to be in path")
		exit_err=True



	dorks_number = get_number(DORK_LIST_FILE)
	while dorks_number == 0:
		myprint("Waiting for new dorks")
		time.sleep(60)
		dorks_number = get_number(DORK_LIST_FILE)
	while dorks_number > 0:
		dork = get_site(DORK_LIST_FILE)
		get_sites_by_dork(dork)
		dorks_number = get_number(DORK_LIST_FILE)
		while dorks_number == 0:
			myprint("Waiting for new dorks")
			time.sleep(60)
			dorks_number = get_number(DORK_LIST_FILE)
	myprint("End get dorks")



if __name__ == '__main__':
	if len(sys.argv)==2 and (sys.argv[1]=="-d" or sys.argv[1]=="--daemon") :
		pid=os.fork()
		
		if pid!=0:
			exit(0)		
	myprint(os.getpid())
	main()
