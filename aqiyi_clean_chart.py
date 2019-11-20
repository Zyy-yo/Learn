import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

pd.set_option('display.max_columns', None)

data = pd.read_csv(r'D:\工作\数据分析\微专业\项目数据\爱奇艺视频数据.csv', engine='python')

# 数据清洗，去除重复数据，填充空值

def fil(data):
    data.drop_duplicates('视频ID', inplace=True)
    for col in data.columns:
        if data[col].dtype == object:
            data[col].fillna('缺失数据', inplace=True)
        else:
            data[col].fillna(0, inplace=True)
    return data

df = fil(data)

# 时间字段转换为时间标签

def date(s, *nyr):
    for hz in nyr:
        s = s.str.replace(hz, '-')
    s = pd.to_datetime(s.str[:-1])
    return s

df['数据获取日期'] = date(df['数据获取日期'], '年', '月', '日')
df.set_index('数据获取日期', inplace=True)
df1 = df.copy()

# 不同导演电影好评率

# 将多个导演分割出来
def fg_dy(df, f1, f2):
    hp = df[['导演', f1, f2]].set_index('导演').drop('缺失数据')
    spl1 = pd.concat([pd.Series(row[f1], i.split('/')) for i, row in hp.iterrows()])
    spl2 = pd.concat([pd.Series(row[f2], i.split('/')) for i, row in hp.iterrows()])
    fg_df = pd.concat([spl1, spl2], axis=1, keys=['好评数', '评分人数'])
    fg_df_g = fg_df.groupby(fg_df.index).sum()
    return fg_df_g

dfspl = fg_dy(df1, '好评数', '评分人数')

# 计算好评率，并进行标准化，取值0~100。提取好评率前20的数据。

def calhp(df):
    df['好评率'] = df['好评数'] / df['评分人数']
    df['好评率_nor'] = (df['好评率'] - df['好评率'].min()) / (df['好评率'].max() - df['好评率'].min()) * 100
    df = df.sort_values('好评率_nor', ascending=False)[:20]
    return df

dfspl_hp = calhp(dfspl)

# 绘制图表（只按导演来看）

y1 = dfspl_hp['好评率_nor']
fig1 = plt.figure(figsize=(12,5))
plt.title('爱奇艺视频_导演好评率top20')
plt.bar(np.arange(20), y1, facecolor='g', tick_label=dfspl_hp.index)
for i, j in zip(np.arange(20), y1):
    plt.text(i-0.3, 2, '%.1f'%j, color='w')

fig2 = plt.figure(figsize=(12,5))
plt.plot(dfspl_hp.index, y1, marker='o', color='g')
plt.grid(axis='y', linestyle='--', color='gray', alpha=0.5)

# 按照导演和电视计算

df2 = df.groupby(['导演', '整理后剧名']).sum()[['好评数', '差评数', '评分人数']]
df2['好评率'] = df2['好评数'] / df2['评分人数']
df2['好评率_nor'] = (df2['好评率'] - df2['好评率'].min()) / (df2['好评率'].max() - df2['好评率'].min()) * 100
df2 = df2.sort_values('好评率', ascending=False).drop('缺失数据',level=0)[:20]

# 绘制图表，按照导演和剧来看

x = df2['好评数']
y = df2['好评率_nor']
fig3 = plt.figure(figsize=(10,6))
plt.title('2001~2016年好评率top20的导演及其影视剧')
plt.scatter(x, y, s=x/15000, c=y, cmap='plasma', label='导演：剧名')
plt.legend()
a = []
for i in range(20):
    a.append(df2.index[:20][i][0] + '：' + df2.index[:20][i][1])

for i, j, k in zip(x, y, a):
    plt.text(i, j, k, fontsize=10)


# 2001年到2016年每年评影人数总量

# 单独以评分人数来看
rs = df.groupby('上映时间').sum()['评分人数'].drop(0)
rs = rs[rs.index > 2000]

# 以标准化取值100以内的评分人数及好评和差评数来看
rs2 = df.groupby('上映时间').sum()[['评分人数', '好评数', '差评数']].drop(0)
rs2 = rs2[rs2.index > 2000]       

def nor(x, *cols):
    '''
    对数据进行标准化，为方便观看，取值0~100
    x: 要进行标准化计算的dataframe
    cols: 可以传入多个要标准化的字段名
    '''
    colns = []
    for col in cols:
        coln = col + '_nor'
        colns.append(coln)
        x[coln] = (x[col] - x[col].min()) / (x[col].max() - x[col].min()) * 100
    xn = x[colns]
    return xn

rsn = nor(rs2, '评分人数', '好评数', '差评数')    # '评分人数', '好评数', '差评数'字段标准化取值

# 绘图
# 单独以评分人数来看
fig4,axes = plt.subplots(2,1,figsize=(8,5))
rs.plot.area(color='lightcoral', ax=axes[0])
axes[0].set_xlabel(None)
axes[0].set_title('2001~2016年评影总人数')
for i, j in zip(rs.index, rs):
    axes[0].text(i, j, '%i'%j, color='b')
axes[0].legend(['评分总人数'])

# 进行标准化后的评分人数及其中的好评和差评数来看
rsn.plot.area(colormap='Set2', ax=axes[1])
axes[1].set_title('2001~2016年评影人数堆叠图')
plt.legend()


def flt(df):
    '''
    筛选2001~2016年的视频数据
    返回提取特定时间年份和字段的视频数据列表: view
    返回只提取时间和评分人数的series列表: pl
    df ：经过初步清洗处理的视频原数据
    '''
    view = []
    pl = []
    t = 2001
    while t <= 2016:
        n = df[df['上映时间'] == t][['上映时间', '导演', '好评数', '差评数', '评分人数','整理后剧名']]
        s = n[['上映时间','评分人数']].set_index('上映时间')
        t += 1
        view.append(n)
        pl.append(s)
    return (view, pl)

dfshai = flt(df1)[0]      # 经过年份和字段筛选后的视频数据列表
seri = flt(df1)[1]           # series组成的列表，series索引为上映时间，value为评分人数

def wx(df):
    '''
    计算外限最大值和最小值
    '''
    Q3 = df.quantile(q=0.75)
    Q1 = df.quantile(q=0.25)
    IQR = Q3 - Q1
    wxmax = Q3 + IQR * 3
    wxmin = Q1 - IQR * 3
    return (wxmax, wxmin)

def wx_yc(df):
    '''
    返回外限最大值和最小值数据列表：wxs
    返回'评分人数'极度异常的视频数据列表：newdf
    df ： 经过年份和字段筛选后的视频数据列表，列表中的每个元素是dataframe类型的视频数据
    '''
    wxs = []
    newdf = []
    for d in df:
        dwx = wx(d)        # 调用外限计算函数
        max = dwx[0]
        min = dwx[1]
        newd = d[d['评分人数'] > max['评分人数']].sort_values('评分人数', ascending=False)  # 筛选评分人数极度异常数据
        wxs.append([max, min])
        newdf.append(newd)
    return (wxs, newdf)

wxvalue = wx_yc(dfshai)[0]        # 外限最大值和最小值
ycvalue = wx_yc(dfshai)[1]        # 异常数据（包含导演、好评数、差评数、评分总人数、剧名）

print('2001~2016年评分数外限最大值和最小值：\n',wxvalue)
print('2001~2016年评分数超过外限的影视剧：\n',ycvalue)

# 箱型图验证每年评分人数极度异常数据

va = []
lab = []
for i in seri:
    va.append(i.values)
    lab.append(i.index.unique()[0])
fig5 = plt.figure(figsize=(12,6))
plt.title('2001~2016年评分人数箱型图')
plt.boxplot(va, whis=3, labels=lab)
plt.show()