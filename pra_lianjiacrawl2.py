import re 
import requests
from bs4 import BeautifulSoup
import datetime
from fake_useragent import UserAgent
import pymongo

'''
链家网-北京二手房信息详情页采集-含经纬度
'''

def urls(table):
    # 数据信息页链接
    url = []
    for i in table.find():
        url.append(i['链接'])
    return url

def proxy_ip(p_host, p_port, p_user, p_pass):
    # 代理IP
    proxy = 'http://%(user)s:%(pass)s@%(host)s:%(port)s'%{
        'user': p_user,
        'pass': p_pass,
        'host': p_host,
        'port': p_port
    }
    proxyip = {
        'http': proxy,
        'https': proxy
    }
    return proxyip

def get_data(ul, d_h, ip, table):
    r = requests.get(ul, headers=d_h, proxies=ip)
    soup = BeautifulSoup(r.text, 'lxml')

    dic = {}
    dic['获取日期'] = str(datetime.datetime.today().date())
    dic['标题'] = soup.h1.text
    
    # 基本信息
    info1 = soup.find('div', class_="base").find_all('li')
    for li in info1:
        lisp = re.split(r'<.*?>', str(li))
        dic[lisp[2]] = lisp[3]
    # 交易信息
    info2 = soup.find('div', class_="transaction").find_all('li')
    for li in info2:
        lisp = re.split(r'<.*?>', str(li))
        dic[lisp[2]] = re.sub(r'\s', '', lisp[4])

    # 经纬度
    position = re.search(r"resblockPosition:'([\d.]+),([\d.]+)'", r.text)
    dic['lng'] = position.group(1)
    dic['lat'] = position.group(2)
    table.insert_one(dic)


if __name__ == '__main__':

    # 连接数据库
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['链家']
    table1 = db['北京二手房房源']
    table2 = db['北京二手房房源-含经纬度']

    # 获得二手房链接
    dataurls = urls(table1)

    # 动态代理IP
    proxyUser = 'xxxxxxx'
    proxyPass = 'xxxxxxx'
    proxyHost = 'xxx'
    proxyPort = 'xxx'
    proxyIp = proxy_ip(proxyHost, proxyPort, proxyUser, proxyPass)

    # 采集数据
    count = 0
    errul = []
    for du in dataurls:
        dic_h = {'User-Agent': UserAgent().random}
        try:
            get_data(du, dic_h, proxyIp, table2)
            count += 1
            print('采集%i条数据'%count)
        except:
            errul.append(du)
    if len(errul) > 0:
        print('以下链接采集失败：\n', errul)
    print('----采集完毕----')

