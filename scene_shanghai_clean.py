import pandas as pd
import re

data = pd.read_excel(r"D:\Fighting\excel_file\data_fromweb.xlsx")
# print(data.isnull().any())      # 是否有空值
# 遍历景点名称，统一景点名称为中文名称
for i, name in data['景点名称'].iteritems():
    data.at[i, '景点名称'] = ''.join(re.split(r"[A-Za-z]|[&：'()]", name))
# 删除重复行
data.drop_duplicates(subset=['景点名称'], inplace=True)
# 重新定义星级,首先去掉星级列无关的字符，只保留数字
for i, width in data['星级'].iteritems():
    data.at[i, '星级'] = width[6:-1]
# 遍历星级列，按总数五颗星，计算星级
for i, width_num in data['星级'].iteritems():
    star = (int(int(width_num) / 10)) / 2
    data.at[i, '星级'] = star
# 将列按照景点名称、星级、攻略、点评重新排版
scene_col = data['景点名称']
data.drop(columns='景点名称', inplace=True)
data.insert(1, '景点名称', scene_col)
stra_col = data['攻略数']
data.drop(columns='攻略数', inplace=True)
data.insert(2, '攻略数', stra_col)
# 将数据按照星级、点评数、攻略数排序
data.sort_values(by=['星级','点评数','攻略数'], ascending=False, inplace=True)
data.reset_index(drop=True, inplace=True)
data.to_excel(r"D:\Fighting\excel_file\scenarydata_shanghai_cleaned.xlsx")
