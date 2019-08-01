from datetime import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
# now = datetime.now()
# """
# date = datetime.strptime('20090809',r'%Y%m%d')  
# 返回datetime格式，传入参数必须是字符串格式

# date1 = datetime.strftime(datetime(2009,8,9),r'%Y%m%d') 
# '''
# 返回字符串，传入参数必须是datetime格式
# 或写作
# date1 = datetime(2009,8,9).strftime(r'%Y%m%d')
# '''
# """
# print(now)
# a = timedelta(days=39)      # datetime格式
# print(a)
# now = date - a
# print(now)
# print(now.strftime(r'%Y%m%d'))

# url = 'http://www.xzw.com/fortune/leo/20190228.html' # 狮子座
# url ='http://www.xzw.com/fortune/aries/20190701.html' # 白羊座

'''
如果要获得十二星座7月运势数据，url里有两个变量，一是星座变量，二是日期变量
所有星座放到一个列表里，通过遍历这个列表获得星座
遍历到某个星座时，遍历一遍日期，获得该星座的这个日期范围内的数据
'''
# 首先建立一个列表，将所有星座放进去
cons = ['aries','taurus','gemini','cancer','leo','virgo','libra',
        'scorpio','sagittarius','capricorn','aquarius','pisces']
# 设定一个初始日期，获取这个日期之后的数据，我要获取7月数据
date0 = datetime.strptime('20190701',r'%Y%m%d')
'''
建立空列表存放获取到的链接
遍历星座列表，每遍历一个星座，获取该星座一个月的链接
'''
urldic = []
for f in cons:
    i = 0
    url = 'http://www.xzw.com/fortune/'
    while i < 31:
        day = timedelta(days=i)
        date = date0 + day
        urldic.append(url+str(f)+'/'+date.strftime(r'%Y%m%d')+'.html')
        i += 1
'''
现在已经获取到所有星座的链接
接下来遍历链接列表，每访问一个链接，解析，然后获取数据存放到字典
'''
data = []
for u in urldic:
	r = requests.get(u)
	soup = BeautifulSoup(r.text,'lxml')
	div = soup.find('div',{'class':'c_main'})
	dic = {}
	dic['title'] = div.find('h4').text
	def div_fun(x, y):
		dic[x] = div.find('ul').find_all('li',limit=4)[y].find('em',style=re.compile(r'width:\d*px')).attrs['style']
	div_fun('综合运势', 0)
	div_fun('爱情运势', 1)
	div_fun('事业学业', 2)
	div_fun('财富运势', 3)

	def div_fun2(x, y):
		dic[x] = div.find('ul').find_all('li')[y].text
	div_fun2('健康',4)
	div_fun2('商谈',5)
	div_fun2('颜色',6)
	div_fun2('数字',7)
	div_fun2('速配',8)

	div2 = soup.find('div',class_='c_cont')
	def div2_fun(x, y):
		dic[x] = div2.find_all('p')[y].find('span').text
	div2_fun('综合运势说明',0)
	div2_fun('爱情运势说明',1)
	div2_fun('事业学业说明',2)
	div2_fun('财富运势说明',3)
	div2_fun('健康运势说明',4)
	data.append(dic)
df = pd.DataFrame(data)
df.to_excel(r"D:\PY\excel_file\cons_crawled.xlsx")

