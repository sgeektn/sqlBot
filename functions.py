import sys

def get_domain_name(link):
	"""Extract domain name from link"""
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

def get_site(file_name):
	"""Get site first from file_name and remove it"""

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



def get_sites(file_name):
	"""Get all sites in file_name"""
	files = open(file_name, "r")
	sites = files.readlines()
	return sites




def get_number(file_name):
	"""Count number of lines in file_name"""
	files = open(file_name, "r")
	sites = files.readlines()
	files.close()
	return len(sites)

def append_sites_on_file(l, file):
	"""Add Sites in l list in file"""
	files = open(file, "a")
	files.writelines('\n'.join(l))
	files.close()


def append_site_on_file(site, file_name):
	"""Add site in file"""
	file = open(file_name, "a")

	file.write('%s' % site)
	file.close()

def myprint(string):
	"""This functino print to stdin if peocess is not daemon else to file"""
	if len(sys.argv)==2 and (sys.argv[1]=="-d" or sys.argv[1]=="--daemon") :
		with open(sys.argv[0]+".txt","a+") as output:
			output.write(str(string)+"\n")
			output.close()
	else:
		print(string)

