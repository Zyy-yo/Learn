import numpy as np 
import re
import time
import pymongo
import requests
from bs4 import BeautifulSoup
import datetime

'''链家北京二手房房源信息采集'''

def pageurl(n):
    # 分页网址
    url = []
    for i in range(1,n+1):
        url.append('https://bj.lianjia.com/ershoufang/pg%i'%i)
    return url


def get_data(ul, d_h, table):
    # 数据采集
    r = requests.get(ul, headers=d_h)
    soup = BeautifulSoup(r.text, 'lxml')
    lis = soup.find('ul', class_="sellListContent").find_all('li')
    n = 0
    for li in lis:
        try:
            dic = {}
            dic['获取日期'] = str(datetime.datetime.today().date())
            dic['标题'] = li.find('div', class_="title").text

            position = li.find('div', class_="positionInfo").text
            dic['小区'] = position.split('-')[0].strip()
            dic['位置'] = position.split('-')[1].strip()

            info = li.find('div', class_="houseInfo").text
            dic['户型'] = info.split('|')[0].strip()
            dic['面积'] = info.split('|')[1].strip()
            dic['朝向'] = info.split('|')[2].replace(' ', '')
            dic['装修'] = info.split('|')[3].strip()
            dic['楼层'] = info.split('|')[4].strip()
            dic['建成年份'] = info.split('|')[5].strip()
            dic['结构'] = info.split('|')[6].strip()

            info2 = li.find('div', class_="followInfo").text
            dic['关注人数'] = re.search(r'(\d+)', info2.split('/')[0]).group(1)
            dic['发布时间'] = info2.split('/')[1].rstrip('发布')

            dic['总价'] = li.find('div', class_="totalPrice").text
            dic['单价'] = re.search(r'(\d+)', li.find('div', class_="unitPrice").text).group(1)
            dic['链接'] = li.find('a')['href']
            table.insert_one(dic)
            n += 1
        except:
            continue
    return n


if __name__ == '__main__':

    dic_h = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'}
    
    # 北京二手房前10页网址
    pageurls = pageurl(10) 

    # 连接数据库
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['链家']
    table = db['北京二手房房源']
    table.delete_many({})

    # 获取数据
    count = 0
    for pu in pageurls:
        time.sleep(np.random.uniform(1,3))
        count += get_data(pu, dic_h, table)
        print('采集数据%i条'%count)

    print('----采集完毕----')
