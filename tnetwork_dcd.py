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

coms = tn.DCD.smoothed_graph(dg)
scores=[]
scores, sizes = tn.DCD.quality_at_each_step(coms, dg)
print(" ")
print(scores)
average = sum(scores) / len(scores)
print(average)

for t in range(1, 10):
    set_total = set()
    set_dynamic = set()
    G = nx.DiGraph()
    for reviewer_id in map_graph[t].keys():
        set_total.add(reviewer_id)
        for owner_id in map_graph[t][reviewer_id].keys():
            G.add_edge(reviewer_id, owner_id, weight=map_graph[t][reviewer_id][owner_id])
            set_total.add(owner_id)

    coms_t = coms.communities(t)
    for com in coms_t.keys():
        com_set = set()
        for userid in coms_t[com]:
            set_dynamic.add(userid)
    print(len(set_total), len(set_dynamic))
# 转换为标准字典
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

