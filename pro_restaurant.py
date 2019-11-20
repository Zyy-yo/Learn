import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.layouts import gridplot
from bokeh.models.annotations import BoxAnnotation

os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习项目03-上海餐饮店铺选址分析')

data1 = pd.read_excel('上海餐饮数据.xlsx')
data1 = data1.drop_duplicates().dropna(subset=['类别'])
# data1.to_csv('上海餐饮数据1.csv', index=False)  # 导出一份csv数据，方便第二步的QGIS空间分析

# 筛选需要的字段，去除值为0的数据
data1_tq =  data1[['类别', '口味', '环境', '服务', '人均消费']].copy().replace(0, np.nan)
data1_tq = data1_tq.dropna()

# 计算性价比
data1_tq['性价比'] = (data1_tq['口味'] + data1_tq['环境'] + data1_tq['服务']) / data1_tq['人均消费']

# 箱型图查看异常值情况
# data1_tq[['口味', '性价比', '人均消费']].boxplot(whis=3)
# plt.show()

# 分别去除异常值
def ycvalue(df, col):
    q3 = df[col].quantile(0.75)
    q1 = df[col].quantile(0.25)
    ycmax = q3 + 3 * (q3 - q1)
    ycmin = q1 - 3 * (q3 - q1)
    dfc = df[(df[col] < ycmax) & (df[col] > ycmin)][['类别', col]]
    return dfc

kw = ycvalue(data1_tq, '口味')
xf = ycvalue(data1_tq, '人均消费')
xjb = ycvalue(data1_tq, '性价比')

# 指标标准化
def nor(df, col):
    gm = df.groupby('类别').mean()
    gm[col+'_nor'] = (gm[col] - gm[col].min()) / (gm[col].max() - gm[col].min())
    return gm

kw_nor = nor(kw, '口味')
xf_nor = nor(xf, '人均消费')
xjb_nor = nor(xjb, '性价比')

# 各指标数据合并
kw_xf = pd.merge(kw_nor, xf_nor, left_index=True, right_index=True)
data1_final = pd.merge(kw_xf, xjb_nor, left_index=True, right_index=True)

# 字段名称转成英文，增加size字段，方便bokeh绘图
data1_final.index.name = 'type'
data1_final.columns = ['kw', 'kw_nor', 'price', 'price_nor', 'quapri', 'quapri_nor']
data1_final['size'] = data1_final['kw_nor'] * 50

# 数据转换
source = ColumnDataSource(data1_final)

# bokeh绘制散点图和柱状图，并做图表联动
output_file('上海餐饮类型得分.html')

hover1 = HoverTool(tooltips=[('餐饮类型', '@type'),
                             ('人均消费', '@price'),
                             ('口味得分', '@kw_nor'),
                             ('性价比得分', '@quapri_nor')])
p1 = figure(plot_width=800, plot_height=400, title='上海餐饮类型各指标得分',
            tools=[hover1, 'pan, box_select, wheel_zoom, reset, crosshair'])
p1.circle(x='price', y='quapri_nor', size='size', source=source,
        color='goldenrod', fill_alpha=0.5, line_dash='dashed')
# 添加辅助矩形
bx = BoxAnnotation(left=40, right=80, fill_color='gray', fill_alpha=0.05)
p1.add_layout(bx)

p1.xgrid.grid_line_dash = 'dotdash'
p1.ygrid.grid_line_dash = 'dotdash'
p1.xaxis.axis_label = '人均消费'
p1.yaxis.axis_label = '性价比得分'

# 索引'类别'数据转化为列表，方便柱状图设置横坐标范围
data_type = data1_final.index.tolist()
hover2 = HoverTool(tooltips=[('口味得分', '@kw_nor')])
p2 = figure(plot_width=800, plot_height=400, title='口味得分', x_range = data_type,
            tools=[hover2, 'pan, box_select, wheel_zoom, reset, crosshair'])
p2.vbar(x='type', top='kw_nor', width=0.5, source=source, color='green', alpha=0.6)
p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_dash = 'dotdash'
p2.xaxis.axis_label = '餐饮类型'
p2.yaxis.axis_label = '口味得分'

hover3 = HoverTool(tooltips=[('性价比得分', '@quapri_nor')])
p3 = figure(plot_width=800, plot_height=400, title='性价比得分', x_range = p2.x_range,
            tools=[hover3, 'pan, box_select, wheel_zoom, reset, crosshair'])
p3.vbar(x='type', top='quapri_nor', width=0.5, source=source, color='navy', alpha=0.6)
p3.xgrid.grid_line_color = None
p3.ygrid.grid_line_dash = 'dotdash'
p3.xaxis.axis_label = '餐饮类型'
p3.yaxis.axis_label = '性价比得分'

# 图表联动
p = gridplot([[p1], [p2], [p3]])
show(p)


# 商铺选址分析

data2 = pd.read_excel('空间统计.xlsx')

data2.rename(columns={'Z': 'pop'}, inplace=True)

# 指标标准化，人口密度、餐饮热度、道路密度越高越好，同类竞品越少越好
def nor2(df, *cols):
    dfc = df.copy()
    for col in cols:
        dfc[col+'_nor'] = (dfc[col] - dfc[col].min()) / (dfc[col].max() - dfc[col].min())
    dfc['sc_nor'] = (dfc['sc'].max() - dfc['sc']) / (dfc['sc'].max() - dfc['sc'].min())
    dfc['finalscore'] = dfc['pop_nor'] * 0.4 + dfc['cy_nor'] * 0.3 + dfc['rdlength_nor'] * 0.2 + dfc['sc_nor'] * 0.1
    dfc = dfc.sort_values('finalscore', ascending=False).reset_index(drop=True)
    return dfc

data2_nor = nor2(data2, 'pop', 'cy', 'rdlength')
data2_nor['size'] = data2_nor['finalscore'] * 20
data2_nor['color'] = 'green'
data2_nor['color'].iloc[:10] = 'red'

source = ColumnDataSource(data2_nor)

output_file('上海素菜馆选址分析.html')
hover4 = HoverTool(tooltips=[('经度', '@lng'),
                             ('纬度', '@lat'),
                             ('综合得分', '@finalscore')])
p4 = figure(plot_width=500, plot_height=600, title='上海素菜馆选址分析',
            tools=[hover4, 'pan, box_select, wheel_zoom, reset'],
            x_axis_label='经度', y_axis_label='纬度')
p4.square(x='lng', y='lat', source=source, size='size', color='color', fill_alpha=0.7,
          line_color='black', line_alpha=0.5)
p4.xgrid.grid_line_color=None
p4.ygrid.grid_line_color=None

show(p4)