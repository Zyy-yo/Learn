'''
采集B站弹幕数据
弹幕是通过加载xml文档来显示在视频上的，不会在html的源代码上来体现
xml和html都是一种标记语言
视频中弹幕对应的xml语言所在的链接如何找到？查看源代码，搜索cid，相当于视频的ID
B站弹幕网址：'https://comment.bilibili.com/%s.xml'%cid
'''
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
'''
打开一个视频，鬼灭之刃第一集，查看源代码，在源代码里找到cid，发现很多cid
找到对应该视频标题的cid，该视频为第一话 残酷，aid为48487753，对应的cid是92468919
'''
# 获得所需弹幕的网址并访问、解析
url = 'https://comment.bilibili.com/92468919.xml'
r = requests.get(url)
# 使用'utf-8'编码，否则可能会出现乱码
r.encoding = 'utf-8'                     
soup = BeautifulSoup(r.text, 'lxml')
d = soup.find_all('d')
# print(d[0])
# <d p="1215.73900,5,25,16707842,1564587126,0,ff8dcf24,19631938471460864">屁的反作用力，合情合理</d>
# 需要的弹幕在d标签的元素里，此外我们需要提取另外一个数据，即时间戳。观察在属性p中'1564587126'应该属于秒级时间戳
# 首先要提取到属性p，如第一个标签d[0]['p']提取之后："1215.73900,5,25,16707842,1564587126,0,ff8dcf24,19631938471460864"
# 再提取索引为4，即第五个位置的时间戳，用datetime.fromtimestamp(1564587126)将秒级时间戳转化为本地时间 2019-07-31 23:32:06
data = []
for i in d:
    dic = {}
    # 提取到的时间戳是字符串，首先将它转为整数，然后装载到datetime.fromtimestamp里
    dic['时间'] = datetime.fromtimestamp(int(i['p'].split(',')[4]))
    dic['弹幕'] = i.text
    data.append(dic)

df = pd.DataFrame(data)
df.sort_values(by='时间',inplace=True)
df.to_excel(r'D:\PY\excel_file\b站弹幕1.xlsx', index=False)

# 上面是一个视频的弹幕数据采集，下面是多个视频弹幕
# 还是以上面的视频为例
# 复制带有cid那段的代码
textc = '''"epList":[{"aid":48487753,"cid":92468919,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F1a6484ca5def2e358fa1f6349a9119019eb69f54.jpg","duration":1425107,"ep_id":267851,"episode_status":2,"from":"bangumi","index":"1","index_title":"残酷","mid":928123,"page":1,"pub_real_time":"2019-04-07 00:00:00","section_id":36308,"section_type":0,"vid":""},
        {"aid":49109190,"cid":93557037,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F2f7385fab9f49846cab6ca2396c331ad4bed5d5a.jpg","duration":1425065,"ep_id":267852,"episode_status":2,"from":"bangumi","index":"2","index_title":"培育师 鳞泷左近次","mid":928123,"page":1,"pub_real_time":"2019-04-14 00:00:00","section_id":36308,"section_type":0,"vid":""},
            {"aid":49890844,"cid":87351529,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F31e54fa3308c7ba5678e2fbb323ed1bea92d4e21.jpg","duration":1425406,"ep_id":267853,"episode_status":2,"from":"bangumi","index":"3","index_title":"锖兔与真菰","mid":928123,"page":1,"pub_real_time":"2019-04-21 00:00:00","section_id":36308,"section_type":0,"vid":""},
                {"aid":50612559,"cid":103750248,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F3945723c6e64d8a361221add07ee778fc75c7ebb.jpg","duration":1425107,"ep_id":267854,"episode_status":2,"from":"bangumi","index":"4","index_title":"最终选拔","mid":928123,"page":1,"pub_real_time":"2019-04-28 00:00:00","section_id":36308,"section_type":0,"vid":""},
                    {"aid":51400999,"cid":92472194,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F6b8390ce35deead6fe10b344cab294ff8f0a1936.jpg","duration":1425193,"ep_id":267855,"episode_status":2,"from":"bangumi","index":"5","index_title":"自己的钢","mid":928123,"page":1,"pub_real_time":"2019-05-05 00:00:00","section_id":36308,"section_type":0,"vid":""},
                        {"aid":52103572,"cid":92472373,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F783551c560b7bb67f20ce608b56f6d9974b3efa5.jpg","duration":1425235,"ep_id":267856,"episode_status":2,"from":"bangumi","index":"6","index_title":"带着鬼的剑士","mid":928123,"page":1,"pub_real_time":"2019-05-12 00:00:00","section_id":36308,"section_type":0,"vid":""},
                            {"aid":52834242,"cid":92468637,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F6f1e339be3d1332e99bfa9a4fe5e27f2d97874d6.jpg","duration":1425235,"ep_id":267857,"episode_status":2,"from":"bangumi","index":"7","index_title":"鬼舞辻无惨","mid":928123,"page":1,"pub_real_time":"2019-05-19 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                {"aid":53525458,"cid":93640630,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002Fe64baa0d3f50d87fa435d7385a33092543a03d39.jpg","duration":1425363,"ep_id":267858,"episode_status":2,"from":"bangumi","index":"8","index_title":"幻惑的血香","mid":928123,"page":1,"pub_real_time":"2019-05-26 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                    {"aid":54247495,"cid":95287956,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F1be0229d0038082df9bf4d10cc35a43f06764cc8.jpg","duration":1425235,"ep_id":267859,"episode_status":2,"from":"bangumi","index":"9","index_title":"手球鬼与箭头鬼","mid":928123,"page":1,"pub_real_time":"2019-06-02 00:00:03","section_id":36308,"section_type":0,"vid":""},
                                        {"aid":54855871,"cid":95941164,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F8e76367b57cb7a91077d38b3eb0bbc3620d8a650.jpg","duration":1425193,"ep_id":267860,"episode_status":2,"from":"bangumi","index":"10","index_title":"一直在一起","mid":928123,"page":1,"pub_real_time":"2019-06-09 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                            {"aid":55547365,"cid":97118642,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F764f75c2db2259c61f86d908ed4ea3d31ab64274.jpg","duration":1425491,"ep_id":267861,"episode_status":2,"from":"bangumi","index":"11","index_title":"鼓之宅邸","mid":928123,"page":1,"pub_real_time":"2019-06-16 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                {"aid":56426667,"cid":98599834,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002Fd3827f29ac3f0d1e7539079da76266f5d242522c.jpg","duration":1425193,"ep_id":267862,"episode_status":2,"from":"bangumi","index":"12","index_title":"野猪露牙 善逸沉睡","mid":928123,"page":1,"pub_real_time":"2019-06-23 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                    {"aid":57259320,"cid":103750897,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F7ab014b29c04889a777ded52e0d53f77a2418f30.jpg","duration":1425150,"ep_id":267863,"episode_status":2,"from":"bangumi","index":"13","index_title":"比生命更重要的东西","mid":928123,"page":1,"pub_real_time":"2019-06-30 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                        {"aid":58066884,"cid":101315749,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F3a8a96158b567745f4e319a31c93b31b9bf3bbf4.jpg","duration":1425363,"ep_id":267864,"episode_status":2,"from":"bangumi","index":"14","index_title":"紫藤花家纹之家","mid":928123,"page":1,"pub_real_time":"2019-07-07 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                            {"aid":58888853,"cid":102665280,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F4c8f6e41f37f40c5f257d72d09f08ec79c974528.jpg","duration":1425491,"ep_id":267865,"episode_status":2,"from":"bangumi","index":"15","index_title":"那田蜘蛛山","mid":928123,"page":1,"pub_real_time":"2019-07-14 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                                {"aid":59833920,"cid":104221434,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002Faca6f5bc683a949ca6847278f18452dceeacc3ac.jpg","duration":1425491,"ep_id":267866,"episode_status":2,"from":"bangumi","index":"16","index_title":"让自己以外的某人前进","mid":928123,"page":1,"pub_real_time":"2019-07-21 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                                    {"aid":60864596,"cid":107591853,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F2b53402f3182ab1e981a91d92935fae37ec34577.jpg","duration":1425363,"ep_id":267867,"episode_status":2,"from":"bangumi","index":"17","index_title":"集中一点登峰造极","mid":928123,"page":1,"pub_real_time":"2019-07-28 00:00:00","section_id":36308,"section_type":0,"vid":""},
                                                                        {"aid":61899914,"badge":"会员","badge_type":0,"cid":107630711,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002Fb85cddf4e8e9edcedd20cced3c5ac14f64439f8c.jpg","duration":1425193,"ep_id":267868,"episode_status":13,"from":"bangumi","index":"18","index_title":"虚假的羁绊","mid":928123,"page":1,"pub_real_time":"2019-08-04 00:00:03","section_id":36308,"section_type":0,"vid":""},
                                                                            {"aid":47074440,"cid":82436359,"cover":"http:\u002F\u002Fi0.hdslb.com\u002Fbfs\u002Farchive\u002F4d08237061deb9ca90968eb0219c86c5688590b1.jpg","duration":53158,"ep_id":265685,"episode_status":2,"from":"bangumi","index":"PV","index_title":"","mid":408002864,"page":1,"pub_real_time":"2019-03-23 12:16:00","section_id":36358,"section_type":1,"vid":""}'''
# 按照"cid":位置分割textc，得到的数据除第一行外，其他行都是以cid的数字开头的
cids = textc.split('"cid":')
# 除第一行外，其他带有cid的行长度都大于50，因此从其他行里以推导式遍历出cid
cid = [x.split(',')[0] for x in cids if len(x) > 50]
# 以免有重复数据，将cid放入集合，因集合元素的唯一性来去重，再转回列表
cid = list(set(cid))
# 定义函数，输入cid输出url
def cid_to_url(c):
    return 'https://comment.bilibili.com/%s.xml'%c
# 定义函数，输入url输出data
def url_to_data(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    d = soup.find_all('d')
    data1 = []
    for i in d:
        dic = {}
        dic['时间'] = datetime.fromtimestamp(int(i['p'].split(',')[4]))
        dic['弹幕'] = i.text
        data1.append(dic)
    return data1
# 定义函数，将上面两个函数整合到一起，实现调用所有cid生成所有的url，然后遍历url返回最终数据
def cid_url_data(cid):
    urls = [cid_to_url(c) for c in cid]
    alldata = []
    for url in urls:
        datalst = url_to_data(url)
        alldata.extend(datalst)
        print('已采集%s条弹幕'%len(alldata))
    return alldata
alldata = cid_url_data(cid)
df_all = pd.DataFrame(alldata)
df_all.sort_values(by='时间',inplace=True)
df_all.to_excel(r'D:\PY\excel_file\b站弹幕.xlsx', index=False)