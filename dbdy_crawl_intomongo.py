import requests
from bs4 import BeautifulSoup
import pymongo
import re

# 豆瓣电影采集上海堡垒的短评，并存入mongo数据库

# 连接mongo，创建数据库和集合
client = pymongo.MongoClient("localhost",27017)
db = client['豆瓣']
table = db['上海堡垒影评']

# 分析网址
url1 = 'https://movie.douban.com/subject/26581837/comments?start=0&limit=20&sort=new_score&status=P'
url2 = 'https://movie.douban.com/subject/26581837/comments?start=20&limit=20&sort=new_score&status=P'

# 生成前50页的网页链接
urls = []
for i in range(50):
    url = 'https://movie.douban.com/subject/26581837/comments?start=%s&limit=20&sort=new_score&status=P'%(i*20)
    urls.append(url)

# 访问网页，获取数据，存入数据库
n = 0
table.delete_many({})

for u in urls:
    r = requests.get(u)
    soup = BeautifulSoup(r.text,'lxml')
    divs = soup.find('div', class_='mod-bd').find_all('div')

    for div in divs:
        dic = {}
        try:
            info1 = div.find('span', class_='comment-info').text     # 单独找这一条没有问题，放到for循环里就报错'NoneType' object has no attribute 'text'
            info1 = re.split(r'[\n]+',info1)
            info2 = div.find('span', class_='comment-vote').text
            info2 = re.split(r'[\n]+',info2)

            dic['用户'] = info1[1]
            dic['是否看过'] = info1[2]
            dic['评价时间'] = info1[3].strip()
            dic['评价'] = div.find('span', title=re.compile(r'[^A-Za-z]')).attrs['title']
            dic['有用数量'] = info2[1]
            dic['评论内容'] = div.find('p').text.strip()

            table.insert_one(dic)
            n += 1
            print('采集%d条数据'%n)
        except:
            continue

# 只能采集到440条数据，之后报错'NoneType' object has no attribute 'find_all'，错误行 divs = soup.find('div', class_='mod-bd').find_all('div')
# 实际采集数据220条，每条数据都重复采集