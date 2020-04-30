import os


SITES_FILE=os.getenv("SITES_FILE")

def main():


	if SITES_FILE==None:
		print("Error : You need to set SITES_FILE\nTry : export SITES_FILE=\"sites.txt\"")
		exit_err=True

	if not os.path.isfile(SITES_FILE):
		with open(SITES_FILE,mode="w") as new_file:
			new_file.close() 

	os.system("wc -l "+SITES_FILE)
	os.system("vi "+SITES_FILE+" -c ':g/https*:\/\/[^\/]*\/$/d' -c ':wq!'")
	os.system("wc -l "+SITES_FILE)


if __name__ == '__main__':
	main()