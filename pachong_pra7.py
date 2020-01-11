import numpy as np 
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pymongo
import re
import time

'''豆瓣读书-搜索python类书籍采集'''

def sele_dataurl(browser):
    # selenium获取数据信息网址
    urls = []
    for i in range(1, 16):
        xpath = '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[%i]/div/div/div[1]/a'%i
        url = browser.find_element_by_xpath(xpath).get_attribute('href')
        urls.append(url)
        time.sleep(5)
    return urls

def get_data(ul, head, cooki, table):
    # 获取书籍数据
    r = requests.get(ul, headers=head, cookies=cooki)
    soup = BeautifulSoup(r.text, 'lxml')

    dic = {}
    dic['书名'] = re.sub(r'\s' , '', soup.h1.text)
    info = re.sub(r'\n | ', '', soup.find('div', id="info").text)  # 其他详细信息
    for i in info.split('\n'):
        if ':' in i:
            dic[i.split(':')[0]] = i.split(':')[1].strip()

    dic['评分'] = soup.find('div', class_="rating_self clearfix").find('strong').text.replace(' ', '')

    comment = soup.find('div', class_="rating_sum").text
    dic['评分人数'] = re.search(r'(\d*)人', comment).group(1)
    table.insert_one(dic)
    r.close()
    

if __name__ == '__main__':

    ul = 'https://search.douban.com/book/subject_search?search_text=python&cat=1001&start=0' 
    cookies = 'll="108296"; bid=Ka83TdNq1ME; __utmz=30149280.1575534363.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); push_doumail_num=0; push_noty_num=0; __utmv=30149280.20199; _pk_ses.100001.3ac3=*; ap_v=0,6.0; __yadk_uid=6AEs6JCuadikbUd49xQptTmghrOpizyv; __utma=30149280.340274549.1575534363.1575540147.1575593081.3; __utmc=30149280; _vwo_uuid_v2=DCE8DADA05CB5AEE832BCB5DEC3CA74EC|7b3ab12f37b50264301e17ad91bb63bd; gr_user_id=0e8040e1-ff89-40ca-8e9c-cbcdde6e2c51; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=d0608638-8600-4138-ab4c-6596c5f33516; gr_cs1_d0608638-8600-4138-ab4c-6596c5f33516=user_id%3A0; __utma=81379588.1837941913.1575593172.1575593172.1575593172.1; __utmc=81379588; __utmz=81379588.1575593172.1.1.utmcsr=search.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/book/subject_search; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_d0608638-8600-4138-ab4c-6596c5f33516=true; __gads=ID=5bc0491125892b07:T=1575593172:S=ALNI_Mboet1Dtq18rN_2DmXqT3gBBpBArw; viewed="3112503_25779298_26829016"; __utmt_douban=1; __utmt=1; __utmb=81379588.3.10.1575593172; _pk_id.100001.3ac3=f06ff286f7404fc8.1575593080.1.1575594132.1575593080.; __utmt=1; __utmb=30149280.11.10.1575593081'
    d_c = {}
    for i in cookies.split('; '):
        d_c[i.split('=')[0]] = i.split('=')[1]
    d_h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.105 Safari/537.36'}


    # 数据信息页
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=option)
    driver.get(ul)
    dataurls = []
    for i in range(1, 11):
        dataurls.extend(sele_dataurl(driver))
        print('采集链接%i条'%len(dataurls))
        time.sleep(np.random.uniform(10,15))
        if i != 10:
            driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div[1]/div[1]/div[16]/a[%i]'%(i+2)).click()
        else:
            pass
    driver.quit()

    # 连接数据库
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['douban']
    table = db['豆瓣读书搜索-python']

    # 数据采集
    n = 0
    for ul in dataurls:
        try:
            get_data(ul, d_h, d_c, table)
            n += 1
            print('采集数据%i条'%n)
            time.sleep(np.random.uniform(5,10))
        except:
            print('%s采集失败'%ul)
    print('--------采集完毕---------')
        


    