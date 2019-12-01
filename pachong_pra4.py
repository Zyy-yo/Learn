import numpy as np 
import pandas as pd 
import requests 
from bs4 import BeautifulSoup 
import os 
import time

def pageurl(city, n):
    # 分页网址
    pages = []
    for i in range(n):
        pages.append('https://travel.qunar.com/p-cs299878-%s-jingdian-1-%i'%(city, i + 1))
    return pages


def data(ul, head, cooki):
    # 采集数据
    r = requests.get(ul, headers=head, cookies=cooki)
    soup = BeautifulSoup(r.text, 'lxml')

    lis = soup.find('ul', class_="list_item clrfix").find_all('li')

    datalst = []
    for li in lis:
        try:
            datadic = {}
            datadic['经度'] = li['data-lng']
            datadic['纬度'] = li['data-lat']
            datadic['景区'] = li.find('span', class_="cn_tit").text
            datadic['攻略数'] = li.find('div', class_="strategy_sum").text
            datadic['点评数'] = li.find('div', class_="comment_sum").text
            datadic['来过驴友比例'] = li.find('span', class_="sum").text
            datadic['评分'] = li.find('span', class_="cur_star")['style']
            datadic['排名'] = li.find('span', class_="ranking_sum").text
            datadic['简介'] = li.find('div', class_="desbox").text
            datalst.append(datadic)
        except:
            continue
    return datalst

if __name__ == '__main__':
    os.chdir(r'D:\工作\数据分析\微专业\项目数据\爬虫练习项目')

    dic_h = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    dic_c = {}
    cookies = 'QN1=O5cv7V3jIaqSFFSSFxf+Ag==; QN205=organic; QN277=organic; csrfToken=i2EapmvfZnhMiv3q5UCGScVnPnt1spKH; _i=VInJOQCCNRxVqTuxZHjs7pYZqbRq; QN269=183E006113E011EA8246FA163E5906AD; Hm_lvt_c56a2b5278263aa647778d304009eafc=1575166380; fid=fe5e44e1-66cd-4ec9-9f9a-f2da0c5c25fa; viewdist=299878-5; uld=1-299878-5-1575167496; QN267=010631379781b287141; _vi=cqbKrfwX8Hwy8lmPP1nOhwVkAuHQo9GxnMcIpV_J6V-lrmNuiFN1-hhrXVMJeOiEJou3CkgEU2-Wn7W6dmnU7ZCo-E0FNgN0UHA46wprPPjUIaanuHy0lvfi8EMZsKnb3yixGchPK7Q9mpbMahddFpEyy4GzEtNe46365PzkqXmC; Hm_lpvt_c56a2b5278263aa647778d304009eafc=1575167497; QN271=8eddc762-0d4e-4211-bee7-8ae2ba156c63'
    for i in cookies.split('; '):
        dic_c[i.split('=')[0]] = i.split('=')[1]

    # 分页网址
    pageurls = pageurl('shanghai', 20)
    # 采集数据
    datas = []
    n = 0
    for pu in pageurls:
        try:
            datas.extend(data(pu, dic_h, dic_c))
            n += 1
            print('成功采集第%i页'%n)
            time.sleep(np.random.uniform(3,8))
        except:
            print('%s采集失败'%pu)
    # 存储数据
    df = pd.DataFrame(datas)

    # 初步清洗
    df['经度'] = df['经度'].astype('float')
    df['纬度'] = df['纬度'].astype('float')
    df['攻略数'] = df['攻略数'].astype('int')
    df['点评数'] = df['点评数'].astype('int')
    df['来过驴友比例'] = df['来过驴友比例'].str.split('%').str[0].astype('float') / 100
    df['评分'] = df['评分'].str.split(':').str[-1].str.replace('%', '').astype('int')
    df.replace('', np.nan, inplace=True)

    df.to_excel('去哪儿网上海景点爬取.xlsx')
