import json
import threading

import requests
import time
import os
import aiohttp
import asyncio
def get_change():
    start_number = 30000
    page_size = 500  # max:500
    base_url = 'https://codereview.qt-project.org/changes/'#'https://review.opendev.org/changes/?q=-owner:proposal-bot'# 'https://gerrit.wikimedia.org/r/changes/'
    query_statement = 'after:2021-02-16 AND before:2023-02-16'
    headers = {}
    dir_name = 'qt_review'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    while (True):
        json_size = get_onePage_changes(base_url, start_number, page_size, query_statement, dir_name)
        if int(json_size) < 100:
            print("失败写到" + str(start_number))
            start_number += page_size
        else:
            print("成功写到" + str(start_number))
            start_number += page_size
    print('done')


def get_onePage_changes(base_url, start_number, page_size, query_statement, dir_name) -> int:
    try:
        requests.adapters.DEFAULT_RETRIES = 60
        s = requests.session()
        s.keep_alive = False
        #s.proxies = {"https": "57.10.114.47:8000", "http": "32.218.1.7:9999"}
        r = s.get(url=base_url,  params={'O': 81, 'S': start_number, 'n': page_size,
                                        'q': query_statement})
        json_size = int(r.headers.get('Content-Length'))
        count = 0
        while json_size < 100 and count <= 20:
            time.sleep(2)
            r = s.get(url=base_url, params={'O': 81, 'S': start_number, 'n': page_size,
                'q': query_statement})
            json_size = int(r.headers.get('Content-Length'))
            print("fail", r.content, r.headers.get('Content-Length'))
            count += 1

        file_name = dir_name + '/' + str(start_number) + '.json'
        if count > 20:
            dir_name = 'qt_review/fail'
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            file_name = dir_name + '/' + str(start_number) + '失败.json'
        f = open(file_name, 'wb');
        f.write(r.content)
        f.close()
        return json_size
    except:
        print("重试")
        return get_onePage_changes(base_url, start_number, page_size, query_statement, dir_name)

#异步获取评论内容，一分钟可爬取500+页面
#默认不用代理，如果用代理则使用proxyHelper
def get_comments_and_detail(directory):
    base_url = 'https://codereview.qt-project.org/changes/'#'https://review.opendev.org/changes/' #'https://gerrit.wikimedia.org/r/changes/'

    count = 0

    dir_name = 'qt_comments/'

    # new_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(new_loop)
    # loop = asyncio.get_event_loop()
    # tasks = []

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)



    for filename in os.listdir(directory):
        hash_set = set()
        for file_name in os.listdir(dir_name):
            hash_set.add(file_name)
        if filename in hash_set:
            print("已有", filename)
            continue
        try:
            with open(os.path.join(directory, filename), 'rb') as f:
                print(filename, "start")
                content = f.read()
                index = content.index(b'\n')
                content = content[index+1:]
                changes_info = json.loads(content)
                map_all = {}
                for index in range(len(changes_info)):
                    retry = 0
                    comment_count = changes_info[index]['total_comment_count']
                    id = changes_info[index]['id']
                    print(filename, id)
                    map_all[id] = {}
                    count = count + 1
                    detail_url = base_url + str(id) + '/detail'
                    response = requests.get(detail_url)
                    while (response.status_code < 200 or response.status_code >= 300) and retry <= 5:
                        print("网络异常", detail_url)
                        time.sleep(3)
                        retry = retry + 1
                        response = requests.get(detail_url)
                    if retry > 5:
                        continue
                    detail_json = json.loads(response.content[response.content.index(b'\n')+1:])
                    owner_id = detail_json["owner"]["_account_id"]
                    owner_name = detail_json["owner"]["name"]
                    owner_email = ''
                    if "email" in detail_json["owner"]:
                        owner_email = detail_json["owner"]["email"]

                    map_all[id]['owner_id'] = owner_id
                    map_all[id]['owner_name'] = owner_name
                    map_all[id]['owner_email'] = owner_email

                    map_all[id]['labels'] = {}
                    if "all" in detail_json["labels"]["Code-Review"]:
                        map_all[id]['labels'] = detail_json["labels"]["Code-Review"]["all"]
                    #print(id, owner_id, owner_name, owner_email, map_all[id]['labels'])
                    map_all[id]['comments'] = {}
                    if comment_count > 0:
                        comment_url = base_url + str(id) + '/comments'
                        response = requests.get(comment_url)
                        while response.status_code < 200 or response.status_code >= 300:
                            print("网络异常", comment_url)
                            response = requests.get(comment_url)
                        comment_json = json.loads(response.content[response.content.index(b'\n')+1:])
                        if len(comment_json) > 0:
                            for key in comment_json.keys():
                                comment_list = comment_json[key]
                                map_all[id]['comments'][key] = comment_list
                json_file_name = dir_name + '/' + filename
                #print(map_all, "map_all")
                # 写入到文件
                with open(json_file_name, "w") as file:
                    json.dump(map_all, file)

        except Exception as e:
            print(e, "==================异常======================!" + filename)
            continue
    print('done', count)

# async def download(url, dir_name, number):
#     async with aiohttp.ClientSession() as session:
#         file_name = dir_name + '/' + number + '.json'
#         await fetchData(url, number, file_name, session)
#         print("变更：" +  number + " 的数据获取完成")
#
#
# async def fetchData(url, number, file_name, session):
#     try:
#         #proxy = await Config.getProxy()
#         headers = selectheaders()
#         async with session.get(url, ssl=False
#                 ) as response:
#             json_size = int(response.headers.get('Content-Length'))
#             if json_size < 10:
#                 print(number, json_size)
#                 return
#             f = open(file_name, 'wb');
#             s = await response.text();
#             bytes = s.encode('utf-8')
#             f.write(bytes)
#             f.close()
#     except:
#         print("重试")
#         fetchData(url, number, file_name, session)

# Gerrit API URL for the change
#get_change()
if __name__ == '__main__':

    t1 = threading.Thread(target=get_comments_and_detail,args=('qt_review/',))     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
    # t2 = threading.Thread(target=get_comments_and_detail,args=('review1/',))
    # t3 = threading.Thread(target=get_comments_and_detail, args=('review2/',))
    # t4 = threading.Thread(target=get_comments_and_detail, args=('review3/',))
    t1.start()
    t1.join()
    os.system("shutdown -s")
    # t2.start()
    # t3.start()
    # t4.start()
    # get_change()


# url = "https://gerrit.wikimedia.org/changes/?q=status:open+OR+status:closed"
#
# response = requests.get(url)
#
# if response.status_code == 200:
#     changes = response.json()
#     change_ids = [change["id"] for change in changes]
# else:
#     raise Exception("Failed to retrieve changes, status code: {}".format(response.status_code))

# for change_id in change_ids:
#     url = f"https://gerrit.wikimedia.org/changes/{change_id}/detail"
#
#     # Send GET request to Gerrit API
#     response = requests.get(url)
#
#     # Check if the request was successful
#     if response.status_code == 200:
#         # Parse the JSON data from the response
#         data = response.json()
#
#         # Print the change details
#         print("Change ID:", data["id"])
#         print("Subject:", data["subject"])
#         print("Committer:", data["committer"]["email"])
#
#         # Loop through each comment in the change
#         for comment in data["comments"]:
#             # Print the comment details
#             print("Comment ID:", comment["id"])
#             print("Comment:", comment["message"])
#             print("Author:", comment["author"]["email"])
#             print("-----------------------------")
#
#         # Loop through each vote in the change
#         for vote in data["votes"]:
#             # Print the vote details
#             print("Vote:", vote["value"])
#             print("Author:", vote["by"]["email"])
#             print("-----------------------------")
#     else:
#         # Print error message if the request was unsuccessful
#         print("Failed to fetch data from Gerrit")