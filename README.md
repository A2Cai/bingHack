

### Usage:

`python bingHack.py [-h] [-k KEYWORD] [-o OUTPUT_FILE] [-n RES_NUM] [-f] [-c COOKIE]`

>  Thanks for using bingHack.py, if there is any problem please contact me: 
>
>  **Wechat**:  A2Cai_
>
>  **Email**:  1149652550@qq.com

1. GoogleHack + asset survival detect

`python bingHack/bingHack.py -k "intitle:公司 && inurl:.php?id" -n 2000 | python HRU/HRU.py -p -s`

2. Read from file and display the results on console

`python bingHack.py -k "site:edu.cn" -n 2000`

3. Read from file and save the results as a file

`python bingHack.py -k "site:edu.cn" -n 2000 -o result.txt`

### Options:

` -h, --help`     show this help message and exit

`-k KEYWORD, --keyword KEYWORD`

​	Search keyword for GoogleHack, for example: site:edu.cn&&inurl:.php?id

`-o OUTPUT_FILE, --output-file OUTPUT_FILE`	 Filename for output

`-n RES_NUM, --res_num RES_NUM` 	Record number for output

`-f, --full`         use international Bing engine - more precise queries

`-c COOKIE, --cookie COOKIE`		config cookie by param

### Question

1. Why am I querying far less data than the actual amount ?

> Log in to Bing and paste the MUIDB value from the cookie into the script.
