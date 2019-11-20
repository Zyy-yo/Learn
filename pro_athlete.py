import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.chdir(r'D:\工作\数据分析\微专业\项目数据\考核项目04-多场景下的图表可视化表达')

data_info = pd.read_excel('奥运运动员数据.xlsx', sheet_name='运动员信息')
print(data_info.info())  # name, event, gender, birthday, height无空值

# 观察数据发现有重复值，删除重复数据
data_dropdup = data_info.drop_duplicates(subset=['name', 'birthday']).reset_index(drop=True)

def fig1_kde():
    # 按性别分析运动员的身高分布，制作密度曲线图，添加平均身高辅助线
    male_height = data_dropdup[data_dropdup['gender'] == '男']['height']
    female_height = data_dropdup[data_dropdup['gender'] == '女']['height']

    sns.distplot(male_height, hist=False, rug=True, 
                color='green', kde_kws={'lw':1, 'alpha':0.5},
                label='male_height_dist')
    sns.distplot(female_height, hist=False, rug=True, 
                color='red', kde_kws={'lw':1, 'alpha':0.5},
                rug_kws={'height':0.1, 'alpha':0.3},
                label='female_height_dist')

    plt.axvline(male_height.mean(), ls='--', lw=1, alpha=0.5, color='g')
    plt.text(male_height.mean()+2, 0.007, 'male_height_mean: %.2fcm'%male_height.mean(),
            color='g')

    plt.axvline(female_height.mean(), ls='--', lw=1, alpha=0.5, color='r')
    plt.text(female_height.mean()+2, 0.01, 'female_height_mean: %.2fcm'%female_height.mean(),
            color='r')
    plt.savefig('athlete_height_dist.jpg')
fig1_kde()

'''
综合指标判断运动员的身材，找到TOP8的运动员，并制作图表
要求：
① 针对不同指标，绘制面积堆叠图
② TOP8的运动员，绘制雷达图表示
提示：
① 四个指标评判运动员身材，并加权平均
   a. BMI 指数（BMI =体重kg ÷ 身高m**2，详细信息可百度查询）→ 越接近22分数越高
   b. 腿长/身高 指数 → 数据筛选，只选取小于0.7的数据，越大分数越高
   c. 臂展/身高 指数 → 数据筛选，只选取大于0.7的数据，比值越接近1分数越高
   d. 年龄 指数 → 年龄越小分数越高
   对上述abcd指标分别标准化得到n1,n2,n3,n4（划分到0-1的分值）
   最后评分： finalscore = (n1 + n2 + n3 + n4)/4
'''


data2 = data_dropdup[['name', 'age', 'height', 'weight', 'arm', 'leg']]
# 删除缺失值
data2_dropnul = data2.dropna()


def cal_zb(df):
    # 计算各项指标
    dfc = df.copy()
    dfc['BMI指数'] = dfc['weight'] / (dfc['height'] / 100) ** 2
    dfc['腿长/身高'] = dfc['leg'] / dfc['height']
    dfc['臂展/身高'] = dfc['arm'] / dfc['height']
    dfc = dfc[(dfc['臂展/身高'] > 0.7) & (dfc['腿长/身高'] < 0.7)]
    return dfc

data3 = cal_zb(data2_dropnul)


def nor(df):
    # 各项指标0~1标准化，越接近1则越好
    dfc = df.copy()
    # BMI指标越接近于22越好
    dfc['BMI-22'] = np.abs(dfc['BMI指数'] - 22)
    dfc['BMI指数nor'] = (dfc['BMI-22'].max() - dfc['BMI-22']) / (dfc['BMI-22'].max() - dfc['BMI-22'].min())
    # 年龄越小越好
    dfc['agenor'] = (dfc['age'].max() - dfc['age']) / (dfc['age'].max() - dfc['age'].min())
    # 腿长/身高比值越大越好
    dfc['腿长/身高nor'] = (dfc['腿长/身高'] - dfc['腿长/身高'].min()) / (dfc['腿长/身高'].max() - dfc['腿长/身高'].min())
    # 臂展/身高比值越接近于1越好
    dfc['臂展/身高-1'] = np.abs(dfc['臂展/身高'] - 1)
    dfc['臂展/身高nor'] = (dfc['臂展/身高-1'].max() - dfc['臂展/身高-1']) / (dfc['臂展/身高-1'].max() - dfc['臂展/身高-1'].min())
    # 计算综合指标并降序
    dfc['finalscore'] = (dfc['BMI指数nor'] + dfc['腿长/身高nor'] + dfc['臂展/身高nor'] +dfc['agenor']) / 4
    dfc = dfc.sort_values('finalscore', ascending=False).reset_index(drop=True)
    return dfc

data4 = nor(data3)

def fig2_area():
    # 绘制四项指标面积图
    data4[['BMI指数nor', '腿长/身高nor', '臂展/身高nor', 'agenor']].plot.area(colormap='Reds', alpha=0.8, lw=0.2)
    plt.grid(ls='--', lw=1, alpha=0.3, color='gray')
    plt.savefig('运动员身材各指标面积图.jpg')
fig2_area()

def fig2_bar(df, *cols):
    # 绘制四项指标top8柱状图
    fig = plt.figure(figsize=(15,6))
    colors = ['hotpink', 'lightseagreen', 'gold', 'greenyellow']
    j = 0
    for i in range(1,5):
        y = df.sort_values(cols[j], ascending=False)[:8]
        ax = fig.add_subplot(2,2,i)
        ax.bar(range(8), y[cols[j]], color=colors[i-1], alpha=0.4)
        tick = y['name'].tolist()
        ax.set_xticks(range(0,8))
        ax.set_xticklabels(tick, rotation=10)
        ax.set_title(cols[i-1])
        j += 1
    fig.suptitle('运动员身材各指标top8')
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.savefig('运动员身材各指标top8.jpg')

fig2_bar(data4, 'BMI指数nor', '腿长/身高nor', '臂展/身高nor', 'agenor')


# 运动员身材综合指标top8雷达图

def radpredf():
    # 雷达图数据准备
    datas = []
    titles = []
    df = data4[['name', 'BMI指数nor', '腿长/身高nor', '臂展/身高nor', 'agenor']][:8]
    for i in df.values:
        data = np.concatenate((i[1:], [i[1]]))   
        titles.append(i[0])
        datas.append(data)
    return [datas, titles]

data5 = radpredf()[0]
titles = radpredf()[1]

# 雷达图角度数据/标签/颜色准备
angles = np.linspace(0, 2*np.pi, 4, endpoint=False)
angles = np.concatenate((angles, [angles[0]]))
labels = ['BMI', '腿长/身高', '臂展/身高', 'age']
colors = plt.get_cmap('tab10')(np.linspace(0.2, 1, 8))

def fig3_radar():
    # 绘制雷达图
    fig = plt.figure(figsize=(12,8))
    i = 0
    while i < 8:
        ax = fig.add_subplot(2, 4, i+1, projection='polar')
        ax.plot(angles, data5[i], color=colors[i], alpha=0.5, lw=1)
        ax.fill(angles, data5[i], color=colors[i], alpha=0.5)
        ax.set_thetagrids(angles*180/np.pi, labels)
        ax.set_theta_offset(5*np.pi/180)
        ax.set_title('top%i'%(i+1) + titles[i] + '%.2f'%data4['finalscore'].values[i]+'\n\n')
        i += 1
    plt.subplots_adjust(hspace=0.4, wspace=0.4)
    fig.suptitle('运动员身材综合指标top8\n\n')
    plt.savefig('运动员身材综合指标top8雷达图.jpg')
fig3_radar()


'''
根据运动员CP数据，分析出CP综合热度
要求：
① 用python计算出综合热度指标
② 用Gephi绘制关系可视化图表
提示：
① 三个指标评判运动员CP综合热度，并加权平均
   a. cp微博数量 → 数量越多分数越高
   b. cp微博话题阅读量 → 阅读量越多分数越高
   c. B站cp视频播放量 → 播放量越大分数越高
   对上述abc指标分别标准化得到n1,n2,n3（划分到0-1的分值）
   最后评分： finalscore = n1*0.5 + n2*0.3 + n3*0.2
'''

data_info2 = pd.read_excel('奥运运动员数据.xlsx', sheet_name='运动员CP热度')
data_r1 = data_info2.replace('无数据', 0)

# 因为空值位置较集中，拉格朗日插值法补充的数据有多个负数，因此采用均值填充

def ycvalue(df, col):
    # 筛选非异常值
    q3 = df[col].quantile(0.75)
    q1 = df[col].quantile(0.25)
    ycmax = q3 + 1.5 * (q3 - q1)
    ycmin = q1 - 1.5 * (q3 - q1)
    not_ycvalue = df[col][(df[col] < ycmax) & (df[col] > ycmin)]
    return not_ycvalue

cpwb_mean = round(ycvalue(data_r1, 'cp微博话题阅读量').mean(), 1)
cpbz_mean = round(ycvalue(data_r1, 'B站cp视频播放量').mean(), 1)

def fil_mean(df, col1, col2):
    # 以排除掉异常值之后的均值填充缺失值
    df[col1].fillna(cpwb_mean, inplace=True)
    df[col2].fillna(cpbz_mean, inplace=True)
    return df

data_r2 = fil_mean(data_r1, 'cp微博话题阅读量', 'B站cp视频播放量')

def nor_2(df, *cols):
    # 各指标标准化
    dfc = df.copy()
    for col in cols:
        dfc[col+'_nor'] = (dfc[col] - dfc[col].min()) / (dfc[col].max() - dfc[col].min())
    return dfc

data_r2_nor = nor_2(data_r2, 'cp微博数量', 'cp微博话题阅读量', 'B站cp视频播放量')
# 计算综合指标
data_r2_nor['finalscore'] = data_r2_nor['cp微博数量_nor'] * 0.5\
    + data_r2_nor['cp微博话题阅读量_nor'] * 0.3 + data_r2_nor['B站cp视频播放量_nor'] * 0.2

# 导出关系数据
data_gephi = data_r2_nor[['p1', 'p2', 'finalscore']]
data_gephi.columns = ['source', 'target', 'weight']
data_gephi.to_csv('athlete_cp.csv', index=False)

def fig4_bar(df, *cols):
    # 绘制各指标CP热度top5
    fig = plt.figure(figsize=(15,6))
    colors = ['brown', 'skyblue', 'darkorange', 'forestgreen']
    j = 0
    for i in range(1,5):
        y = df.sort_values(cols[j], ascending=False)[:5]
        ax = fig.add_subplot(2,2,i)
        ax.bar(range(5), y[cols[j]], color=colors[i-1], alpha=0.4)
        ticks = zip(y['p1'], y['p2'])
        tick = []
        for t in ticks:
            tick.append(t[0]+'/'+t[1])
        ax.set_xticks(range(0,5))
        ax.set_xticklabels(tick)
        ax.set_title(cols[i-1])
        j += 1
    fig.suptitle('CP热度各指标及综合指标TOP5')
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.savefig('CP热度top5.jpg')

fig4_bar(data_r2_nor, 'cp微博数量_nor', 'cp微博话题阅读量_nor', 'B站cp视频播放量_nor', 'finalscore')


