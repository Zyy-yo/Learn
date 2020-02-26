import numpy as np 
import pandas as pd 
import requests 
from bs4 import BeautifulSoup
import time
import os


def pageurl(n):
    # 分页网址
    pageurl_lst = []
    for i in range(n):
        pageurl_lst.append('https://book.douban.com/tag/%E7%94%B5%E5%BD%B1' + '?start=%i&type=T'%(20 * i))
    return pageurl_lst


def get_dataurl(ur, head, cooki):
    # 获取数据信息网页
    r = requests.get(ur, headers=head, cookies=cooki)   # 请求网页
    soup = BeautifulSoup(r.text, 'lxml')        # 解析
    ul = soup.find('ul', class_="subject-list")
    lis = ul.find_all('li')                        # ul下的所有li项

    bookurls = []
    for divs in lis:
        div = divs.find('div', class_="info")
        bookurl = div.find('a')['href']        # 获得书的网站
        bookurls.append(bookurl)
    return bookurls


def get_data(ur, head, cooki):
    # 获得每本书的信息
    r = requests.get(ur, headers=head, cookies=cooki)
    soup = BeautifulSoup(r.text, 'lxml')

    datadic = {}
    try:
        datadic['书名'] = soup.find('div', id="wrapper").find('span').text       # 获得书名
        bookinfo = soup.find('div', id="info").text        # 获得书籍其他信息
        bookinfos = bookinfo.replace('\n ', '').split('\n')

        for i in bookinfos:
            if len(i) > 0:
                datadic[i.split(':')[0]] = i.split(':')[1].strip()    # 书籍信息存储到字典

        pfinfo = soup.find('div', id="interest_sectl")       # 评价信息
        datadic['评分'] = pfinfo.find('strong').text                 # 获得评分
        datadic['评价人数'] = pfinfo.find('div', class_="rating_sum").text   # 获得评价人数
    except:
        pass
    return datadic

if __name__ == '__main__':

    os.chdir('D:\工作\数据分析\微专业\项目数据\爬虫练习项目')

    dic_h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    cookies = 'll="108296"; bid=KOKivekG4Nw; __utmz=30149280.1574934053.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); gr_user_id=ab81abe7-994e-4e21-8e48-b0c97cb9e343; _vwo_uuid_v2=DF4B2C201C732671CC9F26DA59AA63F4F|e4b8ebeb78ca95cc670da4b65d44f1c0; __yadk_uid=hYzRt2DDT7mDVtrTfQhbmylIsWA6btqI; __utmc=30149280; __utmc=81379588; __utmz=81379588.1575005429.3.3.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ap_v=0,6.0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1575009824%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utma=30149280.140224724.1574934053.1575005428.1575009825.4; __utmt_douban=1; __utma=81379588.160695951.1574934056.1575005429.1575009825.4; __utmt=1; viewed="34693685"; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=efecc6cd-7486-414c-bbee-30189ed416ea; gr_cs1_efecc6cd-7486-414c-bbee-30189ed416ea=user_id%3A0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_efecc6cd-7486-414c-bbee-30189ed416ea=true; _pk_id.100001.3ac3=15b44def12cc41af.1574934057.4.1575009964.1575005434.; __utmb=30149280.3.10.1575009825; __utmb=81379588.3.10.1575009825'
    dic_c = {}
    for i in cookies.split('; '):
        dic_c[i.split('=')[0]] = i.split('=')[1]

    # 分页网址
    pageurls = pageurl(10)

    # 每本书籍的数据信息网页
    dataurls = []
    for i in pageurls:
        dataurl = get_dataurl(i, dic_h, dic_c)
        dataurls.extend(dataurl)
        time.sleep(np.random.uniform(5,10))   

    # 遍历数据信息网页，获取所有书籍信息，存储到列表
    datalst = []
    n = 0
    for url in dataurls:
        bookdata = get_data(url, dic_h, dic_c)
        datalst.append(bookdata)
        n += 1
        print('成功采集%i条信息'%n)
        time.sleep(np.random.uniform(3, 7))
        
    df = pd.DataFrame(datalst)
    df.to_excel('豆瓣读书电影类书籍爬取.xlsx')


