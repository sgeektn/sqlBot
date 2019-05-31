import os
  
os.system("wc -l google.txt")
os.system("vi google.txt -c ':g/https*:\/\/[^\/]*\/$/d'  - c':wq!'")

#with open("banned.txt","r") as bannedFile:
#	for site in bannedFile.readlines():
#		if(site[-1]=='\n'):
#			site=site[:-1]
#		if(site!="\n" and site !=""):
#			os.system("vi google.txt  -c 'g/%s/d' -c ':wq' "%site)
#	bannedFile.close()
os.system("wc -l google.txt")
