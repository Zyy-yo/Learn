import pandas as pd

data = pd.read_excel(r"D:\PY\excel_file\cons_crawled.xlsx")
data[['星座','日期']] = data['title'].str.split('运势',expand=True) # 此写法必须要expand=True
data.drop(columns='title', inplace=True)

def clean_col(x):
    data[x] = data[x].str.split(':').str[-1].str.replace('px;','')
clean_col('事业学业')
clean_col('财富运势')
clean_col('综合运势')
clean_col('爱情运势')

def clean_col2(x, y):
    data[x] = data[y].str.split('：').str[-1].str.replace('%','')
    data.drop(columns=y, inplace=True)
clean_col2('健康指数','健康')
clean_col2('商谈指数','商谈')

def clean_col3(x, y):
    data[x] = data[y].str.split('：').str[-1]
    data.drop(columns=y, inplace=True)
clean_col3('幸运数字','数字')
clean_col3('幸运颜色','颜色')
clean_col3('速配星座','速配')

def insert_func(x, y):
    d = data[x]
    data.drop(columns=x, inplace=True)
    data.insert(y, x, d)
labels = ['星座','日期','综合运势','爱情运势','财富运势','事业学业','健康指数','商谈指数','幸运数字','幸运颜色','速配星座']
i = 1
for label in labels:
    insert_func(label, i)
    i += 1

data.to_excel(r'D:\PY\excel_file\constellation_cleaned.xlsx')