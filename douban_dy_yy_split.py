import numpy as np 
import pandas as pd 

path = r"D:\工作\数据分析\微专业\项目数据\豆瓣电影数据.xlsx"

data = pd.read_excel(path)
data = data[['导演', '主演', 'name']].dropna()  # 需要剧名列是为了后面分组做统计
    # 注意先提取需要的字段，再删除缺失值，若在原数据做缺失值删除，会产生不正确的结果

def tq(d):
    # 提取导演和主演，分割成单独的dataframe
    # 分割后的导演和主演文件及原剧名进行合并
    dy = d['导演'].str.split('/', expand=True)
    dy.columns = ['dy'+str(i) for i in dy.columns]

    yy = d['主演'].str.split('/', expand=True)
    yy.columns = ['yy'+str(i) for i in yy.columns]

    d2 = dy.join(yy).join(data['name'])

    return (d2, dy, yy)

data2 = tq(data)[0]

def chuli():
    dy = tq(data)[1]
    yy = tq(data)[2]
    # 建立空dataframe表
    d3 = pd.DataFrame(columns=['导演', '演员', 'name'])
    # 遍历导演和演员的dataframe的列名，将data2中相同的列赋值给新的data_i，每循环一次，将其和data3表连接
    for d in dy.columns:
        for y in yy.columns:
            data_i = data2[[d, y, 'name']].dropna()
            data_i.columns = ['导演', '演员', 'name']
            d3 = pd.concat([d3, data_i])
    return d3

data3 = chuli()

def count():
    c = data3.groupby(['导演', '演员']).count()
    c.reset_index(inplace=True)
    c.rename(columns={'name':'合作次数'}, inplace=True)
    c.to_excel(r'D:\PY\excel_file\gephipri\douban_dy_yy.xlsx', 'sheet1')
    print('finised!')
count()