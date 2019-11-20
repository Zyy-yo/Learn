import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os
import warnings

warnings.filterwarnings('ignore')

os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习07_中国城市资本流动问题探索')
data = pd.read_excel('data.xlsx')


# 分组汇总投资企业对数，2013-2016年每年投资流向
group = data.groupby(['年份', '投资方所在城市', '融资方所在城市']).sum()
group.reset_index(inplace=True)

# group.to_excel('group.xlsx')

# 以下一段为绘制2013到2016年每年同城、跨城投资柱状图代码，绘制完毕后注释
'''
def tckc20(df, i):
    # 分别得到不同年份的同城投资和跨城投资前20
    g1_tc = df[(df['年份'] == i) & (df['投资方所在城市'] == df['融资方所在城市'])].sort_values('投资企业对数', ascending=False)[:20]
    g1_tc = g1_tc.set_index(['投资方所在城市', '融资方所在城市'])['投资企业对数']
    g1_kc = df[(df['年份'] == i) & (df['投资方所在城市'] != df['融资方所在城市'])].sort_values('投资企业对数', ascending=False)[:20]
    g1_kc = g1_kc.set_index(['投资方所在城市', '融资方所在城市'])['投资企业对数']
    return (g1_tc, g1_kc)


for i in range(2013,2017,1):
    # 绘制2013到2016年每年的同城投资和跨城投资前20柱状图
    tc = tckc20(group, i)[0]
    kc = tckc20(group, i)[1]
    fig1 = plt.figure()
    tc.plot.bar(rot=20, figsize=(10,6), title='同城%i'%i, color='g', alpha=0.6)
    plt.savefig('同城%i.jpg'%i, bbox_inches='tight')
    fig2 = plt.figure()
    kc.plot.bar(rot=20, figsize=(10,6), title='跨城%i'%i, color='r', alpha=0.5)
    plt.savefig('跨城%i.jpg'%i, bbox_inches='tight')
'''


# 2013-2016年整体投资流向
df_allyear = group.groupby(['投资方所在城市', '融资方所在城市']).sum()['投资企业对数']
df_allyear = df_allyear.reset_index()
# df_allyear.to_excel('group_allyear.xlsx')


def gephi(df):
    # 处理成gephi中的点文件和线文件
    df.columns = ['target', 'source', 'weight']
    df['weight'] = (df['weight'] - df['weight'].min()) / (df['weight'].max() - df['weight'].min()) * 10
    df.to_csv('edgedata.csv', index=False)

    s1 = df_allyear['target'].value_counts()
    s2 = df_allyear['source'].value_counts()
    s = s1 + s2
    df2 = pd.DataFrame(s).reset_index().fillna(0)
    df2.columns=['Id', 'level']
    df2['level'] = (df2['level'] - df2['level'].min()) / (df2['level'].max() - df2['level'].min()) * 10
    df2['Label'] = df2.sort_values('level', ascending=False)['Id'][:20]
    df2.to_csv('nodedata.csv', index=False)
# gephi(df_allyear)


# 以下一段代码为绘制2013到2016年同城、跨城投资总体柱状图代码，绘制完毕后注释
'''
def tckc20_all(df):
    # 同城、跨城投资top20四年整体情况柱状图绘制
    tc_all = df[df['投资方所在城市'] == df['融资方所在城市']].sort_values('投资企业对数', ascending=False)[:20]
    tc_all.set_index(['投资方所在城市', '融资方所在城市'], inplace=True)
    kc_all = df[df['投资方所在城市'] != df['融资方所在城市']].sort_values('投资企业对数', ascending=False)[:20]
    kc_all.set_index(['投资方所在城市', '融资方所在城市'], inplace=True)

    tc_all.plot.bar(rot=20, figsize=(10,6), title='同城投资2013-2016整体情况', color='g', alpha=0.6)
    plt.savefig('同城投资整体.jpg', bbox_inches='tight')
    kc_all.plot.bar(rot=20, figsize=(10,6), title='跨城投资2013-2016整体情况', color='r', alpha=0.6)
    plt.savefig('跨城投资整体.jpg', bbox_inches='tight')
tckc20_all(df_allyear)
'''

# 读取城市代码对照表
data2 = pd.read_excel('中国城市代码对照表.xlsx')

# 以下一段代码将自治州等地名进行转换，方便下一步和中国城市代码对照表的合并，因运行太慢，转换好之后存储到excel再读取，此代码注释
'''
print('开始')
def citych(df):
    # 将自治州等地名进行转换，转换好之后存储到excel再读取，因运行太慢，此代码注释
    citys = data2['城市名称'].values
    for city in citys:
        for i, row in df.iterrows():
            if city != row['投资方所在城市']:
                if city in row['投资方所在城市'] and city != '鞍山':
                    df['投资方所在城市'].loc[i] = city
                elif len(city) > 2 and city.split('州')[0] in row['投资方所在城市']:
                    df['投资方所在城市'].loc[i] = city
            if city != row['融资方所在城市']:
                if city in row['融资方所在城市'] and city != '鞍山':
                    df['融资方所在城市'].loc[i] = city
                elif len(city) > 2 and city.split('州')[0] in row['融资方所在城市']:
                    df['融资方所在城市'].loc[i] = city        
    return df
dfc = citych(df_allyear)
dfc.to_excel('group2.xlsx')
print('结束')
'''

# 整体投资关系表加上经纬度

data3 = pd.read_excel('group2.xlsx')

def addlng(df, col):
    # 与中国代码对照表以城市名称合并，得到经纬度
    df_mer = pd.merge(df, data2, left_on=col, right_on='城市名称')
    return df_mer

tzlng = addlng(data3, '投资方所在城市')     # 投资方经纬度
rzlng = addlng(tzlng, '融资方所在城市')     # 融资方经纬度

data3_jw = rzlng[['投资方所在城市', '融资方所在城市', '投资企业对数', '经度_x', '纬度_x','经度_y', '纬度_y']].dropna()
# data3_jw.to_csv('投融资经纬度.csv', index=False)




# 2013-2016年对外投资最多的10个城市
tz10 = df_allyear[df_allyear['投资方所在城市'] != df_allyear['融资方所在城市']].groupby('投资方所在城市').sum().sort_values('投资企业对数',ascending=False)[:10]
# 2013-2016年吸引对外投资最多的10个城市
rz10 = df_allyear[df_allyear['投资方所在城市'] != df_allyear['融资方所在城市']].groupby('融资方所在城市').sum().sort_values('投资企业对数',ascending=False)[:10]

def assex():
    # 对外投资和吸引外部融资前10城市柱状图
    tz10.plot.bar(color='y', title='2013-2016年对外投资笔数最多的10个城市', rot=0)
    plt.grid(axis='y', linestyle='--', color='gray', alpha=0.5)
    plt.savefig('对外投资top10.jpg', bbox_inches='tight')

    rz10.plot.bar(color='greenyellow', title='2013-2016年吸引对外投资笔数最多的10个城市', rot=0)
    plt.grid(axis='y', linestyle='--', color='gray', alpha=0.5)
    plt.savefig('吸引外部融资top10.jpg', bbox_inches='tight')
# assex()


# # 计算北上深阵营和非北上深阵营每年城市数量，以投资城市是否为北上深判定
# bss = group[(group['投资方所在城市'] == '北京') | (group['投资方所在城市'] == '上海') | (group['投资方所在城市'] == '深圳')]\
#     .groupby(['年份', '投资方所在城市']).count()['融资方所在城市']
# bss = bss.reset_index()
# bss = bss.groupby('年份').sum()
# print(bss)



# wd = group[(group['投资方所在城市'] != '北京') & (group['投资方所在城市'] != '上海') & (group['投资方所在城市'] != '深圳')]\
#     .groupby(['年份', '投资方所在城市']).count()['融资方所在城市']
# wd = wd.reset_index()
# wd = wd.groupby('年份').sum()
# print(wd.head())


# data4 = pd.merge(bss, wd, left_index=True, right_index=True, suffixes=('_北上深', '_非北上深'))
# data4['北上深占比'] = data4['融资方所在城市_北上深'] / (data4['融资方所在城市_北上深'] + data4['融资方所在城市_非北上深'])
# print(data4)


# 计算北上深阵营和非北上深阵营每年城市数量，接受外来投资笔数最大的来源城市属于北上深之一，则为北上深阵营
# print(group.head())



# b2 = b1[(b1['融资方所在城市'] != '北京') & (b1['融资方所在城市'] != '上海') & (b1['融资方所在城市'] != '深圳')]
# b3 = b2[(b2['投资方所在城市'] == '北京') | (b2['投资方所在城市'] == '上海') | (b2['投资方所在城市'] == '深圳')]


def zheny(year):
    # 求得北上深阵营和非北上深阵营每年城市数量
    # 按照年份划分数据，以融资城市分组获得投资企业对数最大值
    eachyear_data = group[group['年份'] == year]
    eachyear_kc = eachyear_data[eachyear_data['投资方所在城市'] != eachyear_data['融资方所在城市']].groupby('融资方所在城市')['投资企业对数'].max().reset_index()

    # 合并数据，得到该年融资城市对应投资笔数最大的投资城市
    kcmax = pd.merge(eachyear_kc, eachyear_data, on=['融资方所在城市', '投资企业对数'])
    kcmax = pd.merge(kcmax, data2[['城市名称', '经度', '纬度']], left_on='融资方所在城市', right_on='城市名称')
    kcmax = kcmax[['投资方所在城市', '融资方所在城市', '投资企业对数', '经度', '纬度']]
    # 北上深城市划分为1，其他城市为0，计数并存储到字典
    kcmax['阵营'] = 0
    kcmax['阵营'][(kcmax['投资方所在城市'] == '北京') | (kcmax['投资方所在城市'] == '上海') | (kcmax['投资方所在城市'] == '深圳')] = 1
    count = kcmax['阵营'].value_counts()
    dic = {}
    dic['北上深阵营城市数量'] = count.iloc[1]
    dic['非北上深阵营城市数量'] = count.iloc[0]
    return (dic, kcmax)

# 组成一个数据帧，计算北上深城市占比
data4 = pd.DataFrame([zheny(2013)[0], zheny(2014)[0], zheny(2015)[0], zheny(2016)[0]], index=['2013年', '2014年', '2015年', '2016年'])
data4['北上深阵营占比'] = data4['北上深阵营城市数量'] / (data4['北上深阵营城市数量'] + data4['非北上深阵营城市数量'])

# 绘图
data4[['北上深阵营城市数量', '非北上深阵营城市数量']].plot.bar(figsize=(8,6), rot=0, title='北上深阵营数量')
# plt.savefig('北上深阵营的扩张.jpg')

# 存储2013到2016年的阵营数据，在qgis中绘图
# for i in range(2013,2017,1):
#     zheny(i)[1].to_csv('北上深阵营%s.csv'%i, index=False)

