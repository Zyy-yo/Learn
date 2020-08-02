import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
# import seaborn as sn
import re

plt.rcParams['axes.unicode_minus'] = False

def change_colname(s, oldname, newname):
    return s.replace(oldname, newname)


# 对话
path1 = r'd:\data_all\对话留电\6月.xlsx'  
path2 = r'd:\data_all\7月.xlsx'

data1 = pd.read_excel(path1, sheet_name='留电')
data2 = pd.read_excel(path2, sheet_name='留电')

data1['来源'] = change_colname(data1['来源'], '支付宝口碑', '口碑')
data1['来源'] = change_colname(data1['来源'], '淘宝天猫/阿里健康', '天猫')
data1['来源'] = change_colname(data1['来源'], '大众点评/美团', '大众')

data2['来源'] = change_colname(data2['来源'], '支付宝口碑', '口碑')
data2['来源'] = change_colname(data2['来源'], '淘宝天猫/阿里健康', '天猫')
data2['来源'] = change_colname(data2['来源'], '大众点评/美团', '大众')

# 选择日期
data1 = data1[(data1['日期'] >= '2020-06-01') & (data1['日期'] < '2020-06-30')]
data2 = data2[(data2['日期'] >= '2020-07-01') & (data2['日期'] < '2020-07-30')]

'''
分平台总对话量对比情况分析
'''
# 按平台统计对话量
last_zdh_groupby_pingtai = data1.groupby('来源')['对话'].sum()
next_zdh_groupby_pingtai = data2.groupby('来源')['对话'].sum()

# 合并两个对话表
last_next_zdh = pd.merge(last_zdh_groupby_pingtai, next_zdh_groupby_pingtai, left_index=True, right_index=True, suffixes=('_上月', '_本月'))
last_next_zdh['同比'] = last_next_zdh['对话_本月'] / last_next_zdh['对话_上月'] - 1
# print(last_next_zdh)

# 文字标注函数
def show_text(value, deviation1, deviation2, color, reference=None):
    '''
    reference：百分比，或None。默认None，百分比类数据选择百分比
    deviation1: 横坐标偏移值
    deviation2: 纵坐标偏移值
    '''
    if reference == '百分比':
        for i, j in enumerate(value):
            if np.isnan(j):
                continue
            else:
                plt.text(i + deviation1, j + deviation2, '%.0f%%'%(j * 100), color=color)
    else:
        for i, j in enumerate(value):
            plt.text(i + deviation1, j + deviation2, '%.0f'%j, color=color)

# 绘制对话量柱状图
def fig_dh(axis, df, collast, colnext, title, ylabelname1, ylabelname2='百分比'):
    '''
    collast：上期数据字段名
    colnext：本期数据字段名
    title：图表标题
    ylabelname1: 纵坐标主轴名
    ylabelname2: 纵坐标副轴名
    '''
    axis.bar(df.index, df[collast], color='burlywood', width=0.3)
    show_text(df[collast], -0.1, 0, 'black')
    axis.bar(np.arange(len(df.index)) + 0.3, df[colnext], color='cyan', width=0.3)
    show_text(df[colnext], 0.2, 0, 'black')
    plt.legend(['上月', '本月'])
    plt.xticks(rotation=10)
    axis.set_ylabel(ylabelname1)
    plt.title('%s'%title)

    # 绘制副坐标轴，对话增长率
    axis2 = axis.twinx()
    axis2.scatter(np.arange(len(df.index)) + 0.3, df['同比'], color='r', alpha=0.6)
    plt.legend(['增长率'], loc=(0.05, 0.9))
    axis2.set_ylabel(ylabelname2)
    axis2.axhline(0, linestyle='--', linewidth=0.6, color='gray', alpha=0.7)
    show_text(df['同比'], 0.3, 0, 'black', '百分比')

fig1, axis1 = plt.subplots(figsize=(7, 3))
fig_dh(axis1, last_next_zdh, '对话_上月', '对话_本月', '各平台对话对比', '对话量')


'''
各平台分科室对话对比
'''
def last_next_mer(merleft, merright, colnext, collast, newcolnext, newcollast):
    df = pd.merge(merleft, merright, left_index=True, right_index=True, how='outer', suffixes=('_上月', '_本月'))
    df = df.fillna(0)
    df['同比'] = np.nan
    for i in df.copy().iterrows():
        if i[1][collast] == 0:
            df.loc[i[0], '同比'] = np.nan
        elif i[1][collast] < 0:
            df.loc[i[0], '同比'] = i[1][colnext] / abs(i[1][collast]) + 1
        else:
            df.loc[i[0], '同比'] = i[1][colnext] / i[1][collast] - 1
    df = df.rename(columns={collast: newcollast, colnext: newcolnext})
    return df



# last_pt_pf_dh = data1[data1['科室'] == '皮肤科'].groupby(['来源'])['对话'].sum()   # 上期皮肤科对话
# last_pt_wk_dh = data1[data1['科室'] == '外科'].groupby(['来源'])['对话'].sum()   # 上期外科对话

# next_pt_pf_dh = data2[data2['科室'] == '皮肤科'].groupby(['来源'])['对话'].sum()   # 本期皮肤科对话
# next_pt_wk_dh = data2[data2['科室'] == '外科'].groupby(['来源'])['对话'].sum()   # 本期外科对话

# pt_pf_dh = last_next_mer(last_pt_pf_dh, next_pt_pf_dh, '对话_本月', '对话_上月', '本月', '上月')
# pt_wk_dh = last_next_mer(last_pt_wk_dh, next_pt_wk_dh, '对话_本月', '对话_上月', '本月', '上月')


# fig12, axis_12 = plt.subplots(figsize=(7, 3))
# fig_dh(axis_12, pt_pf_dh, '上月', '本月', '各平台皮肤科对话对比', '对话量')

# fig13, axis_13 = plt.subplots(figsize=(7, 3))
# fig_dh(axis_13, pt_wk_dh, '上月', '本月', '各平台外科对话对比', '对话量')
# print(pt_wk_dh)

# # 网络部整体总对话、皮肤科、外科对话对比

# last_zdh_wl = last_zdh_groupby_pingtai.sum()
# next_zdh_wl = next_zdh_groupby_pingtai.sum()

# last_zdh_pf_wl = last_pt_pf_dh.sum()
# next_zdh_pf_wl = next_pt_pf_dh.sum()

# last_zdh_wk_wl = last_pt_wk_dh.sum()
# next_zdh_wk_wl = next_pt_wk_dh.sum()


# pf_wk_zdh_wl = pd.DataFrame([[last_zdh_wl, next_zdh_wl],
#                               [last_zdh_pf_wl, next_zdh_pf_wl],
#                               [last_zdh_wk_wl, next_zdh_wk_wl]],
#                               index=['总计', '皮肤科', '外科'],
#                               columns=['上月', '本月'])
# pf_wk_zdh_wl['同比'] = pf_wk_zdh_wl['本月'] / pf_wk_zdh_wl['上月'] - 1

# fig14, axis_14 = plt.subplots(figsize=(7, 3))
# fig_dh(axis_14, pf_wk_zdh_wl, '上月', '本月', '网络部整体对话对比', '对话量')


'''
对话结构占比情况， 以下此代码新增
'''

# 皮肤科、外科占比及对比
def fig_pie(axis, df, titlename, explodes=0.04):
    df = df.sort_values(ascending=False)
    length = len(df.index)
    axis.pie(df, explode=[explodes] * length, colors=plt.get_cmap('Set3')(np.linspace(0.1, 0.9, length)), 
             autopct='%.0f%%', pctdistance=0.8, labeldistance=1.1, shadow=True, startangle=90)
    axis.set_title(titlename, fontsize='small')
    axis.legend(df.index, loc=(1, 0.1), fontsize='small')

# 对项目分类进行处理，减少字数
def change_colname_manyitems(df):
    '''
    缩短外科项目名称
    '''
    dfc = df.copy()
    for i in df.iterrows():
        if '形' in i[1]['项目']:
            j = re.match(r'(\S{2}).形$', i[1]['项目']).group(1)
            dfc.loc[i[0], '项目'] = j
        if i[1]['项目'] == '自体脂肪':
            dfc.loc[i[0], '项目'] = '脂肪'
    return dfc
    
data1_c = change_colname_manyitems(data1)
data2_c = change_colname_manyitems(data2)


# print(data1_c.head(10))
last_dh_pf_wk_groupby_keshi = data1_c.groupby(['科室'])['对话'].sum()  # 上期对话皮肤科、外科占比
next_dh_pf_wk_groupby_keshi = data2_c.groupby(['科室'])['对话'].sum()

last_dh_pf_groupby_xiangmu = data1_c[data1_c['科室'] == '皮肤科'].groupby('项目')['对话'].sum()   # 上期皮肤科对话项目占比
next_dh_pf_groupby_xiangmu = data2_c[data2_c['科室'] == '皮肤科'].groupby('项目')['对话'].sum()   # 本期皮肤科对话项目占比

last_dh_wk_groupby_xiangmu = data1_c[data1_c['科室'] == '外科'].groupby('项目')['对话'].sum()   # 上期外科对话项目占比
next_dh_wk_groupby_xiangmu = data2_c[data2_c['科室'] == '外科'].groupby('项目')['对话'].sum()   # 本期外科对话项目占比

fig15, axis_15 = plt.subplots(2, 3, figsize=(12, 6))
fig15.suptitle('\n对话结构占比对比图')

fig_pie(axis_15[0, 0], last_dh_pf_wk_groupby_keshi, '上月科室对话占比')      # 科室对话占比
fig_pie(axis_15[1, 0], next_dh_pf_wk_groupby_keshi, '本月科室对话占比')

fig_pie(axis_15[0, 1], last_dh_pf_groupby_xiangmu, '上月皮肤科对话项目占比')      # 皮肤科项目占比
fig_pie(axis_15[1, 1], next_dh_pf_groupby_xiangmu, '本月皮肤科对话项目占比')

fig_pie(axis_15[0, 2], last_dh_wk_groupby_xiangmu, '上月外科对话项目占比')      # 外科项目占比
fig_pie(axis_15[1, 2], next_dh_wk_groupby_xiangmu, '本月外科对话项目占比')
# plt.savefig(r'd:\PY\figures\data_analysis_gbs\对话结构占比.jpg')




'''
各平台分科室对话对比分析,暂放
'''


# '''
# 各平台业绩对比分析
# '''

# path3 = r'd:\data_all\客户信息\6月客户信息总表.xlsx'
# path4 = r'd:\data_all\日报\总表\7月\运营数据_7.30.xlsx'

# import month_kehu

# data3 = pd.read_excel(path3, sheet_name='Sheet1')
# data4 = pd.read_excel(path4, sheet_name='客户数据月累计')

# # 选择日期
# data3 = data3[(data3['日期'] >= '2020-06-01') & (data3['日期'] < '2020-06-30')]
# data4 = data4[(data4['日期'] >= '2020-07-01') & (data4['日期'] < '2020-07-30')]


# # 客户信息源数据处理
# def pro_data(data):
#     '''
#     data：需要处理的数据，源数据为客户月累计中的数据格式
#     '''
#     yej_he = month_kehu.keshi_yej(data)
#     return yej_he

# last_zyj = pro_data(data3)
# next_zyj = pro_data(data4)

# def change_colname(s, oldname, newname):
#     return s.replace(oldname, newname)

# last_zyj['二级来源'] = change_colname(last_zyj['二级来源'], '支付宝口碑', '口碑')
# last_zyj['二级来源'] = change_colname(last_zyj['二级来源'], '淘宝天猫/阿里健康', '天猫')
# last_zyj['二级来源'] = change_colname(last_zyj['二级来源'], '大众点评/美团', '大众')

# next_zyj['二级来源'] = change_colname(next_zyj['二级来源'], '支付宝口碑', '口碑')
# next_zyj['二级来源'] = change_colname(next_zyj['二级来源'], '淘宝天猫/阿里健康', '天猫')
# next_zyj['二级来源'] = change_colname(next_zyj['二级来源'], '大众点评/美团', '大众')


# # 各平台新老客业绩
# def yj_groupby_pingtai_keshi(df, chuorfu):
#     df['初复诊'] = df['初复诊'].replace('未到院', '初诊')
#     df_1 = df[df['初复诊'] == chuorfu].groupby(['来源分类', '二级来源'])['sum'].sum()  
#     df_1 = df_1.loc['网络渠道']
#     df_1 = df_1 / 10000
#     return df_1
# last_chu_wl = yj_groupby_pingtai_keshi(last_zyj, '初诊')
# last_fu_wl = yj_groupby_pingtai_keshi(last_zyj, '复诊')
# next_chu_wl = yj_groupby_pingtai_keshi(next_zyj, '初诊')

# next_fu_wl = yj_groupby_pingtai_keshi(next_zyj, '复诊')

# # 2个时期业绩合并
# def last_next_mer(merleft, merright, colnext, collast, newcolnext, newcollast):
#     df = pd.merge(merleft, merright, left_index=True, right_index=True, how='outer', suffixes=('_上月', '_本月'))
#     df = df.fillna(0)                    # 解决空值时，画图出现posx and posy should be finite values问题
#     df['同比'] = np.nan
#     for i in df.copy().iterrows():
#         if i[1][collast] == 0:
#             df.loc[i[0], '同比'] = np.nan
#         elif i[1][collast] < 0:
#             df.loc[i[0], '同比'] = i[1][colnext] / abs(i[1][collast]) + 1
#         else:
#             df.loc[i[0], '同比'] = i[1][colnext] / i[1][collast] - 1
#     df = df.rename(columns={collast: newcollast, colnext: newcolnext})
#     return df

# # 新老客业绩分别对比
# chu_last_next = last_next_mer(last_chu_wl, next_chu_wl, 'sum_本月', 'sum_上月', '新客_本月', '新客_上月')
# fu_last_next = last_next_mer(last_fu_wl, next_fu_wl, 'sum_本月', 'sum_上月', '老客_本月', '老客_上月')


# # 新老客对比图
# def fig_s(axis, df, collast, colnext, titlename):
#     axis.bar(df.index, df[collast], width=0.3, color='burlywood')
#     show_text(df[collast], -0.1, 0, 'black', None)
#     axis.bar(np.arange(len(df.index)) + 0.3, df[colnext], width=0.3, color='cyan')
#     show_text(df[colnext], 0.2, 0, 'black', None)
#     plt.title('%s业绩对比'%titlename)
#     plt.legend(['上月', '本月'])
#     plt.xticks(rotation=10)
#     axis.set_ylabel('业绩-万')

#     axis_1 = axis.twinx()
#     axis_1.scatter(np.arange(len(df.index)) + 0.3, df['同比'], color='r')
#     plt.legend(['增长率'], loc=(0.02, 0.9))
#     show_text(df['同比'], 0.3, 0, 'black', '百分比')
#     axis_1.set_ylabel('百分比')
#     axis_1.axhline(0, linestyle='--', linewidth=0.5, color='gray')

# fig2, axis_2 = plt.subplots(figsize=(7, 3))
# fig_s(axis_2, chu_last_next, '新客_上月', '新客_本月', '各平台新客')  # 新客图

# fig3, axis_3 = plt.subplots(figsize=(7, 3))
# fig_s(axis_3, fu_last_next, '老客_上月', '老客_本月', '各平台老客')  # 老客图


# # 各平台总业绩对比
# def chu_fu_mer(dfchu, dffu, col1, col2):
#     # 计算每期新老客总业绩
#     df = pd.merge(dfchu, dffu, left_index=True, right_index=True, how='outer')  
#     df = df.fillna(0)
#     df['总计'] = df[col1] + df[col2]
#     return df

# last_zyj_pt = chu_fu_mer(last_chu_wl, last_fu_wl, 'sum_x', 'sum_y')  
# next_zyj_pt = chu_fu_mer(next_chu_wl, next_fu_wl, 'sum_x', 'sum_y')

# # 合并两期新老客业绩
# zyj_chu_fu = last_next_mer(last_zyj_pt['总计'], next_zyj_pt['总计'], '总计_本月', '总计_上月', '本月', '上月')

# fig4, axis_4 = plt.subplots(figsize=(7, 3))
# fig_s(axis_4, zyj_chu_fu, '上月', '本月', '各平台总')

# # 网络部整体（不分平台）总业绩、新客、老客业绩对比

# last_zyj_wl = last_zyj_pt['总计'].sum()  # 上期网络总业绩
# next_zyj_wl = next_zyj_pt['总计'].sum()

# last_zyj_chu_wl = last_chu_wl.sum()  # 上期网络新客总业绩
# next_zyj_chu_wl = next_chu_wl.sum()

# last_zyj_fu_wl = last_fu_wl.sum()   # 上期网络老客总业绩
# next_zyj_fu_wl = next_fu_wl.sum()


# wl_zyj_mer = pd.DataFrame([[last_zyj_wl, next_zyj_wl],              # 合并
#                            [last_zyj_chu_wl, next_zyj_chu_wl], 
#                            [last_zyj_fu_wl, next_zyj_fu_wl]],
#                            index=['总计', '新客', '老客'],
#                            columns=['上月', '本月'])

# wl_zyj_mer['同比'] = wl_zyj_mer['本月'] / wl_zyj_mer['上月'] - 1     # 计算增长率


# fig5, axis_5 = plt.subplots(figsize=(7, 3))    # 绘图
# fig_s(axis_5, wl_zyj_mer, '上月', '本月', '网络新老客及总')

# # plt.show()

# '''
# 分科室业绩对比
# '''

# # 各平台皮肤科和外科业绩对比

# def get_keshi_yj(df, chuorfu, col, newseriesname):
#     # 计算各网络各平台皮肤科、外科业绩
#     df1 = df[['来源分类', '二级来源', '初复诊', '皮肤科业绩2', '外科业绩2']].copy()
#     df1['初复诊'] = df1['初复诊'].replace('未到院', '初诊')
#     df2 = df1[df1['初复诊'] == chuorfu].groupby(['来源分类', '二级来源'])[col].sum()
#     df2 = df2.loc['网络渠道']
#     df2 = df2 / 10000
#     df2.name = newseriesname
#     return df2


# last_pt_chu_pf = get_keshi_yj(last_zyj, '初诊', '皮肤科业绩2', '皮肤科')  # 上期皮肤科新客
# last_pt_fu_pf = get_keshi_yj(last_zyj, '复诊', '皮肤科业绩2', '皮肤科')  

# last_pt_chu_wk = get_keshi_yj(last_zyj, '初诊', '外科业绩2', '外科')  # 上期外科新客
# last_pt_fu_wk = get_keshi_yj(last_zyj, '复诊', '外科业绩2', '外科')  

# next_pt_chu_pf = get_keshi_yj(next_zyj, '初诊', '皮肤科业绩2', '皮肤科')  # 本期皮肤科新客
# next_pt_fu_pf = get_keshi_yj(next_zyj, '复诊', '皮肤科业绩2', '皮肤科')  

# next_pt_chu_wk = get_keshi_yj(next_zyj, '初诊', '外科业绩2', '外科')  # 本期外科新客
# next_pt_fu_wk = get_keshi_yj(next_zyj, '复诊', '外科业绩2', '外科')  


# # 合并皮肤科新客
# pf_chu_pt_mer = last_next_mer(last_pt_chu_pf, next_pt_chu_pf, '皮肤科_本月', '皮肤科_上月', '本月', '上月')
# # 合并皮肤科老客
# pf_fu_pt_mer = last_next_mer(last_pt_fu_pf, next_pt_fu_pf, '皮肤科_本月', '皮肤科_上月', '本月', '上月')
# # 合并外科新客
# wk_chu_pt_mer = last_next_mer(last_pt_chu_wk, next_pt_chu_wk, '外科_本月', '外科_上月', '本月', '上月')
# # 合并外科老客
# wk_fu_pt_mer = last_next_mer(last_pt_fu_wk, next_pt_fu_wk, '外科_本月', '外科_上月', '本月', '上月')


# # 绘图
# fig6, axis_6 = plt.subplots(figsize=(7, 3))
# fig_s(axis_6, pf_chu_pt_mer, '上月', '本月', '各平台皮肤科新客')  
# fig7, axis_7 = plt.subplots(figsize=(7, 3))
# fig_s(axis_7, pf_fu_pt_mer, '上月', '本月', '各平台皮肤科老客')  
# fig8, axis_8 = plt.subplots(figsize=(7, 3))
# fig_s(axis_8, wk_chu_pt_mer, '上月', '本月', '各平台外科新客')  
# fig9, axis_9 = plt.subplots(figsize=(7, 3))
# fig_s(axis_9, wk_fu_pt_mer, '上月', '本月', '各平台外科老客')  


# # 各平台皮肤科、外科新老客业绩合并
# last_pt_pf_yj = chu_fu_mer(last_pt_chu_pf, last_pt_fu_pf, '皮肤科_x', '皮肤科_y')  # 上期皮肤科
# last_pt_wk_yj = chu_fu_mer(last_pt_chu_wk, last_pt_fu_wk, '外科_x', '外科_y')  # 上期外科

# next_pt_pf_yj = chu_fu_mer(next_pt_chu_pf, next_pt_fu_pf, '皮肤科_x', '皮肤科_y')  # 本期皮肤科
# next_pt_wk_yj = chu_fu_mer(next_pt_chu_wk, next_pt_fu_wk, '外科_x', '外科_y')  # 本期外科

# # 合并2期皮肤科、外科业绩
# last_next_pt_pf_yj = last_next_mer(last_pt_pf_yj['总计'], next_pt_pf_yj['总计'], '总计_本月', '总计_上月', '本月', '上月')
# last_next_pt_wk_yj = last_next_mer(last_pt_wk_yj['总计'], next_pt_wk_yj['总计'], '总计_本月', '总计_上月', '本月', '上月')

# fig10, axis_10 = plt.subplots(figsize=(7, 3))
# fig_s(axis_10, last_next_pt_pf_yj, '上月', '本月', '各平台皮肤科')
# fig11, axis_11 = plt.subplots(figsize=(7, 3))
# fig_s(axis_11, last_next_pt_wk_yj, '上月', '本月', '各平台外科')


# # 网络部整体皮肤科、外科业绩对比
# last_wl_pf_z = last_pt_pf_yj['总计'].sum()  # 上期皮肤科总-网络整体
# last_wl_wk_z = last_pt_wk_yj['总计'].sum()  

# next_wl_pf_z = next_pt_pf_yj['总计'].sum()  # 本皮肤科总-网络整体
# next_wl_wk_z = next_pt_wk_yj['总计'].sum()  


# last_wl_pf_chu = last_pt_chu_pf.sum()  # 上期皮肤科新客-网络整体
# last_wl_pf_fu = last_pt_fu_pf.sum()  

# last_wl_wk_chu = last_pt_chu_wk.sum()  # 上期外科新客-网络整体
# last_wl_wk_fu = last_pt_fu_wk.sum()  

# next_wl_pf_chu = next_pt_chu_pf.sum()  # 本期皮肤科新客-网络整体
# next_wl_pf_fu = next_pt_fu_pf.sum()  

# next_wl_wk_chu = next_pt_chu_wk.sum()  # 本期外科新客-网络整体
# next_wl_wk_fu = next_pt_fu_wk.sum()  

# wl_pf_wk_mer = pd.DataFrame([[last_wl_pf_z, next_wl_pf_z],         # 合并
#                              [last_wl_pf_chu, next_wl_pf_chu],             
#                              [last_wl_pf_fu, next_wl_pf_fu],
#                              [last_wl_wk_z, next_wl_wk_z],
#                              [last_wl_wk_chu, next_wl_wk_chu],
#                              [last_wl_wk_fu, next_wl_wk_fu]],
#                              index=['皮肤科', '皮肤-新客', '皮肤科-老客', '外科', '外科-新客', '外科-老客'],
#                              columns=['上月', '本月'])

# wl_pf_wk_mer['同比'] = wl_pf_wk_mer['本月'] / wl_pf_wk_mer['上月'] - 1     # 计算增长率


# fig12, axis_12 = plt.subplots(figsize=(7, 3))    # 绘图
# fig_s(axis_12, wl_pf_wk_mer, '上月', '本月', '网络皮肤/外科')




