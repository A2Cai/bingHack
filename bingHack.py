from urllib.parse import quote
from re import match
import argparse
from time import sleep, time
from bs4 import BeautifulSoup as bs
from threading import Thread
import requests

# You must be login in and add your cookie to the following headers.

class Bing:
    headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": "MUID=154B90D1D66E62A918858468D7086389; MUIDB=154B90D1D66E62A918858468D7086389; _EDGE_V=1; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=CDA807A26A95424692D8749737E01331&dmnchg=1; SRCHUSR=DOB=20240711&T=1731989518000&POEX=W; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=W&BRH=S&CW=1450&CH=283&SCW=1451&SCH=283&DPR=1.8&UTC=480&DM=1&HV=1731989521&WTS=63867456131&PRVCW=1450&PRVCH=774&EXLTT=31&THEME=0&WEBTHEME=0&IG=0FE015E15FAE490281830F8B1047537A&AV=14&ADV=14&RB=0&MB=0; _HPVN=CS=eyJQbiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI…DumCFYqvpJ0Ogqv9fdDiMo=; MUIDB=154B90D1D66E62A918858468D7086389; MSCC=cid=hh836iobn99x4y31rf5i5eps-c1=2-c2=2-c3=2; SnrOvr=X=rebateson; SNRHOP=I=&TS=; _EDGE_S=SID=300F3830F0A366D232842D0CF1E06747; WLS=C=8f125643d0c6b11f&N=%e6%95%8c; _SS=SID=300F3830F0A366D232842D0CF1E06747&R=1379&RB=1379&GB=0&RG=1800&RP=1379; ipv6=hit=1731993120232&t=4; _C_ETH=1; _Rwho=u=d&ts=2024-11-19; MicrosoftApplicationsTelemetryDeviceId=2514d39b-b0d2-43f2-aba1-375699cd1ad8; ai_session=IT2xoMqxiD9kEvlBw6KsOG|1731989523362|1731989523362".encode("utf-8").decode("unicode_escape"),
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

    # 可以添加不需要收集的域名
    block_domain_list = [
        "go.microsoft.com",
        "support.microsoft.com",
        "dxzhgl.miit.gov.cn",
        "www.beian.gov.cn",
        "beian.miit.gov.cn",
        "www.cnblogs.com", # 博客园
        "blog.csdn.net", # CSDN
        "baike.baidu.com", # 百度百科
        "www.freebuf.com", # FreeBuf
        "www.exploit-db.com", # exploit-db
        "github.com", # github
        "www.php.net", # php 官网
        "www.php.cn", # php 中文网
    ]

    ret_list = []

    def __init__(self, keyword, record_num=1000):
        self.keyword = keyword
        self.record_num = int((record_num/10) * 14)

    def getPageAllUrl(self):
        threads = []
        t_list = []
        tmp = []
        i = 1
        while i < self.record_num:
            pn_start = i
            threads.append(Thread(target=self.getPageUrl, args=(pn_start,)))
            i += 14
        # 当要查询的记录太大时(大于100页),会将其分割成多组依次查询
        if len(threads) > 100:
            max = len(threads) / 100 if len(threads) % 100 == 0 else len(threads) / 100 + 1
            for i in range(int(max)):
                tmp = []
                for j in range(i*100, (i+1)*100):
                    tmp.append(threads[j])
                t_list.append(tmp)
            start_time = int(time())
            for index, group in enumerate(t_list):
                for thread in group:
                    thread.start()
                for thread in group:
                    thread.join()
                if index == len(t_list)-1:
                    print(f"使用的时间: {int(time()) - start_time}s")
                    return self.ret_list
                print(f"{index+1} Group Finished~")
                # 以免连接太多 Bing 拒绝连接
                sleep(5)
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
            for block_rule in self.block_domain_list:
                if match(f"^https?:\/\/{block_rule}", i["href"]):
                    flag = False
                    break
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
    parser.add_argument("-o", "--output-file", help='Filename for output')
    parser.add_argument("-n", "--res_num", help='Record number for output')
    args = parser.parse_args()
    keyword = args.keyword
    filename = args.output_file
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

