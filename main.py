import os
import pickle

import infomap
import json

import pandas as pd
import collections
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from cdlib import algorithms, evaluation
from cdlib import TemporalClustering

import os


def printImage(df):
    source_data = df
    data = pd.DataFrame(source_data)
    re_list = np.array(data['score']).tolist()
    # count = Counter(re_list)
    # list_x = list(set(re_list))
    # list_y = []
    # for item in list_x:
    #     list_y.append(count[item])

    plt.xlabel = "score"
    plt.ylabel = "count"

    # plt.scatter(list_x, list_y, marker='o')
    # plt.show()
    bins = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
    plt.hist(re_list,  bins = bins, rwidth = 0.8,
    histtype = 'bar', orientation = 'vertical')
    k = {}
    for i in re_list:


        for a, b in enumerate(sorted(bins)):
            if i > b and i < bins[a + 1]:
                try:
                    k[a + 1] += 1
                except:
                    k[a + 1] = 1
    for x in k:
        plt.text(bins[x] - 0.05, k[x] + 150, k[x], ha='center', va='center',
                 color='black', fontsize=10)

    plt.show()
    img_path = "calculate/img/"
    plt.close()

def split(df):
    # 按“quarter”列分组
    groups = df.groupby('quarter')

    # 遍历分组结果，保存为单独的csv文件
    for name, group in groups:
        filename = './data/split/'f'{name}.csv'
        group.to_csv(filename, index=False)
        print(f'{filename} saved successfully!')

def init():
    # 读取 CSV 文件
    data = pd.read_csv('F:/pythonProject/Data/OpenStack/OpenStack_comment_list.csv', header=0)
    # data = pd.read_excel('test.xlsx')
    # 将"updated"列转换为datetime类型
    data['updated'] = pd.to_datetime(data['updated'])

    # 自定义一个函数，实现将日期转换为季度的功能
    def quarter_to_number(date):
        quarter = (date.month-1)//3+1 # 计算季度
        year = date.year-data['updated'].min().year
        return year*4+quarter # 计算季度对应的数字

    # 对"updated"列中的每一个日期应用上述函数
    data['quarter'] = data['updated'].apply(quarter_to_number)

    data = data.sort_values('quarter')
    data.to_csv('quarter.csv', index=False)
    # 输出结果
    print(data)

def get_match(tc):
    jaccard = lambda x, y:  len(set(x) & set(y)) / len(set(x) | set(y))
    matches = tc.community_matching(jaccard, two_sided=True)
    print(matches)

def data_trans():
    import pickle
    map_graph = {}
    for t in range(1, 10):
        map_graph[t] = dict()
        count = 0
        data = pd.read_csv(f'F:/pythonProject/community_detection/data/split/{t + 20}.csv', header=0)
        # 遍历数据集
        for index, row in data.iterrows():
            count += 1
            reviewer_id = row['author']
            file_name = 'F:/pythonProject/Data/OpenStack/changes/' + 'OpenStack_' + str(
                row['change_id']) + '_change.json'
            if reviewer_id not in map_graph[t]:
                map_graph[t][reviewer_id] = {}
            with open(file_name) as f:
                json_file = json.load(f)
                owner_id = json_file["owner"]["_account_id"]
                if owner_id not in map_graph[t][reviewer_id]:
                    map_graph[t][reviewer_id][owner_id] = 1
                else:
                    map_graph[t][reviewer_id][owner_id] = map_graph[t][reviewer_id][owner_id] + 1

    # 保存字典对象到文件
    with open('data.pkl', 'wb') as f:
        pickle.dump(map_graph, f)

def get_com_static():
    tc = TemporalClustering()
    for t in range(21, 24):
        weights = list()
        map_graph = {}
        count = 0
        data = pd.read_csv(f'./data/split/{t}.csv', header=0)
        # 遍历数据集
        for index, row in data.iterrows():
            count += 1
            reviewer_id = row['author']
            file_name = 'F:/pythonProject/Data/OpenStack/changes/' + 'OpenStack_' + str(row['change_id']) + '_change.json'
            if reviewer_id not in map_graph:
                map_graph[reviewer_id] = {}
            with open(file_name) as f:
                json_file = json.load(f)
                owner_id = json_file["owner"]["_account_id"]
                if owner_id not in map_graph[reviewer_id]:
                    map_graph[reviewer_id][owner_id] = 1
                else:
                    map_graph[reviewer_id][owner_id] = map_graph[reviewer_id][owner_id] + 1
        G = nx.DiGraph()

        for reviewer_id in map_graph.keys():
            for owner_id in map_graph[reviewer_id].keys():
                G.add_edge(reviewer_id, owner_id, weight=map_graph[reviewer_id][owner_id])
                weights.append(map_graph[reviewer_id][owner_id])
        coms = algorithms.rb_pots(G, weights=weights)  # here any CDlib algorithm can be applied
        print(evaluation.newman_girvan_modularity(G, coms))
        tc.add_clustering(coms, t)

    json_obj = json.loads(tc.to_json())
    with open('test_nomatching.json', 'w', encoding='utf8') as f2:
        # ensure_ascii=False才能输入中文，否则是Unicode字符
        # indent=2 JSON数据的缩进，美观
        json.dump(json_obj, f2, ensure_ascii=False, indent=2)
    jaccard = lambda x, y: len(set(x) & set(y)) / len(set(x) | set(y))
    matches = tc.community_matching(jaccard, two_sided=True)

    json_obj = json.loads(tc.to_json())
    with open('test.json','w',encoding='utf8') as f2:
        # ensure_ascii=False才能输入中文，否则是Unicode字符
        # indent=2 JSON数据的缩进，美观
        json.dump(json_obj, f2, ensure_ascii=False, indent=2)

def get_com_dynamic():
    import dynetx as dn
    dg = dn.DynGraph()
    map_graph = {}
    with open('data.pkl', 'rb') as f:
        map_graph = pickle.load(f)

    for t in range(1, 10):
        for reviewer_id in map_graph[t].keys():
            for owner_id in map_graph[t][reviewer_id].keys():
                dg.add_interaction(reviewer_id, owner_id, t)

    coms = algorithms.tiles(dg)


    json_obj = json.loads(coms.to_json())
    with open('cdlib_tiles.json', 'w', encoding='utf8') as f2:
        # ensure_ascii=False才能输入中文，否则是Unicode字符
        # indent=2 JSON数据的缩进，美观
        json.dump(json_obj, f2, ensure_ascii=False, indent=2)
        # f2.write(json.dumps(tc.to_json().strip('"'), ensure_ascii=False, indent=2))

    for t in range(1, 10):
        set_total = set()
        set_dynamic = set()
        G = nx.DiGraph()
        for reviewer_id in map_graph[t].keys():
            set_total.add(reviewer_id)
            for owner_id in map_graph[t][reviewer_id].keys():
                G.add_edge(reviewer_id, owner_id, weight=map_graph[t][reviewer_id][owner_id])
                set_total.add(owner_id)

        coms_t = coms.get_clustering_at(t)
        for com in coms_t.communities:
            for userid in com.keys():
                set_dynamic.add(userid)
        #print(len(dg.nodes(t=t)))
        print(len(set_total), len(set_dynamic))


        print(evaluation.newman_girvan_modularity(G, coms_t))

get_com_dynamic()
# data = pd.read_csv('quarter.csv', header=0)
# split(data)

# map_graph = {}
# count = 0
# # 遍历数据集
# for index, row in data.iterrows():
#     count += 1
#     reviewer_id = row['author']
#     file_name = 'F:/pythonProject/Data/OpenStack/changes/' + 'OpenStack_' + str(row['change_id']) + '_change.json'
#     if reviewer_id not in map_graph:
#         map_graph[reviewer_id] = {}
#     with open(file_name) as f:
#         json_file = json.load(f)
#         owner_id = json_file["owner"]["_account_id"]
#         if owner_id not in map_graph[reviewer_id]:
#             map_graph[reviewer_id][owner_id] = 1
#         else:
#             map_graph[reviewer_id][owner_id] = map_graph[reviewer_id][owner_id] + 1
#
# print(map_graph)
# set_total = set()
# set_owner = set()
# set_reviewer = set()
# for reviewer_id in map_graph.keys():
#     set_total.add(reviewer_id)
#     set_reviewer.add(reviewer_id)
#     for owner_id in map_graph[reviewer_id].keys():
#         set_total.add(owner_id)
#         set_owner.add(owner_id)
# print("用户总数：", len(set_total), "数据总量：", count)
# print("owner总数：", len(set_owner), "reviewer总数：", len(set_reviewer))

# for file_name in os.listdir(dir_name):
#     with open(os.path.join(dir_name, file_name), 'rb') as f:
#         content = f.read()
#         json_file = json.loads(content)
#         if len(json_file) <= 0:
#             continue
#         for key in json_file.keys():
#             count += 1
#             print(file_name, "start", key)
#             if len(json_file[key]) <= 0:
#                 continue
#             owner_id = json_file[key]["owner_id"]
#             if owner_id not in map_graph:
#                 map_graph[owner_id] = {}
#             json_comment = json_file[key]["comments"]
#             if len(json_comment) > 0:
#                 for comment_file in json_comment.keys():
#                     for index in range(len(json_comment[comment_file])):
#                         reviewer_id = json_comment[comment_file][index]["author"]["_account_id"]
#                         if reviewer_id not in map_graph[owner_id]:
#                             map_graph[owner_id][reviewer_id] = 1
#                         else:
#                             map_graph[owner_id][reviewer_id] = map_graph[owner_id][reviewer_id] + 1
# #graph = infomap.Infomap("--two-level --directed")
# graph = infomap.Infomap("--directed")
# for owner_id in map_graph.keys():
#     for reviewer_id in map_graph[owner_id].keys():
#         graph.add_link(reviewer_id, owner_id, map_graph[owner_id][reviewer_id])
#
# # Run Infomap algorithm
# graph.run()
#
# # Get communities
# print(f"Found {graph.num_top_modules} modules with codelength: {graph.codelength}")
# # Print communities
# # for node in graph.tree:
# #     print("Node {} is in community {}".format(node.physical_id, node.module_index))
# print("Result")
# print("\n#node module")
# map_result = {}
# for node in graph.tree:
#     if node.is_leaf:
#         map_result[node.node_id] = {}
#         map_result[node.node_id]["module"] = node.module_id
#
#         print(node.node_id, node.module_id)
# data = pd.DataFrame.from_dict(map_result)
# df = pd.DataFrame(data.values.T, columns=data.index, index=data.columns)
# df.index.name = 'user_id'
# print(df)
# set_total = set()
# set_owner = set()
# set_reviewer = set()
# for owner_id in map_graph.keys():
#     set_total.add(owner_id)
#     set_owner.add(owner_id)
#     for reviewer_id in map_graph[owner_id].keys():
#         set_total.add(reviewer_id)
#         set_reviewer.add(reviewer_id)
# print("用户总数：", len(set_total), "数据总量：", count)
# print("owner总数：", len(set_owner), "reviewer总数：", len(set_reviewer))
#
# community_counts = df['module'].value_counts()
# community_counts = pd.DataFrame(community_counts)
# community_counts.index.name = 'module'
# community_counts.columns = ['count']
# community_counts.to_excel(dir_name.split("_")[0] + '.xlsx', index=True)
# # 画出直方图
# # community_counts.plot.bar()
# #
# # # 添加数据标签
# # for i in range(len(community_counts)):
# #     plt.text(x=i, y=community_counts[i+1]+5, s=str(community_counts[i+1]), ha='center', fontsize=10)
# #
# # # 显示图片
# # plt.show()