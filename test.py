from bs4 import BeautifulSoup  #网页解析，获取数据
import re  #正则表达式，进行文字匹配
import urllib.request, urllib.error  #制定URL，获取网页数据
import xlwt  #进行excel操作
import sqlite3  #进行SQLite数据库操作
import xlrd  #excel read
Find_Title = re.compile(r'target="_blank">(.*?)</a>')
Find_Link = re.compile(r'href="(.*?)" target="_blank">')

Find_Img_Link = re.compile(r'src="(.*?)"')
Find_Essay = re.compile(r'<p>(.*?)</p>')

Find_Date = re.compile(r'<span class="date">(.*?)</span>')


def getWeb():
    data = []
    url = "https://news.sina.com.cn/gov/xlxw/2020-11-13/doc-iiznezxs1689187.shtml"

    html = askURL(url)
    # print(html, '\n\n\n\n')
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all('span', class_="date"):  #查找符合要求的字符串，形成列
        #测试：查看电影item全部信息
        item = str(item)
        # print(item)

        #print(item, '\n\n')
        #得到img链接
        time = re.findall(Find_Date, item)
        print(time)
        # data.append(imglink[0])
        # if data != []:
        #     break

    # print(data)

    return data


def askURL(url):
    head = {  #模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent":
        "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    #用户代理，表示告诉豆瓣服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


getWeb()
