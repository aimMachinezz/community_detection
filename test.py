from cdlib import algorithms, evaluation
import networkx as nx

G = nx.DiGraph()

G.add_edge(1, 2, weight=4.7, timestamp=1234567890.0)
G.add_edge(2, 3, weight=3.9, timestamp=1234567891.0)
G.add_edge(3, 4, weight=2.9, timestamp=1234567892.0)


# 使用Louvain算法进行动态社区检测
communities = algorithms.louvain(g)

# 打印检测结果
for c in communities.communities:
    print(c)

# # 计算模块度
# q = evaluation.modularity_density_fitness(g, communities.communities, weight='weight', resolution=1.0)
# print('Modularity:', q.modularity())
