from urllib.parse import quote
from re import match
import argparse
from bs4 import BeautifulSoup as bs
from threading import Thread
import requests

# You must be login in and add your cookie to the following headers.

class Bing:
    headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": "".encode('utf-8'),
        "Referer": "https://cn.bing.com/search?q=site%3aedu.cn&rdr=1&FPIG=F9E8B1EB09E745598DE4ECA499F51BC3&FPIG=097F1C9E25414FC7ABC61F4299AE7BB7&first=11&FORM=PERE",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers",
    }
    ret_list = []

    def __init__(self, keyword, record_num=1000):
        self.keyword = keyword
        self.record_num = (record_num/10) * 14

    def getPageAllUrl(self):
        threads = []
        i = 1
        while i < self.record_num:
            pn_start = i
            threads.append(Thread(target=self.getPageUrl, args=(pn_start,)))
            i += 14
        for j in threads:
            j.start()
        for j in threads:
            j.join()
        return self.ret_list


    def getPageUrl(self, pn_start):
        url = f"https://cn.bing.com/search?q={quote(self.keyword)}&first={str(pn_start)}&rdr=1&FORM=PERE1"
        ans = requests.get(url=url, headers=self.headers)
        urls = self.htmlParser(ans.text)
        ans.close()
        self.ret_list += urls

    def htmlParser(self, html):
        soup = bs(html, "html.parser")
        # 获取所有存在 href 属性的 a 标签
        raw = soup.find_all("a", href=True)
        res = []
        for i in raw:
            flag = True
            if not match("^https?", i["href"]):
                flag = False
            if flag:
                res.append(i["href"])

        # 取前 20 条记录然后去重
        res = list(set(res[:20]))
        return res

    def saveAsFile(self, filename):
        try:
            f = open(str(filename), "w")
            for i in self.ret_list:
                f.write(i + "\n")
            f.close()
        except:
            exit("文件写入失败!")
        print(f"成功存储为 {filename} 文件!")

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Thanks for using bingHack.py, if there is any problem please contact me: 【Wechat: A2Cai_】 or 【Email: 1149652550@qq.com】")
    parser.add_argument("-k", "--keyword", help='Search keyword for GoogleHack, for example: site:edu.cn&&inurl:.php?id')
    parser.add_argument("-f", "--file", help='Filename for output')
    parser.add_argument("-n", "--res_num", help='Record number for output')
    args = parser.parse_args()
    keyword = args.keyword
    filename = args.file
    res_num = args.res_num
    if not keyword:
        exit("Missing Param: keyword ...")
    if res_num:
        bing = Bing(keyword, int(res_num))
    else:
        bing = Bing(keyword)
    bing.getPageAllUrl()
    if filename:
        bing.saveAsFile(filename)
    else:
        for i in bing.ret_list:
            print(i)
        print(f"Total record len: {len(bing.ret_list)}")




