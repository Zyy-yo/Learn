import numpy as np 
import requests 
from bs4 import BeautifulSoup 
import os 
import time


def pageurl(n):
    # 分页网址
    pageurls = []
    for i in range(n):
        pageurls.append('https://movie.douban.com/subject/25887288/photos' + '?type=S&start=%i&sortby=like&size=a&subtype=a'%(30 * i))
    return pageurls

def get_data(ur, head, cooki):
    # 获取图片id和url
    r = requests.get(ur, headers=head, cookies=cooki)
    soup = BeautifulSoup(r.text, 'lxml')

    lis = soup.find('ul', class_="poster-col3 clearfix").find_all('li')

    imginfo = []
    for li in lis:
        imgdic = {}
        imgdic['id'] = li['data-id']
        imgdic['src'] = li.img['src']
        imginfo.append(imgdic)
    return imginfo

def save_pic(srcs, head):
    # 存储图片
    r = requests.get(srcs['src'], headers=head)
    with open('P' + srcs['id'] + '.jpg', 'ab') as f:
        f.write(r.content)
        f.close()


if __name__ == '__main__':

    os.chdir(r'D:\工作\数据分析\微专业\项目数据\爬虫练习项目\豆瓣电影图片爬取')

    ul = 'https://movie.douban.com/subject/25887288/photos?type=S&start=0&sortby=like&size=a&subtype=a'
    dic_h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    cookies = 'll="108296"; bid=KOKivekG4Nw; __utmz=30149280.1574934053.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); gr_user_id=ab81abe7-994e-4e21-8e48-b0c97cb9e343; _vwo_uuid_v2=DF4B2C201C732671CC9F26DA59AA63F4F|e4b8ebeb78ca95cc670da4b65d44f1c0; __yadk_uid=hYzRt2DDT7mDVtrTfQhbmylIsWA6btqI; __utmc=30149280; __utmc=81379588; __utmz=81379588.1575005429.3.3.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ap_v=0,6.0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1575009824%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utma=30149280.140224724.1574934053.1575005428.1575009825.4; __utmt_douban=1; __utma=81379588.160695951.1574934056.1575005429.1575009825.4; __utmt=1; viewed="34693685"; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=efecc6cd-7486-414c-bbee-30189ed416ea; gr_cs1_efecc6cd-7486-414c-bbee-30189ed416ea=user_id%3A0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_efecc6cd-7486-414c-bbee-30189ed416ea=true; _pk_id.100001.3ac3=15b44def12cc41af.1574934057.4.1575009964.1575005434.; __utmb=30149280.3.10.1575009825; __utmb=81379588.3.10.1575009825'
    dic_c = {}
    for i in cookies.split('; '):
        dic_c[i.split('=')[0]] = i.split('=')[1]

    # 分页网址
    pageurls = pageurl(10)

    # 采集图片链接
    imgdatas = []
    n = 0
    for pu in pageurls:
        try:
            imgdata = get_data(pu, dic_h, dic_c)
            imgdatas.extend(imgdata)
            n += 1
            print('成功采集第%i页数据'%n)
            time.sleep(np.random.uniform(2,6))
        except:
            print('%s采集失败'%pu)

    # 采集图片并存储
    n1 = 0
    for i in imgdatas:
        try:
            save_pic(i, dic_h)
            n1 += 1
            print('采集%i张图片'%n1)
            time.sleep(np.random.uniform(2,5))
        except:
            continue
    

    