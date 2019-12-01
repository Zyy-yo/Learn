import numpy as np 
import pandas as pd 
import requests 
from bs4 import BeautifulSoup 
import os 
import time

def pageurl(n):
    # 分页网址
    purls = []
    for i in range(n):
        purls.append(r'https://book.douban.com/tag/%E6%8E%A8%E7%90%86' + '?start=%i&type=T'%(i * 20))
    return purls


def data(ur, head, cooki):
    r = requests.get(ur, headers=head, cookies=cooki)
    soup = BeautifulSoup(r.text, 'lxml')

    lis = soup.find('ul', class_="subject-list").find_all('li')  # 找到所有图书所在的列表项

    booklst = []
    for li in lis:
        datadic = {}                               # 这里要注意，空字典在循环里面
        div = li.find('div', class_="info")
        datadic['书名'] = div.h2.text.replace('\n', '').replace(' ', '')
        datadic['info'] = div.find('div', class_="pub").text.replace('\n', '').replace(' ', '')
        datadic['评分'] = div.find('span', class_="rating_nums").text
        datadic['评价人数'] = div.find('span', class_="pl").text.replace('\n', '').replace(' ', '')
        datadic['简介'] = div.p.text.replace('\n', '')
        booklst.append(datadic)
    return booklst


if __name__ == '__main__':
    os.chdir(r'D:\工作\数据分析\微专业\项目数据\爬虫练习项目')

    # 设置登录信息cookie
    dic_h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    cookies = 'll="108296"; bid=KOKivekG4Nw; gr_user_id=ab81abe7-994e-4e21-8e48-b0c97cb9e343; _vwo_uuid_v2=DF4B2C201C732671CC9F26DA59AA63F4F|e4b8ebeb78ca95cc670da4b65d44f1c0; __yadk_uid=hYzRt2DDT7mDVtrTfQhbmylIsWA6btqI; viewed="27174130_1080370_34693685_1829226"; __gads=ID=c89e8f73ea3371df:T=1575079581:S=ALNI_MaAB1a7jdTiZITbvtXuZyXfeNw_OA; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=4b98ee65-12c2-47ef-8ed3-348b02d75060; gr_cs1_4b98ee65-12c2-47ef-8ed3-348b02d75060=user_id%3A0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1575087666%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; ap_v=0,6.0; __utma=30149280.140224724.1574934053.1575079579.1575087666.8; __utmc=30149280; __utmz=30149280.1575087666.8.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=81379588.160695951.1574934056.1575079579.1575087666.8; __utmc=81379588; __utmz=81379588.1575087666.8.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_4b98ee65-12c2-47ef-8ed3-348b02d75060=true; _pk_id.100001.3ac3=15b44def12cc41af.1574934057.8.1575087691.1575079709.; __utmb=30149280.4.10.1575087666; __utmb=81379588.3.10.1575087666'
    dic_c = {}
    for i in cookies.split('; '):
        dic_c[i.split('=')[0]] = i.split('=')[1]

    # 分页网址
    pageurls = pageurl(10)

    # 采集数据
    datalst = []
    n = 0
    for i in pageurls:
        try:
            bookdata = data(i, dic_h, dic_c)
            datalst.extend(bookdata)
            n += 1
            print('成功采集%i页信息'%n)
            time.sleep(np.random.uniform(3,7))
        except:
            print('%s采集失败'%i)

    # 转为dataframe
    df = pd.DataFrame(datalst)
    df['作者'] = df['info'].str.split('/').str[0]
    df['出版社'] = df['info'].str.split('/').str[-3]
    df['出版年份'] = df['info'].str.split('/').str[-2]
    df['价格'] = df['info'].str.split('/').str[-1]
    
    # 评价人数初步清洗
    df['评价人数'][df['评价人数'] == '少于10人评价'] = df['评价人数'][df['评价人数'] == '少于10人评价'].str.split('人').str[0].str[2:]
    df['评价人数'][df['评价人数'] != '少于10人评价'] = df['评价人数'][df['评价人数'] != '少于10人评价'].str.split('人').str[0].str[1:]
    df['评价人数'][df['评价人数'].str.contains('无')] = np.nan

    df.to_excel('豆瓣读书推理类书籍爬取.xlsx')
        

