import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import os
import seaborn as sns 
from  bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.layouts import gridplot

os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习06_房价影响因素挖掘')

sellp = pd.read_csv('house_sell.csv', encoding='ANSI')     # 买房信息
rentp = pd.read_csv('house_rent.csv', encoding='ANSI')     # 租房信息

def data1():
    # 计算每平方米买房价格及租房价格
    # 计算每平方米售租比（售价/租金）
    sellp1 = sellp[['property_name', 'total_price', 'area', 'lng', 'lat']].copy()
    sellp1 = sellp1[sellp1['area'] > 0].dropna()                                       # 删除空值及面积为0的数据（0不能为分母）
    rentp1 = rentp[['community', 'price', 'area', 'lng', 'lat']].copy()
    rentp1 = rentp1[rentp1['area'] > 0].dropna()

    sellp1['sell_price'] = sellp1['total_price'] * 10000 / sellp1['area']
    sellp2 = sellp1.groupby('property_name').mean()      # 按照小区计算售价均值

    rentp1['rent_price'] = rentp1['price'] / rentp1['area']
    rentp2 = rentp1.groupby('community').mean()        # 按照小区计算租金均值

    s_r = pd.merge(sellp2, rentp2, left_index=True, right_index=True, suffixes=('_x',''))     # 按照小区名合并
    s_r['sell_to_rent'] = round(s_r['sell_price'] / s_r['rent_price'], 2)   # 售租比
    s_r = s_r[['sell_price', 'rent_price', 'lng', 'lat', 'sell_to_rent']]
    s_r.index.name = 'community'
    return s_r
sell_rent = data1().reset_index()

# sell_rent.to_csv('sell_price.csv', index=False)

# output_file('上海房价分布.html')
# hist, edges = np.histogram(sell_rent['sell_price'], bins=80)
# p1 = figure(plot_width=800, plot_height=300, title='上海每平米房价分布')
# p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color='olive')


# hist, edges = np.histogram(sell_rent['rent_price'], bins=80)
# p2 = figure(plot_width=800, plot_height=300, title='上海每平米房屋租金分布')
# p2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color='orange')


# hist, edges = np.histogram(sell_rent['sell_to_rent'], bins=80)
# p3 = figure(plot_width=800, plot_height=300, title='上海每平米售租比分布')
# p3.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color='green')

# p = gridplot([[p1], [p2], [p3]])

# show(p)

# 读取qgis中处理的空间统计数据
data2 = pd.read_excel('空间统计.xlsx')
data2.fillna(0, inplace=True)

def nor(df, *cols):
    # 餐饮密度，道路密度，人口密度指标标准化
    for col in cols:
        df[col+'nor'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    return df
data2_nor = nor(data2, 'length', 'cycount', 'Z')

# 计算每个坐标距离市中心的距离，市中心坐标点：lng-353508.848122，lat-3456140.926976 

data2_nor['距离市中心长度'] = np.sqrt((data2_nor['lng'] - 353508.848122) ** 2 + (data2_nor['lat'] - 3456140.926976) ** 2)
data2_nor = data2_nor[data2_nor['sell_price'] > 0][['cycountnor', 'Znor', 'lengthnor', '距离市中心长度', 'sell_price', 'rent_price']].reset_index(drop=True)
# data2_nor.sort_values('距离市中心长度', inplace=True, ascending=False)


# from scipy import stats

# u = data2_nor['sell_price'].mean()
# std = data2_nor['sell_price'].std()

# print(stats.kstest(data2_nor['sell_price'], 'norm', (u, std)))


# x = data2_nor.corr('pearson')['sell_price']
# print(x)


# def cor_respective(df):
#     # 按照距离市中心每10000米的距离，分别计算指标与房价的相关性
#     l = []
#     item1 = df[df['距离市中心长度'] <= 10000].corr()['sell_price']
#     item1['juli'] = 10000
#     l.append(item1)
#     for i in range(1,6):
#         item2 = df[(df['距离市中心长度'] > 10000 * i) & (df['距离市中心长度'] <= 10000 * (i+1))].corr()['sell_price']
#         item2['juli'] = 10000 * (i+1)
#         l.append(item2)
#     return l

def cor_respective(df):
    # 按照距离市中心每10000米的距离，分别计算指标与房价的相关性
    l = []
    for i in range(10000,70000,10000):
        item1 = df[df['距离市中心长度'] <= i].corr()['sell_price']
        item1['juli'] = i
        l.append(item1)
    return l

cor_r = cor_respective(data2_nor)
df_cor = pd.DataFrame(cor_r)
df_cor.rename(columns={'距离市中心长度': 'center_cor'}, inplace=True)
# print(df_cor)
source = ColumnDataSource(df_cor)

p = figure(plot_width=800, plot_height=300, title='餐饮、路网、人口与房价的关系')
p.line(x='juli', y='cycountnor', source=source, color='green', legend='餐饮密度与房价相关性', line_dash=[4,2])
p.circle(x='juli', y='cycountnor', source=source, color='green')

p.line(x='juli', y='Znor', source=source, color='red', legend='人口密度与房价相关性', line_dash=[3,3])
p.circle(x='juli', y='Znor', source=source, color='red')

p.line(x='juli', y='lengthnor', source=source, color='blue', legend='路网密度与房价相关性', line_dash=[2,7])
p.circle(x='juli', y='lengthnor', source=source, color='blue')

p.line(x='juli', y='center_cor', source=source, color='orange', legend='市中心距离与房价相关性', line_dash=[1,4])
p.circle(x='juli', y='center_cor', source=source, color='orange')

p.legend.location = 'bottom_right'
p.legend.background_fill_alpha = 0.2
show(p)
