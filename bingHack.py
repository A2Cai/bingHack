from random import randint
from urllib.parse import quote, urlencode
from re import match
import argparse
from time import sleep, time
from bs4 import BeautifulSoup as bs
from threading import Thread
import requests

class Bing:

    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:130.0) Gecko/20010101 Firefox/130.0",
        "Mozilla/5.0 (Windows NT 6.3; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Windows NT 6.3; Win64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Windows NT 6.2; WOW64; x64; rv:132.0) Gecko/20010101 Firefox/132.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.59 Safari/537.36"
    ]



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
    # 分割每组查询的最大页数
    GROUP_SPLIT_NUM = 20

    def __init__(self, keyword, record_num=1000, global_bing = 0, log_status = 0):
        self.keyword = keyword
        self.record_num = record_num
        self.page_num = int((record_num/10))
        self.log_status = log_status
        if global_bing:
            # 国际版内容更全，但必须得挂梯子
            self.bing_domain = "www.bing.com"
        else:
            # 国内版 bing
            self.bing_domain = "cn.bing.com"

    def getPageAllUrl(self):
        threads = []
        t_list = []
        i = 1
        while i <= self.record_num:
            pn_start = i
            threads.append(Thread(target=self.getPageUrl, args=(pn_start,)))
            i += 10
        # 当要查询的记录太大时(大于GROUP_SPLIT_NUM页),会将其分割成多组依次查询
        if self.page_num > self.GROUP_SPLIT_NUM:
            max = self.page_num / self.GROUP_SPLIT_NUM if self.page_num % self.GROUP_SPLIT_NUM == 0 else self.page_num / self.GROUP_SPLIT_NUM + 1
            for i in range(int(max)):
                tmp = []
                for j in range(i*self.GROUP_SPLIT_NUM, (i+1)*self.GROUP_SPLIT_NUM):
                    tmp.append(threads[j])
                t_list.append(tmp)

            # 开始计时
            self.start_time = int(time())
            for index, group in enumerate(t_list):
                for thread in group:
                    thread.start()
                for thread in group:
                    thread.join()
                self.showMessage(f"--> {index + 1} Group finished...")
                if index == len(t_list)-1:
                    self.showMessage(f"--> Final Group finished...")
                    # 结束计时
                    self.end_time = int(time())
                    # 使用 set 对 list 去重
                    if len(self.ret_list) < 2 ** 31:
                        self.ret_list = list(set(self.ret_list))
                    return self.ret_list
                # 以免连接太多 Bing 拒绝连接
                sleep(5)
        # 开始计时
        self.start_time = int(time())
        for j in threads:
            j.start()
        for j in threads:
            j.join()
        # 结束计时
        self.end_time = int(time())
        # 使用 set 对 list 去重
        if len(self.ret_list) < 2**31:
            self.ret_list = list(set(self.ret_list))
        return self.ret_list


    def getPageUrl(self, pn_start):
        url = f"https://{self.bing_domain}/search?q={quote(self.keyword, encoding='utf-8')}&first={str(pn_start)}&rdr=1&FORM=QBRE"
        headers = {
            'User-Agent': self.ua_list[randint(0, len(self.ua_list) - 1)],
            "Referer": url,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br, zstd"
        }
        ans = requests.get(url=url, cookies=self.cookies, headers=headers)
        urls = self.htmlParser(ans.text)
        ans.close()
        self.ret_list += urls

    def htmlParser(self, html):
        soup = bs(html, "html.parser")
        # 获取所有存在 href 属性的 a 标签
        raw = soup.find_all("a", attrs={"href":True})
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

    def showMessage(self, message):
        if self.log_status:
            print(message)

    def showResult(self):
        for i in self.ret_list:
            print(i)
        self.showMessage(f"--> Total time consumed: {self.end_time - self.start_time}s")
        self.showMessage(f"--> Total record num: {len(self.ret_list)}")


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Thanks for using bingHack.py, if there is any problem please contact me: 【Wechat: A2Cai_】 or 【Email: 1149652550@qq.com】")
    parser.add_argument("-k", "--keyword", help='Search keyword for GoogleHack, for example: site:edu.cn&&inurl:.php?id')
    parser.add_argument("-o", "--output-file", help='Filename for output')
    parser.add_argument("-n", "--res_num", help='Record number for output')
    parser.add_argument("-f", "--full", help='use international Bing engine', action="store_true")
    parser.add_argument("-c", "--cookie", help='config cookie by param')
    parser.add_argument("-v", "--show-info", help='show info', action="store_true")
    parser.add_argument("-s", "--show-result", help='display result on console', action="store_true")

    args = parser.parse_args()
    keyword = args.keyword
    filename = args.output_file
    res_num = args.res_num
    global_bing_flag = args.full
    cookie = args.cookie
    is_show_info = args.show_info
    is_show_result = args.show_result

    if not keyword:
        exit("Missing Param: keyword ...")
    if res_num:
        bing = Bing(keyword, int(res_num), global_bing_flag, is_show_info)
    else:
        bing = Bing(keyword=keyword, global_bing=global_bing_flag, log_status=is_show_info)

    # 设置 Cookie 为必填项
    if bing.cookies['MUIDB'] == "" and not cookie:
        print("【WARNING】: Missing cookies can result in query results that are far less than the actual situation.")
    elif cookie:
        bing.cookies['MUIDB'] = cookie

    bing.getPageAllUrl()

    # 将结果存储为文件还是直接展示在终端
    if filename:
        bing.saveAsFile(filename)
        print(f"Total record len: {len(bing.ret_list)}")
    else:
        bing.showResult()

