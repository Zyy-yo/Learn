import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import os 
import warnings
import time
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.palettes import viridis

warnings.filterwarnings('ignore')
os.chdir(r'D:\工作\数据分析\微专业\项目数据\考核项目06_婚恋配对实验')


'''
婚恋配对模拟规则：
① 按照一定规则生成了1万男性+1万女性样本：
   ** 在配对实验中，这2万个样本具有各自不同的个人属性（财富、内涵、外貌），每项属性都有一个得分
   ** 财富值符合指数分布，内涵和颜值符合正态分布
   ** 三项的平均值都为60分，标准差都为15分
② 模拟实验。基于现实世界的提炼及适度简化，我们概括了三个最主流的择偶策略：
   ** 择偶策略1：门当户对，要求双方三项指标加和的总分接近，差值不超过20分；
   ** 择偶策略2：男才女貌，男性要求女性的外貌分比自己高出至少10分，女性要求男性的财富分比自己高出至少10分；
   ** 择偶策略3：志趣相投、适度引领，要求对方的内涵得分在比自己低10分~高10分的区间内，且外貌和财富两项与自己的得分差值都在5分以内
③ 每一轮实验中，我们将三种策略随机平分给所有样本（即采用每种策略的男性有3333个样本）
④ 我们为每位单身男女随机选择一个对象，若双方互相符合要求就算配对成功，配对失败的男女则进入下一轮配对。
'''

# 生成财富、内涵、外貌初始数据
def origindata(sex, si):
    # sex: 性别
    # si: 样本大小
    inds = []
    for i in range(1, si+1):
        inds.append(sex + str(i))
    df = pd.DataFrame({'wealth': np.random.exponential(scale=15, size=si) + 45,
                       'character': np.random.normal(loc=60, scale=15, size=si),
                       'appearance': np.random.normal(loc=60, scale=15, size=si)},
                       index=inds)
    df['score'] = (df['wealth'] + df['character'] + df['appearance']) / 3
    return df

# 男女各99条样本数据
maledata = origindata('m', 99)
femaledata = origindata('f', 99)
maledata['strategy'] = np.random.choice([1, 2, 3], 99)
test_m1 = maledata.copy()
test_f1 = femaledata.copy()


# 男女各10000条实验数据
maledata2 = origindata('m', 10000)
femaledata2 = origindata('f', 10000)
maledata2['strategy'] = np.random.choice([1, 2, 3], 10000)
test_m2 = maledata2.copy()
test_f2 = femaledata2.copy()

# 查看数据分布（男性数据）
def fig_hist(df, *cols):
    fig = plt.figure(figsize=(12, 6))
    i = 1
    for col in cols:
        ax = fig.add_subplot(1, 3, i)
        ax.set_title('%s数据分布'%col)
        df[col].plot.hist(bins=100, edgecolor='w')  
        i += 1
    plt.savefig('男性样本数据分布图.jpg')
fig_hist(maledata2, 'character', 'wealth', 'appearance')
    
maledata2[['wealth', 'character', 'appearance']].iloc[:50].plot.bar(stacked=True)  # 堆叠柱状图查看
plt.savefig('实验样本前50条数据堆叠图.png')


# 构建配对模型
def match(df_m, df_f, round):
    # 准备用来匹配的数据
    # 为male的测试数据随机选择female
    df_m['choice'] = np.random.choice(df_f.index, len(df_m))
    # 合并数据
    match_data = pd.merge(df_m, df_f, left_on='choice', right_index=True, suffixes=('_m', '_f')).reset_index()
    # 计算各标准
    match_data['sumscore_chaabs'] = abs((match_data['wealth_m'] + match_data['character_m'] + match_data['appearance_m']) - \
        (match_data['wealth_f'] + match_data['character_f'] + match_data['appearance_f']))          # 三项总分差值
    match_data['wealth_cha'] = match_data['wealth_m'] - match_data['wealth_f']   # 男性财富值高于女性财富值
    match_data['appear_cha'] = match_data['appearance_f'] - match_data['appearance_m']   # 女性外貌值高于男性外貌值
    match_data['wealth_chaabs'] = abs(match_data['wealth_m'] - match_data['wealth_f'])  # 男性与女性财富差值
    match_data['appear_chaabs'] = abs(match_data['appearance_f'] - match_data['appearance_m']) # 男性与女性外貌差值
    match_data['charac_chaabs'] = abs(match_data['character_m'] - match_data['character_f']) # 男性与女性内涵差值

    # 策略1
    match1 = match_data[match_data['strategy'] == 1]
    match1 = match1[match1['sumscore_chaabs'] <= 20].groupby('choice').max()   
    match1_suc = match1[['index']].reset_index()
    match1_suc.columns = ['f', 'm']
    match1_suc['strategies'] = 1
    match1_suc['rounds'] = round

    # 策略2
    match2 = match_data[match_data['strategy'] == 2]
    match2 = match2[(match2['appear_cha'] >= 10) & (match2['wealth_cha'] >= 10)].groupby('choice').max()
    match2_suc = match2[['index']].reset_index()
    match2_suc.columns = ['f', 'm']
    match2_suc['strategies'] = 2
    match2_suc['rounds'] = round

    # 策略3
    match3 = match_data[match_data['strategy'] == 3]
    match3 = match3[(match3['charac_chaabs'] < 10) & (match3['wealth_chaabs'] < 5) & (match3['appear_chaabs'] < 5)].groupby('choice').max()
    match3_suc = match3[['index']].reset_index()
    match3_suc.columns = ['f', 'm']
    match3_suc['strategies'] = 3
    match3_suc['rounds'] = round

    matchsuccess = pd.concat([match1_suc, match2_suc, match3_suc]).reset_index(drop=True)
    # 用choice随机选择女性，可能出现不同策略下的男性匹配同一女性的情况，因此以先来后到为原则，保留第一次策略匹配成功的数据
    matchsuccess.drop_duplicates(subset=['f'], inplace=True)
    return matchsuccess

# 运行模型
def run_model(df_m, df_f):
    samplesize = len(df_m)     # 原数据样本大小
    strategy1_size = len(df_m[df_m['strategy'] == 1])         # 原数据不同策略的样本大小
    strategy2_size = len(df_m[df_m['strategy'] == 2])   
    strategy3_size = len(df_m[df_m['strategy'] == 3])           
    mean_m_bystrategy = df_m.groupby('strategy')[['wealth', 'character', 'appearance']].mean()      # 原数据不同策略男性各项属性均值

    starttime = time.time()
    n = 1
    pair = match(df_m, df_f, n)      # 第一次匹配
    pairs = pair.copy()
    df_m.drop(pair['m'].tolist(), inplace=True)        # 删除已经匹配成功的男性和女性
    df_f.drop(pair['f'].tolist(), inplace=True)
    print('成功进行第%i轮实验，本轮匹配%i对，共成功匹配%i对，还剩%i位男性和%i位女性'%(n, len(pair), len(pairs), len(df_m), len(df_f)))

    while len(pair) != 0:
        n += 1
        pair = match(df_m, df_f, n)
        pairs = pd.concat([pairs, pair])
        df_m.drop(pair['m'].tolist(), inplace=True)
        df_f.drop(pair['f'].tolist(), inplace=True)
        print('成功进行第%i轮实验，本轮匹配%i对，共成功匹配%i对，还剩%i位男性和%i位女性'%(n, len(pair), len(pairs), len(df_m), len(df_f)))
    endtime = time.time()
    
    print('-'*50)
    print('共进行%i轮实验，成功匹配%i对，用时%.2f秒'%(n, len(pairs), (endtime - starttime)))
    print('%.2f%%的数据成功匹配到了对象'%((len(pairs) / samplesize) * 100))
    print('择偶策略1匹配成功率是%.2f%%'%((len(pairs[pairs['strategies'] == 1]) / strategy1_size) * 100))
    print('择偶策略2匹配成功率是%.2f%%'%((len(pairs[pairs['strategies'] == 2]) / strategy2_size) * 100))
    print('择偶策略3匹配成功率是%.2f%%'%((len(pairs[pairs['strategies'] == 3]) / strategy3_size) * 100))
    print('采取不同策略的男性各项平均分：\n', mean_m_bystrategy)  # 这个应该没啥意义，本身数据就是按照均值60生成的
    return pairs
pair99 = run_model(test_m1, test_f1).reset_index(drop=True)    # 99条数据实验结果
pair10000 = run_model(test_m2, test_f2)    # 10000条数据实验结果

m2 = pd.merge(pair10000, maledata2, left_on='m', right_index=True)           # 与原数据合并男性数据
m2.boxplot(by='strategies', column=['wealth', 'character', 'appearance'])
plt.savefig('10000对样本数据匹配成功的男性数据分布.png')

'''
以99男+99女的样本数据，绘制匹配折线图
要求：
① 生成样本数据，模拟匹配实验
② 生成绘制数据表格
③ bokhe制图
   ** 这里设置图例，并且可交互（消隐模式）
'''

pair99['x'] = pair99['f'].str.replace('f', '')
pair99['y'] = pair99['m'].str.replace('m', '')
for i in pair99.index:
    pair99['x'][i] = [0, int(pair99['x'][i]), int(pair99['x'][i])]
    pair99['y'][i] = [int(pair99['y'][i]), int(pair99['y'][i]), 0]

r = pair99['rounds'].max()
colors = viridis(r)
pair99['color'] = np.nan
for i in pair99['rounds']:
    pair99['color'][pair99['rounds'] == i] = colors[i-1]

output_file('99对样本数据配对模拟.html')

p = figure(plot_width=700, plot_height=500, x_range=[0,100], y_range=[0, 100])
for i in pair99.index:
    p.line(pair99['x'][i], pair99['y'][i], line_color=pair99['color'][i], line_width=0.5, legend='round %i'%pair99['rounds'][i])
    p.circle(pair99['x'][i][1], pair99['y'][i][1], color=pair99['color'][i], size=4, legend='round %i'%pair99['rounds'][i])
p.legend.background_fill_alpha = 0.1
p.legend.click_policy = 'hide'
p.grid.grid_line_dash = [3,5]
show(p)


'''
生成“不同类型男女配对成功率”矩阵图
要求：
① 以之前1万男+1万女实验的结果为数据
② 按照财富值、内涵值、外貌值分别给三个区间，以区间来评判“男女类型”
   ** 高分（70-100分），中分（50-70分），低分（0-50分）
   ** 按照此类分布，男性女性都可以分为27中类型：财高品高颜高、财高品中颜高、财高品低颜高、... （财→财富，品→内涵，颜→外貌）
③ bokhe制图
   ** 散点图
   ** 27行*27列，散点的颜色深浅代表匹配成功率
'''

# 准备数据
f2 = pd.merge(m2, femaledata2, left_on='f', right_index=True, suffixes=('_m', '_f'))    # 与原数据合并女性数据
mf2 = f2.copy()      

def pro_class(df, col1, col2):
    # 为三项属性分值做分类
    df[col1] = 0
    df[col1][df[col2] >= 70] = col1[-1] + '高'
    df[col1][(df[col2] < 70) & (df[col2] >= 50)] = col1[-1] + '中'
    df[col1][df[col2] < 50] = col1[-1] + '低'
    return df

mf2 = pro_class(mf2, '男财', 'wealth_m')              # 划分属性类型
mf2 = pro_class(mf2, '男颜', 'appearance_m')
mf2 = pro_class(mf2, '男品', 'character_m')
mf2 = pro_class(mf2, '女财', 'wealth_f')
mf2 = pro_class(mf2, '女颜', 'appearance_f')
mf2 = pro_class(mf2, '女品', 'character_f')

mf2['type_m'] = mf2['男财'] + mf2['男品'] + mf2['男颜']         # 类型合并
mf2['type_f'] = mf2['女财'] + mf2['女品'] + mf2['女颜']

mf2_filt = mf2[['f', 'm', 'type_m', 'type_f']]       # 筛选数据

protype_pair = mf2_filt.groupby(['type_m', 'type_f']).count()    # 计算各属性匹配对数
protype_pair = protype_pair.reset_index()
protype_pair['pair_per'] = protype_pair['f'] / protype_pair['f'].sum()   # 计算属性匹配成功率
protype_pair['alpha'] = (protype_pair['pair_per'] - protype_pair['pair_per'].min()) / \
    (protype_pair['pair_per'].max() - protype_pair['pair_per'].min()) * 10            # 按匹配成功率计算颜色透明度
print(protype_pair.head())

ranx = protype_pair['type_m'].unique()
rany = protype_pair['type_f'].unique()

# bokeh绘图
source = ColumnDataSource(protype_pair)
hover = HoverTool(tooltips=[('男性类型', '@type_m'),
                            ('女性类型', '@type_f'),
                            ('匹配成功率', '@pair_per')])
output_file('不同属性分类男女配对成功率.html')
p2 = figure(plot_width=600, plot_height=500, tools=[hover, 'pan, wheel_zoom, reset'], x_range=ranx, y_range=rany)
p2.square(x='type_m', y='type_f', source=source, color='green', alpha='alpha', size=13)
p2.grid.grid_line_dash = [2,5]
p2.xaxis.major_label_orientation = 'vertical'
show(p2)

plt.show()