import numpy as np 
import re
import time
import pymongo
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

'''链家上海二手房房源信息采集-详情页采集
动态IP代理设置
'''

def urls(table):
    # 从数据库中获取链接
    dataurls = []
    for i in table.find():
        dataurls.append(i['链接'])
    return dataurls


def get_proxies(p_host, p_port, p_user, p_pass):
    # 设置代理IP池
    proxy = 'http://%(user)s:%(pass)s@%(host)s:%(port)s'%{
        'host': p_host,
        'port': p_port,
        'user': p_user,
        'pass': p_pass
    }
    ips = {
        'http': proxy,
        'https': proxy
    }
    return ips


def get_data(ul, d_h, p_ip, table):
    '''
    采集数据
    ul ： 网页链接
    d_h ：user agent
    p_ip ：代理IP
    table ：mongodb集合对象
    '''
    r = requests.get(ul, headers=d_h, proxies=p_ip)
    soup = BeautifulSoup(r.text, 'lxml')

    dic = {}
    dic['标题'] = soup.h1.text
    # 基本信息
    info1 = soup.find('div', class_="base").find_all('li')
    for li in info1:
        lisp = re.split(r'<.*?>', str(li))
        dic[lisp[2]] = lisp[3]
    info2 = soup.find('div', class_="transaction").find_all('li')
    for li2 in info2:
        lisp2 = re.split(r'<.*?>', str(li2))
        dic[lisp2[2]] = re.sub(r'\s', '', lisp2[4])
    # 经纬度
    position = re.search(r"resblockPosition:'([\d.]+),([\d.]+)'", r.text)  
    dic['lng'] = position.group(1)
    dic['lat'] = position.group(2)
    table.insert_one(dic)


if __name__ == '__main__':

    # 连接数据库
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['链家']
    table = db['上海二手房房源']
    table2 = db['上海二手房房源-含经纬度']

    # 数据信息页链接
    dataurls = urls(table)

    # 获取动态代理IP
    proxyhost = 'xxx'     # 代理服务器域名
    proxyport = 'xxx'      # 端口
    proxyuser = 'xxx'        # 通行证书
    proxypass = 'xxx'         # 通行密钥
    proxyip = get_proxies(proxyhost, proxyport, proxyuser, proxypass)

    # 采集数据
    n = 0
    errourl = []
    for u in dataurls:
        dic_h = {'User-Agent': UserAgent().random}
        try:
            get_data(u, dic_h, proxyip, table2)
            n += 1
            print('采集%i条数据'%n)
        except:
            print('%s采集失败'%u)
            errourl.append(u)
    print('以下链接数据采集失败:\n', errourl)
    print('采集完毕')    



    

