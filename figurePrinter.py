import pandas as pd
import collections
import matplotlib.pyplot as plt
import numpy as np

def printImage(repo_name, version):
    source_data = pd.read_excel('F:/pythonProject/poison/data/' + repo_name + '_feature_score.xlsx')
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
        plt.text(bins[x]- 0.05, k[x] + 150, k[x], ha='center', va='center',
                 color='black', fontsize=10)
    print(repo_name + "结果：")

    #plt.show()
    img_path = "calculate/img/"
    plt.savefig(img_path + repo_name + '_' + version + '.png')
    plt.close()