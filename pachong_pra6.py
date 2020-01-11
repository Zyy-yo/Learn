import numpy as np 
import time
import os 
import re
import pymongo
import requests
from bs4 import BeautifulSoup

'''
爬虫逻辑：【视频页面url采集】-【视频页面数据采集 / cid信息 / 弹幕xml数据采集】
'''


def videourl(ul, head):
    r = requests.get(ul, headers=head)
    soup = BeautifulSoup(r.text, 'lxml')
    lis = soup.find('ul', class_="video-list clearfix").find_all('li')
    urls = []
    for li in lis:
        urls.append('https:' + li.a['href'])
    r.close()
    return urls


def get_data(ul, head, table):
    r = requests.get(ul, headers=head)
    soup = BeautifulSoup(r.text, 'lxml')

    cid = re.search(r'"cid":(\d*),', r.text).group(1)           # 视频cid，注意直接从网页源代码中用正则获取
    name = soup.find('div', id="viewbox_report").h1['title']      # 视频标题
    dates = soup.find('div', class_="video-data").text            
    date = re.search(r'(\d{4}-\d{2}-\d{2})', dates).group(1)                  # 视频发布日期

    u2 = 'https://comment.bilibili.com/%s.xml'%cid               # 该视频的弹幕url
    r2 = requests.get(u2)    
    r2.encoding = r2.apparent_encoding                                
    dms = re.findall(r'<d.*?</d>', r2.text)                       # 用正则从弹幕url获得所有弹幕标签，这里一定要非贪婪模式，否则所有的都在一个字符串里

    n = 0
    for dm in dms:
        dic = {}
        dic['标题'] = name 
        dic['发布时间'] = date
        dic['cid'] = cid
        dic['弹幕'] = re.search(r'>(.*)</d>', dm).group(1)           # 正则从每个弹幕标签里获取弹幕文本
        dic['其他信息 '] = re.search(r'p="(.*)">', dm).group(1)
        table.insert_one(dic)                                       # 存到数据库
        n += 1
    r2.close()
    r.close()
    return n


if __name__ == '__main__':
    ul = r'https://search.bilibili.com/all?keyword=%E8%82%96%E6%88%98&from_source=nav_search_new'  # 搜索肖战后的url

    # d_h = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'}
    d_h = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17'}

    
    # 获取该页每条视频的url
    videourls = videourl(ul, d_h)

    # 连接数据库
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient['哔哩哔哩']
    table = db['肖战相关视频弹幕']

    n2 = 0
    for vu in videourls:
        try:
            n2 += get_data(vu, d_h, table)
            time.sleep(np.random.uniform(1,5))
            print('共采集数据%i条'%n2)
        except:
            ('%s采集失败'%vu)

