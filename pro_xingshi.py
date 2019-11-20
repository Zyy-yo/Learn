import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import os
import warnings
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.models import HoverTool

warnings.filterwarnings('ignore')


os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习05_中国姓氏排行研究')

def load():
    # 读取数据
    d1 = pd.read_csv('data01.csv')
    d2 = pd.read_csv('data02.csv')
    d2['户籍地城市编号'] = d2['户籍地城市编号'].astype(np.str).str[:-2]    # 处理浮点型编号字段

    d3 = pd.read_excel('中国行政代码对照表.xlsx', sheet_name=0)
    d3['行政编码'] = d3['行政编码'].astype(np.str)              # 处理整型编码字段
    d3 = d3.add_prefix('户籍地_')
    # 合并数据
    d12 = pd.concat([d1,d2]).reset_index(drop=True)
    d123 = pd.merge(d12, d3, left_on='户籍地城市编号', right_on='户籍地_行政编码', how='left')
    return d123
data = load()
# print(data.head())
# pd.set_option('display.max_columns', None)

def work_place(dfc):
    # 分割工作地，获取工作地省市区字段
    dfc['省'] = dfc['工作地'].str.split('省').str[0]
    dfc['市'] = dfc['工作地'].str.split('省').str[-1].str.split('市').str[0]

    dfc['区县'] = ''
    dfc['区县'][dfc['工作地'].str.contains('区')] = dfc['工作地'].str.split('市', n=1).str[-1].str.split('区').str[0] + '区'
    dfc['区县'][dfc['工作地'].str.contains('县')] = dfc['工作地'].str.split('市', n=1).str[-1].str.split('县').str[0] + '县'
    

    dfc['省'][dfc['省'].str.len() > 4] = '未识别'
    dfc['市'][dfc['市'].str.len() > 4] = '未识别'
    dfc['区县'][(dfc['区县'].str.len() < 2) | (dfc['区县'].str.len() > 5)] = '未识别'
    del dfc['户籍地城市编号']
    del dfc['户籍地_行政编码']
    return dfc

data1 = work_place(data)

'''
查看姓氏“普遍指数”，普遍指数=姓氏人口数量
    将数据按照“姓”做统计，找到数量最多的TOP20
    分别制作图表，查看姓氏TOP20的数量及占比
'''

# def coun_per():
#     # 姓氏统计
#     data2 = data1['姓'].value_counts()
#     xscount = pd.DataFrame(data2)
#     xscount.columns = ['count']
#     xscount.index.name = 'firstname'
#     xscount['percent'] = xscount['count'] / xscount['count'].sum()
#     return xscount[:20]
# xstop20 = coun_per()

# firstnames = xstop20.index.tolist()
# source = ColumnDataSource(xstop20)

# output_file('中国姓氏占比排行前20.html')

# hover1 = HoverTool(tooltips=[('数量', '@count')])
# p1 = figure(x_range=firstnames, plot_width=800, plot_height=300, title='姓氏计数-前20',
#             tools=[hover1, 'pan, wheel_zoom, box_zoom, box_select, reset'])
# p1.vbar(x='firstname', top='count', width=0.8, source=source, fill_color='red',
#         fill_alpha=0.5, line_color='goldenrod', line_alpha=0.8, line_dash='dotted')

# hover2 = HoverTool(tooltips=[('占比', '@percent')])
# p2 = figure(x_range=p1.x_range, plot_width=800, plot_height=300, title='姓氏占比-前20',
#             tools=[hover2, 'pan, wheel_zoom, box_zoom, box_select, reset'])
# p2.vbar(x='firstname', top='percent', width=0.8, source=source, fill_color='orange',
#         fill_alpha=0.5, line_color='goldenrod', line_alpha=0.8, line_dash='dotted')

# f = gridplot([[p1], [p2]])
# show(f)

# 利用powermap查看王姓和姬姓的全国分布

# 导出这俩姓氏

# wangx = data1[data1['姓'] == '王'].copy()
# jix = data1[data1['姓'] == '姬'].copy()

# wangx.to_excel('王姓筛选.xlsx')
# jix.to_excel('姬姓筛选.xlsx')

'''
查看姓氏“奔波指数”，奔波指数=姓氏人均迁徙距离。
迁徙距离为户籍地所在地级市与现居住地所在地级市的距离。
'''

data2 = data1[data1['姓'] == '汤'].copy().dropna()
data3 = data2[(data2['市'] != '未识别') & (data2['市'] != '')][['姓', '工作地', '户籍地_lng', '户籍地_lat', '市']]

data3.to_excel('tang.xlsx', index=False)

print('D-O-N-E')


