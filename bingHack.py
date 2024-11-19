from urllib.parse import quote, urlencode
from re import match
import argparse
from time import sleep, time
from bs4 import BeautifulSoup as bs
from threading import Thread
import requests


class Bing:

    # You must be login in and fill your cookie in the following field.
    cookies = {
        "MUIDB": ""
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
        "zhuanlan.zhihu.com", # 知乎专栏
        "www.php.id",
        "stackoverflow.com", #stackoverflow
    ]

    ret_list = []

    def __init__(self, keyword, record_num=1000, global_bing = 0):
        self.keyword = keyword
        self.record_num = int((record_num/10) * 14)
        if global_bing:
            # 国际版内容更全，但必须得挂梯子
            self.bing_domain = "www.bing.com"
        else:
            # 国内版 bing
            self.bing_domain = "cn.bing.com"

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
        # 使用 set 对 list 去重
        try:
            tmp = list(set(self.ret_list))
        except:
            return self.ret_list
        self.ret_list = tmp
        return self.ret_list


    def getPageUrl(self, pn_start):
        url = f"https://{self.bing_domain}/search?q={quote(self.keyword, encoding='utf-8')}&first={str(pn_start)}&rdr=1&FORM=QBRE"
        ans = requests.get(url=url, cookies=self.cookies)
        # ans = requests.get(url=url, )
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
    parser.add_argument("-f", "--full", help='use international Bing engine', action="store_true")
    args = parser.parse_args()
    keyword = args.keyword
    filename = args.output_file
    res_num = args.res_num
    global_bing_flag = args.full

    if not keyword:
        exit("Missing Param: keyword ...")
    if res_num:
        bing = Bing(keyword, int(res_num), global_bing_flag)
    else:
        bing = Bing(keyword, global_bing_flag)
    if bing.cookies['MUIDB'] == "":
        print("【WARNING】: Missing cookies can result in query results that are far less than the actual situation.")
    bing.getPageAllUrl()
    if filename:
        bing.saveAsFile(filename)
        print(f"Total record len: {len(bing.ret_list)}")
    else:
        for i in bing.ret_list:
            print(i)

