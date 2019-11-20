import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.layouts import gridplot 
from bokeh.models import HoverTool
from bokeh.models.widgets import Panel, Tabs
import warnings

warnings.filterwarnings('ignore')


os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习04_电商打折套路解析')

data = pd.read_excel('双十一淘宝美妆数据.xlsx', index_col=0)

# print(data.info()) # 无缺失数据
'''
计算得到：商品总数、品牌总数
双十一当天在售的商品占比情况
'''

data['date'] = data.index.day     # 提取销售日期成为新的字段

data1 = data[['id', 'title', '店名', 'date']]    # 提取需要的数据字段

df1 = data1[['id', 'date']].groupby('id').agg(['min', 'max'])['date']  # 最后再提取['date']不会让date成为多重索引

id_11 = data1[data1['date'] == 11]['id'].unique()  # 提取销售日期为11号的产品id
df2 = pd.DataFrame({'id': id_11, '双十一当天售卖': True})     # 将双十一当天售卖的产品id放到新的表里

id_date = pd.merge(df1, df2, left_index=True, right_on='id', how='left')   # 合并df1和df2
id_date['双十一当天售卖'].fillna(False, inplace=True)

c = len(data1['id'].unique())
c11 = len(id_11)
c11_rat = (c11 / c) * 100
print('商品总数有 %i 个，双十一当天活动产品有 %i 个，占总产品的 %.2f%%'%(c, c11, c11_rat))


'''
   A. 11.11前后及当天都在售 → 一直在售
   B. 11.11之后停止销售 → 双十一后停止销售
   C. 11.11开始销售并当天不停止 → 双十一当天上架并持续在售
   D. 11.11开始销售且当天停止 → 仅双十一当天有售
   E. 11.5 - 11.10 → 双十一前停止销售
   F. 仅11.11当天停止销售 → 仅双十一当天停止销售
   G. 11.12开始销售 → 双十一后上架
'''

id_date['type'] = '待分类'
id_date['type'][(id_date['min'] < 11) & (id_date['max'] > 11) & (id_date['双十一当天售卖'] == True)] = 'A'
id_date['type'][(id_date['min'] < 11) & (id_date['max'] == 11)] = 'B'
id_date['type'][(id_date['min'] == 11) & (id_date['max'] > 11)] = 'C'
id_date['type'][(id_date['min'] == 11) & (id_date['max'] == 11)] = 'D'
id_date['type'][id_date['max'] < 11] = 'E'
id_date['type'][(id_date['min'] < 11) & (id_date['max'] > 11) & (id_date['双十一当天售卖'] == False)] = 'F'
id_date['type'][id_date['min'] > 11] = 'G'

result1 = id_date['type'].value_counts()
result1 = result1.loc[['A', 'C', 'B', 'D', 'E', 'F', 'G']] # 调整顺序，ABCD为双十一有售的，且BD之后停售；EFG未参与双十一

from bokeh.palettes import brewer
color = brewer['Set1'][7]

fig = plt.figure(figsize=(8,5))
plt.pie(result1, autopct='%.2f%%', labels=result1.index, colors=color, startangle=90, counterclock=False)

# plt.show()

'''
未参与双十一当天活动的商品，在双十一之后的去向如何？
可能有四种情况：
   con1 → 暂时下架（F）
   con2 → 重新上架（E中部分数据，数据中同一个id可能有不同title，“换个马甲重新上架”）
   con3 → 预售（E中部分数据，预售商品的title中包含“预售”二字），字符串查找特定字符 dataframe.str.contains('预售')
   con4 → 彻底下架（E中部分数据），可忽略
'''

id_not11 = id_date[id_date['双十一当天售卖'] == False]  # 筛选未参加双十一活动的产品
cnot11 = len(id_not11)
cnot11_rat = (cnot11 / c) * 100
print('未参加双十一的产品有 %i 个，占总产品的 %.2f%%'%(cnot11, cnot11_rat))
print('未参加双十一的产品销售节奏有：', id_not11['type'].unique())
# print(id_not11.head())


data2 = id_not11[['id', 'type']]    # 提取未参加双十一产品id和销售节奏类型
df3 = pd.merge(data2, data, on='id', how='left')      # 与原数据合并，筛选出未参加双十一活动产品的原数据


id_con1 = id_date['id'][id_date['type'] == 'F'].values        # 筛选出暂时下架的产品id

data_con2 = df3[['id', 'title', 'date']].groupby(['id', 'title']).count()  # 按照id和title分组
data_con2.reset_index(inplace=True) # 重设索引
title_count = data_con2['id'].value_counts()  # 计数，如果同一个id次数大于1，则证明有多个title
id_con2 = title_count[title_count > 1].index  # 筛选出重新上架的产品id

data_con3 = df3[df3['title'].str.contains('预售')]  # 筛选标题中包含预售的产品
id_con3 = data_con3['id'].unique()         # 筛选预售产品的id

print('未参与双十一活动的产品中，暂时下架的有 %i 个，重新上架过的产品有 %i 个，预售产品有 %i 个'\
      %(len(id_con1), len(id_con2), len(id_con3)))


'''
真正参与双十一活动的品牌有哪些？（双十一当天在售的商品 + 预售商品）
其各个品牌参与双十一活动的商品数量分布是怎样的？
'''

id_11sale = np.hstack((id_11, id_con3))           # 双十一当天在售的商品id_11 + 预售商品id_con3
result2 = pd.DataFrame({'id': id_11sale})   
c11sale = len(result2)        # 真正参与双十一活动的产品数量
print('真正参与了双十一活动的产品数量有 %i 个，占总产品的 %.2f%%'%(c11sale, (c11sale / c) * 100))

data1_uniqueid = data1.groupby(['店名', 'id'])['date'].count()  # 处理data1的数据，使它的id唯一（若不处理，下面统计的id数量就不对）
data1_uniqueid2 = data1_uniqueid.reset_index()

id_11_df = pd.DataFrame({'id': id_11})
s11 = pd.merge(id_11_df, data1_uniqueid2, on='id', how='left')      # 从处理好的数据中筛选参加双十一当天活动的产品数据
s11_g = s11.groupby('店名')['id'].count()          # 计算不同品牌参加双十一当天活动产品的数量
s11_g.name = '当天参加双十一活动产品数量'

id_con3_df = pd.DataFrame({'id': id_con3})
s11_ys = pd.merge(id_con3_df, data1_uniqueid2, on='id', how='left')    # 从处理好的数据中筛选预售产品数据
s11_ys_g = s11_ys.groupby('店名')['id'].count()       # 计算不同品牌预售产品的数量
s11_ys_g.name = '预售产品数量'

result3 = pd.merge(s11_g, s11_ys_g, left_index=True, right_index=True)  
result3['真正参与双十一活动产品总数'] = result3['当天参加双十一活动产品数量'] + result3['预售产品数量']
result3.sort_values('真正参与双十一活动产品总数', ascending=False, inplace=True)
# print(result3)

# 绘制堆叠柱状图
from bokeh.core.properties import value
# output_file('双十一活动产品数量分布.html')

result3.columns = ['s11_sale', 'pre_sale', 'sale_sum']
result3.index.name = 'brand'

columns = result3.columns.tolist()[:2]
index = result3.index.tolist()

source = ColumnDataSource(result3)
colors = ['skyblue', 'tomato']
hover = HoverTool(tooltips=[('预售商品数量', '@pre_sale'),
                            ('当天参加双十一活动产品数量', '@s11_sale'),
                            ('真正参与双十一活动的产品数', '@sale_sum')])
p1 = figure(plot_width=800, plot_height=300, title='各品牌参与双十一活动产品数量分布',
            x_range=index, tools=[hover, 'pan, box_select, wheel_zoom, box_zoom, reset'])

p1.vbar_stack(columns, x='brand', width=0.8, source=source, color=colors, 
            legend=[value(x) for x in columns], muted_color='gray', muted_alpha=0.3)
p1.legend.click_policy = 'mute'
p1.legend.orientation = 'horizontal'
p1.xgrid.grid_line_color = None
p1.axis.minor_tick_line_color = None
p1.xaxis.major_label_orientation = 120
# show(p1)
tab1 = Panel(child=p1, title='双十一美妆品牌产品分布')


'''
哪些商品真的在打折呢？
   针对每个商品，评估其打折的情况
   针对在打折的商品，其折扣率是多少
   按照品牌分析，不同品牌的打折力度
'''

data3 = data.copy()
# 按照date日期分为三部分
data3['period'] = pd.cut(data3['date'], bins=[4, 10, 11, 14], labels=['双十一前', '双十一', '双十一后'])
# print(data3.head())

# 按照id和period分组，得出每个时期的最低价格
price = data3[['id', '店名', 'price', 'period']].groupby(['id', 'period']).min()
price.reset_index(inplace=True)

p1 = price[price['period'] == '双十一前']    # 筛选双十一前产品
p2 = price[price['period'] == '双十一']      # 筛选双十一当天产品

prices = pd.merge(p1, p2, on='id', suffixes=('_前', '_当天'))     # 合并以上两个表格
prices['disco_rat'] = prices['price_当天'] / prices['price_前']      # 计算打折商品的折扣率
pri_z = prices[prices['price_当天'] < prices['price_前']]         # 筛选出打折商品
dzzb = len(pri_z) / c * 100                                        # 打折商品占总商品的比例

print('打折商品占比 %.2f%%'%dzzb)

# # 绘制折扣率图表，x轴为折扣率，y轴为折扣率占比

price_rat = pri_z[['id', 'disco_rat']]            # 筛选所需字段
price_rat['range'] = pd.cut(price_rat['disco_rat'], bins=np.linspace(0,1,21))  # 以0.05的区间将折扣率做分组
price_rat2 = price_rat.groupby('range').count().iloc[:-1]   # 统计每个组的数量，去掉折扣率0.95以上的，即最后一个(0.95, 1.0]区间
price_rat2['disco_rat_per'] = price_rat2['disco_rat'] / price_rat2['disco_rat'].sum()  # 折扣率区间占比
price_rat2.index = price_rat2.index.astype(np.str)      # 改变索引的数据类型，原分组类型interval无法作图

source1 = ColumnDataSource(price_rat2)
indexes = price_rat2.index.tolist()

# output_file('商品折扣率统计.html')
hover = HoverTool(tooltips=[('该折扣区间商品数', '@disco_rat'),
                            ('折扣率占比', '@disco_rat_per')])
p2 = figure(x_range=indexes, plot_width=800, plot_height=400, title='商品折扣率', 
            tools=[hover, 'pan, box_select, wheel_zoom, reset'],
            x_axis_label='折扣区间', y_axis_label='折扣占比')
p2.line(x='range', y='disco_rat_per', source=source1, line_color='coral')
p2.circle(x='range', y='disco_rat_per', source=source1, size=8, fill_color=None)
p2.xaxis.major_label_orientation = 120
# show(p2)
tab2 = Panel(child=p2, title='折扣率分布区间')

# 绘制各品牌打折力度散点图
from bokeh.transform import jitter

brands = prices['店名_前'].dropna().unique()        # 从双十一前后价格表 prices 中筛选品牌
dazhe = prices[['id', '店名_前', 'disco_rat']]        # 筛选所需字段
dazhe = dazhe[dazhe['disco_rat'] <= 0.95]             # 筛选折扣率0.95及以下数据

source2 =  ColumnDataSource(dazhe)
# output_file('不同品牌打折力度.html')

hover = HoverTool(tooltips=[('折扣率', '@disco_rat')])
p3 = figure(y_range=brands, plot_width=800, plot_height=500, title='不同品牌打折力度',
            tools=[hover, 'pan, box_select, wheel_zoom, reset'])
p3.circle(x='disco_rat', y=jitter('店名_前', width=0.6, range=p3.y_range), source=source2, alpha=0.4)
p3.ygrid.grid_line_color = None
# show(p3)
tab3 = Panel(child=p3, title='各品牌折扣率分布')


'''
商家营销套路挖掘？
解析出不同品牌的参与打折商品比例及折扣力度，并做散点图，总结打折套路
   用bokeh绘制散点图，x轴为参与打折商品比例，y轴为折扣力度，点的大小代表该品牌参加双11活动的商品总数
提示：
① 折扣力度为该品牌所有打折商品的折扣均值，这里去掉品牌中不打折的数据
② 绘制散点图后，可以将x、y轴绘制均值辅助线，将绘图空间分为四个象限，基于该象限来总结套路
'''

dzld = dazhe.groupby('店名_前')['disco_rat'].mean()      # 不同品牌折扣力度(取折扣率均值)，从已筛选的95折以下数据 dazhe 中计算
dzsps = dazhe['店名_前'].value_counts()           # 打折商品数
spzs = result3['s11_sale']                  # 参加双11活动的商品总数(不算预售商品)

dzbl = pd.DataFrame({'打折商品数':dzsps,'商品总数':spzs})     
dzbl['参与打折商品比例'] = dzbl['打折商品数'] / dzbl['商品总数']  # 不同品牌参与打折的商品占比
dzbl.dropna(inplace=True)       # 删除空值（未打折的品牌）

dzmer = pd.merge(dzld, dzbl, left_index=True, right_index=True) # 合并打折力度和打折比例表格（索引为店名）

# bokeh绘制图表
from bokeh.models.annotations import Span, Label, BoxAnnotation

dzbl_final = dzmer[['disco_rat', '参与打折商品比例', '商品总数']]  # 筛选所需字段
dzbl_final.columns = ['disco_rat', 'dzspbl', 'spzs']
dzbl_final.index.name = 'brand'
dzbl_final['size'] = dzbl_final['spzs'] * 0.3

bljz = dzbl_final['dzspbl'].mean()      # 参与打折商品占比的均值
zkjz = dzbl_final['disco_rat'].mean()       # 折扣力度均值

source3 = ColumnDataSource(dzbl_final)

output_file('美妆品牌双十一打折解析.html')
hover = HoverTool(tooltips=[('品牌', '@brand'),
                            ('折扣率', '@disco_rat'),
                            ('商品总数', '@spzs'),
                            ('参与打折商品比例', '@dzspbl')])
p4 = figure(plot_width=600, plot_height=500, title='各品牌打折套路解析',
            tools=[hover, 'pan, box_zoom, wheel_zoom, box_select, reset'],
            x_axis_label='参与打折商品比例', y_axis_label='折扣率')
p4.circle_x(x='dzspbl', y='disco_rat', source=source3, size='size', fill_color='red',
         fill_alpha=0.7, line_color='black', line_alpha=0.6, line_dash=[8,4])
p4.xgrid.grid_line_dash = 'dotted'
p4.ygrid.grid_line_dash = 'dotted'
x = Span(location=bljz, dimension='height', line_color='green', line_width=2, line_dash=[2,3])
y = Span(location=zkjz, dimension='width', line_color='green', line_width=2, line_dash=[2,3])
p4.add_layout(x)
p4.add_layout(y)

# 左上角区域
box1 = BoxAnnotation(bottom=zkjz, right=bljz, fill_color='yellow', fill_alpha=0.1)
label1 = Label(x=0.18, y=0.8, text='少量少打折', text_font_size='10pt')
p4.add_layout(box1)
p4.add_layout(label1)

# 右上角区域
box2 = BoxAnnotation(bottom=zkjz, left=bljz, fill_color='orange', fill_alpha=0.1)
label2 = Label(x=0.7, y=0.8, text='大量少打折', text_font_size='10pt')
p4.add_layout(box2)
p4.add_layout(label2)

# 左下角区域
box3 = BoxAnnotation(top=zkjz, right=bljz, fill_color='orange', fill_alpha=0.1)
label3 = Label(x=0.18, y=0.55, text='少量大打折', text_font_size='10pt')
p4.add_layout(box3)
p4.add_layout(label3)

# 右下角区域
box4 = BoxAnnotation(top=zkjz, left=bljz, fill_color='yellow', fill_alpha=0.1)
label4 = Label(x=0.7, y=0.55, text='大量大打折', text_font_size='10pt')
p4.add_layout(box4)
p4.add_layout(label4)

# show(p4)
tab4 = Panel(child=p4, title='打折套路最终分析')

zt = Tabs(tabs=[tab1, tab2, tab3, tab4])   # 终图

show(zt)
