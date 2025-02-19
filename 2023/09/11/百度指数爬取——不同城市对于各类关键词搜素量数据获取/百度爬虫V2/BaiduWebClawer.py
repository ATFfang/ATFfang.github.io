import queue
from queue import Queue
from typing import List
import traceback
import time
from qdata.baidu_index import get_search_index
from qdata.baidu_index.common import check_keywords_exists, split_keywords
import csv

# 存储城市id与名称的键值对，全局变量
global CITY_MAP

global STARTTIME
STARTTIME = '2023-09-5'

global ENDTIME
ENDTIME = '2023-9-5'


# 获取百度指数的函数
def get_baidu_index(keywords_list: List[List[str]], citycode, cookiesQueue):

    # cookie
    cookies = cookiesQueue.queue[0]

    # 当前请求的五个关键词
    requested_keywords = []

    # 一组（五个）关键词为元素的队列
    q_keywords = queue.Queue(-1)

    # 将keywordlist分组后置入队列q_keywords
    for splited_keywords_list in split_keywords(keywords_list):
        q_keywords.put(splited_keywords_list)

    # 当次请求的城市名称
    cityname = str(CITY_MAP[str(citycode)])

    print("开始请求"+str(CITY_MAP[str(citycode)])+"的百度指数")

    # 遍历q_keywords，每一组q_keywords请求一次
    # 获得的数据输入data
    datas = []
    while not q_keywords.empty():

        # 取出一组
        cur_keywords_list = q_keywords.get()

        # 增加容错率：若错误，则换cookie重试
        # 当前尝试次数
        attempts = 0
        # 最大尝试次数
        max_attempts = 3

        while attempts < max_attempts:
            try:
                print(f"开始请求: {cur_keywords_list}")
                # 这一组获得的data
                current_data = []
                for index in get_search_index(
                        keywords_list=cur_keywords_list,
                        start_date=STARTTIME,
                        end_date=ENDTIME,
                        cookies=cookies,
                        area=citycode
                ):
                    index["keyword"] = ",".join(index["keyword"])
                    # 将输出的index数据转化为list
                    index_list = [citycode, cityname, index['keyword'], index['type'], index['date'], index['index']]
                    current_data.append(index_list)
                requested_keywords.extend(cur_keywords_list)
                print(f"请求完成: {cur_keywords_list}")
                datas.extend(current_data)
                time.sleep(0.2)
                break

            except Exception as e:
                traceback.print_exc()
                print(f"请求出错, requested_keywords: {requested_keywords}，错误为{e}")
                time.sleep(5)
                cookies = cookiesQueue.get()
                attempts += 1

    return datas


# 主函数
if __name__ == "__main__":

    # 存放目标关键词
    keywords_list = []
    # 输入目标关键词
    with open('输入数据/Keyword.csv') as DCityfile:
        reader = csv.reader(DCityfile)
        for row in reader:
            listcity = [row[1]]
            keywords_list.append(listcity)

    # 存放起始的城市（搜索者所在地）
    CITY_MAP = {}
    # 输入OCity的城市id与名
    with open('输入数据/Ocity.csv') as OCityfile:
        reader = csv.reader(OCityfile)
        for row in reader:
            CITY_MAP[row[0]] = row[1]

    # 定义一个队列cookiesQueue，存放所有的cookies
    cookiesQueue = Queue(-1)
    with open('输入数据/Allcookies.txt') as cookiesIN:
        reader = csv.reader(cookiesIN)
        for row in reader:
            cookiesQueue.put(row[0])

    # 总存储空间
    all_data = []

    # 爬取数据并写入
    for citycode in CITY_MAP.keys():
        data = get_baidu_index(keywords_list, citycode, cookiesQueue)
        all_data.extend(data)

    with open('输出数据/output.csv', 'a', newline='') as fileOut:
        writer = csv.writer(fileOut)
        for row in all_data:
            writer.writerow(row)





