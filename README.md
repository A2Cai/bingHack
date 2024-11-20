

### Usage:

`python bingHack.py [-h] [-k KEYWORD] [-o OUTPUT_FILE] [-n RES_NUM] [-f] [-c COOKIE] [-v] [-s]`

>  Thanks for using bingHack.py, if there is any problem please contact me: 
>
>  **Wechat**:  A2Cai_
>
>  **Email**:  1149652550@qq.com

1. GoogleHack + asset survival detect

`python bingHack/bingHack.py -k "intitle:公司 && inurl:.php?id" -n 2000 -s | python HRU/HRU.py -p -s`

2. Read from file and display the results on console

`python bingHack.py -k "site:edu.cn" -n 2000 -s -v`

3. Read from file and save the results as a file

`python bingHack.py -k "site:edu.cn" -n 2000 -o result.txt -v` 

### Options:

` -h, --help`     show this help message and exit

`-k KEYWORD, --keyword KEYWORD`

​	Search keyword for GoogleHack, for example: site:edu.cn&&inurl:.php?id

`-o OUTPUT_FILE, --output-file OUTPUT_FILE`	 Filename for output

`-n RES_NUM, --res_num RES_NUM` 	Record number for output

`-f, --full`         use international Bing engine - more precise queries

`-c COOKIE, --cookie COOKIE`		config cookie by param

`-v, --show-info`      	 show info

`-s, --show-result`     	display result on console

### Question

1. Why am I querying far less data than the actual amount ?

> Depend on Bing and your network...In other words, Bing has its own Search API, so I estimate that it will impose certain restrictions on my scripts. However, so far I have not found any patterns regarding these restrictions, so my scripts are not stable. Sometimes they produce satisfactory results, and sometimes they may have nothing at all
