from bs4 import BeautifulSoup
import requests
import pandas as pd

# 网页上上海景点一共有200页，为了快速演示，只提取前10页
list = []
url1 = 'https://travel.qunar.com/p-cs299878-shanghai-jingdian-1-'
for i in range(0,11):
    list.append(url1+str(i))

data = []
for l in list:
    r = requests.get(l)      # 访问网页
    soup = BeautifulSoup(r.text,'lxml')     # 解析网页
    # 要找的信息在哪个块，查找这个块，注意find只会查找到第一个出现的符合条件的目标
    ul = soup.find('ul', class_='list_item clrfix')
    # 查找块里所有的列表赋给变量
    li = ul.find_all('li')
    # 获取想要的信息：景点名称、攻略数、点评数、星级
    for li0 in li:
        dic = {}       # 定义一个空字典
        # 将获取到的元素存到字典
        dic['景点名称'] = li0.find('span', class_='cn_tit').text
        dic['攻略数'] = li0.find('div', class_='strategy_sum').text  # .text表示在获取的这个标签里找到它的元素
        dic['点评数'] = li0.find('div', class_='comment_sum').text
        dic['星级'] = li0.find('span', class_='cur_star').attrs['style']
        data.append(dic)        # 将该页获取信息得到的字典存到data列表

df = pd.DataFrame(data)
df.to_excel(r"D:\Fighting\data_fromweb.xlsx")




