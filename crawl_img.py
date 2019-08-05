# 哪吒之魔童降世剧照获取（只获取部分）
import requests
from bs4 import BeautifulSoup
import os

'''
观察链接
url = 'https://movie.douban.com/subject/26794435/photos?type=S&start=0&sortby=like&size=a&subtype=a'
url = 'https://movie.douban.com/subject/26794435/photos?type=S&start=30&sortby=like&size=a&subtype=a'
'''

# 获取前5页链接，变量在链接字符串的中间位置，此时可以用格式控制字符串%s替代，再在字符串结尾加上控制格式的变量，如下所示
urls = []
for i in range(0,121,30):
    url = 'https://movie.douban.com/subject/26794435/photos?type=S&start=%s&sortby=like&size=a&subtype=a'%i
    urls.append(url)
# 遍历每个网页链接，来获取每页图片标签
imgs = []
for u in urls:
    r = requests.get(u)     # 网页访问
    soup = BeautifulSoup(r.text,'lxml')   # 网页解析
    img = soup.find('ul', class_='poster-col3 clearfix').find_all('img')   # 采集图片标签
    imgs.extend(img)                 # 此处用extend添加到imgs列表中，因为img是可迭代的列表项

imgsrc = [x['src'] for x in imgs]         # imgs['src']可以直接提取img标签里的src属性值，也就是图片链接

# os.mkdir(r'D:\PY\图片')            # 创建图片文件夹，来存储图片，因为创建成功之后无法再创建，此处注释掉
os.chdir(r'D:\PY\图片')              # 指定工作路径，图片会存储到工作路径
# 遍历imgsrc列表，访问图片链接
n = 0
for g in imgsrc:
    n += 1                               # 图片名称顺序
    r = requests.get(g)                  # 访问图片链接
    with open('哪吒%s.jpg'%n, 'wb') as f:           # 打开一个空的jpg格式文件，'wb'表示写入二进制流
        f.write(r.content)                 # 写入图片的二进制流，图片不是text，而是二进制流
    print('成功保存%s张图片'%n)





