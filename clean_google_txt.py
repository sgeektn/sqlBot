import os
  
os.system("wc -l google.txt")
os.system("vi google.txt -c ':g/https*:\/\/[^\/]*\/$/d' -c ':wq!'")
os.system("wc -l google.txt")
