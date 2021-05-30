#-*- codeing = utf-8 -*-
#@Time : 2020/3/3 17:51
#@Author : 李巍
#@File : spider.py
#@Software: PyCharm

from bs4 import BeautifulSoup  #网页解析，获取数据
import re  #正则表达式，进行文字匹配
import urllib.request, urllib.error  #制定URL，获取网页数据
import xlwt  #进行excel操作
import sqlite3  #进行SQLite数据库操作
import xlrd  #excel read
from xlutils.copy import copy


def main():
    baseurl = "http://news.sina.com.cn/"
    savepath = "news.xls"
    dbpath = "news.sqlite3"
    # #1.爬取网页
    datalist = getData(baseurl)
    # #2.爬取新闻页
    complement_data = getWebs(datalist)
    # #3.完善数据结构datalist
    for i in range(len(datalist)):
        for j in range(len(complement_data[i]) - 1):
            datalist[i].append(complement_data[i][j])
        # datalist[i] = [datalist[i][0],datalist[i][1][0],datalist[i][2],datalist[i][3],datalist[i][4]]
    for i in range(len(datalist)):
        if datalist[i] == []:
            datalist.remove(i)
        for j in range(len(datalist[i])):
            if type(datalist[i][j]) is list:
                if datalist[i][j] != []:
                    datalist[i][j] = str(datalist[i][j][0])
                else:
                    datalist[i][j] = ''

    # #4. 存储到db和excel
    saveData2DB(datalist, dbpath)
    saveWeb(datalist, savepath)


# 爬取新闻规则
# Find_Title = re.compile(r'<a data-param="_f=index_chan08cpc_0" href="(.*?)">')
Find_Title = re.compile(r'target="_blank">(.*?)</a>')
Find_Link = re.compile(r'href="(.*?)" target="_blank">')

Find_Img_Link = re.compile(r'src="(.*?)"')
Find_Essay = re.compile(r'"(.*?)"')
Find_Date = re.compile(r'<span class="date">(.*?)</span>')


#从Excel读取要爬的网址，返回存有link的list
def readExcel(savepath):
    readbook = xlrd.open_workbook(r'news.xls')
    sheet = readbook.sheet_by_index(0)  #索引的方式，从0开始
    # rowNum = sheet.nrows
    # colNum = sheet.ncols
    #第二列数据
    cols2 = sheet.col_values(1)
    # for item in cols2:
    #     print(item, '\n')
    return cols2


#爬取新闻内部网页+图片,保存至excel
#根据link，得到text和img的url，下载text和img
def getWebs(datalist_already):
    #datalist_already = title + url
    # 从db中获取link_list

    link_list = []
    for i in range(len(datalist_already)):
        link_list.append(datalist_already[i][1][0])
    print(link_list)

    datalist = []

    for item in link_list:
        data = getWeb(item)
        data.append(item)  #第三列保存web网址，用于判断是否成功爬取网页
        datalist.append(data)
    # saveWeb(datalist, savepath)
    return datalist


# getWebs (from excel)
# def getWebs(savepath):
#     link_list = readExcel(savepath)
#     del link_list[0]  #去掉excel表里的标题栏
#     datalist = []
#     # print(link_list)
#     for item in link_list:
#         data = getWeb(item)
#         data.append(item)  #第三列保存web网址，用于判断是否成功爬取网页
#         datalist.append(data)
#     # saveWeb(datalist, savepath)
#     return datalist


#爬取一个网页的img和essay-》data
def getWeb(url):
    data = []
    # url = "https://news.sina.com.cn/c/2020-11-12/doc-iiznezxs1558624.shtml"

    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all('div', class_="img_wrapper"):  #查找符合要求的字符串，形成列表
        #print(item)   #测试：查看电影item全部信息
        item = str(item)
        #print(item, '\n\n')
        #得到img链接
        imglink = re.findall(Find_Img_Link, item)
        # print(url, imglink)
        data.append(imglink[0])
        if data != []:
            break
    if data == []:
        data.append("")
    essay = ""
    if soup.find('div', attrs={"class": 'article', "id": "article"}) != None:
        text = soup.find('div', attrs={
            "class": 'article',
            "id": "article"
        }).find_all('p')
        for t in text:
            essay += t.text + '\n'
    data.append(essay)
    # print(data, '\n\n')
    item = soup.find_all('span', class_="date")  #查找符合要求的字符串，形成列
    item = str(item)
    time = re.findall(Find_Date, item)
    data.append(time)

    return data


# save web to excel
# 通过read+copy写数据，不能自动创建文件，如果excel不存在会报错 ###
def saveWeb(datalist, savepath):
    print("save....")
    book = xlrd.open_workbook(savepath)
    newWb = copy(book)  #复制
    newWs = newWb.get_sheet(0)
    #取sheet表
    sheet = newWs
    col = ("title", "link", "imglink", "essay", "date")
    for i in range(0, 5):
        sheet.write(0, i, col[i])  #列名
    # print(datalist)
    for i in range(0, len(datalist)):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 5):
            sheet.write(i + 1, j, data[j])  #数据

    newWb.save(savepath)  #保存


#爬取网页，得到新闻名称，链接
def getData(baseurl):
    datalist = []
    #for i in range(0, 10):  #调用获取页面信息的函数，10次
    url = baseurl
    html = askURL(url)  #保存获取到的网页源码

    # print(html)

    # 2.逐一解析数据
    soup = BeautifulSoup(html, "html.parser")
    # 第一种:在attrs属性用字典进行传递参数
    # find_class = soup.find(attrs={'class':'item-1'})
    # print('findclass:',find_class,'\n')
    # # 第二种:BeautifulSoup中的特别关键字参数class_
    # beautifulsoup_class_ = soup.find(class_ = 'item-1')
    # print('BeautifulSoup_class_:',beautifulsoup_class_,'\n')
    for item in soup.find_all('h1', attrs={"data-client":
                                           "headline"}):  #查找符合要求的字符串，形成列表
        #print(item)   #测试：查看电影item全部信息
        data = []  #保存一部电影的所有信息
        item = str(item)
        # print(item, '\n\n')
        #得到新闻名字
        title = re.findall(Find_Title, item)[0]

        # 为了防止存入db时，标题中的双引号与最外面的引号乱匹配
        title = title.replace('\"', '\'')

        # print(type(title), title)

        data.append(title)
        # print(title, '\n\n')
        #得到新闻链接
        link = re.findall(Find_Link, item)
        # print(link, '\n\n')
        data.append(link)

        datalist.append(data)

    return datalist


#得到指定一个URL的网页内容
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


#保存数据
def saveData(datalist, savepath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  #创建workbook对象
    sheet = book.add_sheet('news', cell_overwrite_ok=True)  #创建工作表
    col = ("title", "link")
    for i in range(0, 2):
        sheet.write(0, i, col[i])  #列名
    for i in range(0, 6):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 2):
            sheet.write(i + 1, j, data[j])  #数据

    book.save(savepath)  #保存


def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    #这两种方法循环出的的结果不一样？？？？
    # for i in range(len(datalist)):
    #     print(datalist[i])
    for data in datalist:
        for index in range(len(data)):
            # print(data[index])
            if type(data[index]) is str:
                data[index] = '"' + data[index] + '"'
            else:
                print(data[index], '\n')
    # for i in range(len(datalist)):
    #     print(datalist[i])

    #     print(data)
    # print(datalist)
    # 如果上次数据没有清空，下次insert会报错：primary key not unique
    # 先判断db中是否存在data，如果不存在则insert，否则跳过
        check_existed = '''select title from news where title=%s''' % data[0]
        print(check_existed)
        cur.execute(check_existed)
        conn.commit()
        rs = cur.fetchall()
        # print(type(rs), rs)
        #rs是list，没有查询到结果时返回[]
        if rs != []:
            continue
        else:
            #插入新闻条目
            sql = '''
                insert into news (
                title,link,imglink,essay,`date`)
                values(%s)''' % ",".join(data)
            # print(sql)
            cur.execute(sql)
            conn.commit()

    cur.close()
    conn.close()


def init_db(dbpath):
    sql = '''
        create table if not exists news
        (
            title varchar primary key,
            link varchar,
            imglink varchar,
            essay varchar,
            date varchar
        )
    
    '''  #创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":  #当程序执行时
    #调用函数
    main()
    #init_db("movietest.db")
    print("爬取完毕！")