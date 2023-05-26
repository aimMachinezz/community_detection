import tnetwork as tn
import networkx as nx
import seaborn as sns
import pickle
import json

# 从文件中加载字典对象
with open('data.pkl', 'rb') as f:
    map_graph = pickle.load(f)

dg = tn.DynGraphSN()
for t in range(1, 10):
    for reviewer_id in map_graph[t].keys():
        for owner_id in map_graph[t][reviewer_id].keys():
            dg.add_interaction(reviewer_id, owner_id, t)

coms = tn.DCD.smoothed_louvain(dg)

# 转换为标准字典
dict_data = {str(key): value for key, value in coms.snapshots.items()}
dict_data = {key: list(value) for key, value in dict_data.items()}
sorted_dict = dict()
sorted_dict = coms.snapshots
dict_data = dict(sorted_dict)
# for time in sorted_dict.keys():
#     dict_data[time] = dict()
#     for com in sorted_dict[time].keys():
#         dict_data[time][com] = sorted_dict[time][com]
# 保存为 JSON 文件
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError
with open('tnetwork_smoothed_louvain.json', 'w') as f:
    json.dump(dict_data, f, default=set_default, ensure_ascii=False, indent=2)

