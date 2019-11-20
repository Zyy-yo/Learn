import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import os 

os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习09_泰坦尼克号获救问题')

train_data = pd.read_csv('train.csv')

'''
RangeIndex: 891 entries, 0 to 890
Data columns (total 12 columns):
PassengerId    891 non-null int64
Survived       891 non-null int64
Pclass         891 non-null int64
Name           891 non-null object
Sex            891 non-null object
Age            714 non-null float64
SibSp          891 non-null int64
Parch          891 non-null int64
Ticket         891 non-null object
Fare           891 non-null float64
Cabin          204 non-null object
Embarked       889 non-null object
dtypes: float64(2), int64(5), object(5)
'''


'''
查看整体存活情况
'''
# s = train_data['Survived'].value_counts()
# plt.pie(s, colors=['skyblue', 'hotpink'], autopct='%.2f%%', labels=s.index)
# plt.savefig('整体存活比例.jpg')


'''
结合性别和年龄数据，分析幸存下来的人是哪些人？
'''

agesexdf = train_data[['Sex', 'Age', 'Survived']].copy()

def sexanal(df):
    surdf_group = df.groupby(['Sex', 'Survived'])['Survived'].count()                 # 根据性别/生存字段计数生存数
    female_sur = surdf_group.loc['female', 1] / surdf_group.loc['female'].sum()        # 计算女性存活率
    male_sur = surdf_group.loc['male', 1] / surdf_group.loc['male'].sum()              # 计算男性存活率
    print('女性存活率为 %.2f%%，男性存活率为 %.2f%%'%(female_sur*100, male_sur*100))

    # 存活率性别分布
    sns.barplot(x=df['Sex'], y=df['Survived'], ci=None, color='yellow')
    plt.savefig('不同性别存活率分布')
# sexanal(agesexdf)

def ageanal(df):
    age_df = df.dropna()
    # age_sur = age_df[age_df['Survived'] == 1]                 # 提取存活者数据
    age_group = age_df.groupby('Sex')['Age'].describe()
    # print(age_group)
    print('去掉样本缺失值后，女性数据%d条，平均年龄%.0f, 最大%d岁，最小%.2f岁；男性数据%d条，平均年龄%.0f, 最大%d岁，最小%.2f岁'\
        %(age_group.loc['female']['count'], age_group.loc['female']['mean'], age_group.loc['female']['max'], age_group.loc['female']['min'],\
        age_group.loc['male']['count'], age_group.loc['male']['mean'], age_group.loc['male']['max'], age_group.loc['male']['min']))
    plt.figure()
    # 年龄分布
    sns.distplot(age_df['Age'], bins=30, color='lightgreen', hist_kws={'lw':0.5, 'edgecolor':'g'})
    plt.savefig('年龄分布')
    # 男性女性存活情况
    plt.figure()
    sns.violinplot(x=age_df['Sex'], y=age_df['Age'], hue=age_df['Survived'], split=True)
    plt.savefig('男女存活年龄分布')
    # 各年龄存活情况
    plt.figure(figsize=(12,4))
    sns.barplot(x=age_df['Age'].astype(int), y=age_df['Survived'], ci=None)
    plt.savefig('各年龄存活分布')
# ageanal(agesexdf)

'''
结合 SibSp、Parch字段，研究亲人多少与存活的关系
'''

parchdf = train_data[['Survived', 'SibSp', 'Parch']]

# 有无亲戚和父母子女与存活的关系
sibsp = parchdf[parchdf['SibSp'] != 0]        # 有兄妹/配偶
nosibsp = parchdf[parchdf['SibSp'] == 0]     # 无兄妹/配偶

parch = parchdf[parchdf['Parch'] != 0]        # 有父母子女
noparch = parchdf[parchdf['Parch'] == 0]     # 无父母子女

def sibpa_orno(df, place, title):
    fig.add_subplot(2,2,place)
    plt.pie(df['Survived'].value_counts(), autopct='%.1f%%', labels=['Nosurvived', 'Survived'])
    plt.title(title)

# fig = plt.figure()
# sibpa_orno(sibsp, 1, '有兄妹/配偶')
# sibpa_orno(nosibsp, 2, '无兄妹/配偶')
# sibpa_orno(parch, 3, '有父母/子女')
# sibpa_orno(noparch, 4, '无父母/子女')
# plt.savefig('有无亲人和存活的关系.jpg')


# 亲戚/父母子女多少与存活的关系
def paranal(df):
    # 不同亲戚数量的存活比例
    plt.figure()
    sns.barplot(x=df['SibSp'], y=df['Survived'], ci=None)
    plt.savefig('不同兄弟配偶数量的存活率.jpg')
    # 不同父母子女数量的存活比例
    plt.figure()
    sns.barplot(x=df['Parch'], y=df['Survived'], ci=None)
    plt.savefig('不同父母子女数量的存活率.jpg')
# paranal(parchdf)

'''
结合票的费用情况，研究票价和存活与否的关系
'''

price = train_data[['Survived', 'Fare']]

# # 票价分布
# fig, axes = plt.subplots(1, 2, figsize=(12,5))
# sns.distplot(price['Fare'], ax=axes[0])
# train_data.boxplot(column='Fare', by='Pclass', ax=axes[1])    # 根据船舱等级的票价分布
# plt.savefig('票价分布.jpg')

# # 生还者和未生还者的平均票价
# plt.figure()
# sns.barplot(x=price['Survived'], y=price.groupby('Survived')['Fare'].mean())
# plt.savefig('生还者和未生还者的平均票价.jpg')

# 不同船舱等级存活情况
# pclass_sur = train_data[['Survived', 'Pclass']]
# plt.figure()
# sns.barplot(x='Pclass', y='Survived', data=pclass_sur, ci=None)
# plt.savefig('不同船舱等级存活情况.jpg')

'''
生存预测
'''

from sklearn import neighbors
import warnings 
warnings.filterwarnings('ignore')

# 训练数据
train_d = train_data[['Survived', 'Age', 'Sex', 'Pclass', 'Fare', 'SibSp', 'Parch']].dropna()
train_d['Sex'][train_d['Sex'] == 'female'] = 1
train_d['Sex'][train_d['Sex'] == 'male'] = 0

# 测试数据
test_data = pd.read_csv('test.csv')
test_d = test_data[['Age', 'Sex', 'Pclass', 'Fare', 'SibSp', 'Parch']].dropna()
test_d['Sex'][test_d['Sex'] == 'female'] = 1
test_d['Sex'][test_d['Sex'] == 'male'] = 0


# 拟合训练数据
knn = neighbors.KNeighborsClassifier()
knn.fit(train_d[['Age', 'Sex', 'Pclass', 'Fare', 'SibSp', 'Parch']], train_d['Survived'])

# 预测测试数据
sur_predict = knn.predict(test_d)

test_d['surpre'] = sur_predict
# print('剩余%d名乘客预测生还率为:%.2f%%'%(len(test_d), (test_d['surpre'].sum() / len(test_d))*100))


s1 = test_d['surpre'].value_counts()
plt.pie(s1, colors=['lightgreen', 'yellowgreen'], autopct='%.2f%%', labels=['nosurvived', 'survived'])
# plt.savefig('整体存活比例预测.jpg')



