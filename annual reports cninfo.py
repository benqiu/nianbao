import requests,time,random,json
import pandas as pd
from datetime import datetime
import os

def req(stock,year,org_dict,company_dict):
    # post请求地址（巨潮资讯网的那个查询框实质为该地址）
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    # 表单数据，需要在浏览器开发者模式中查看具体格式
    data  = {
        "pageNum":"1",
        "pageSize":"30",
        "tabName":"fulltext",
        "stock":stock + "," + org_dict[stock] ,# 按照浏览器开发者模式中显示的参数格式构造参数
        "seDate":f"{str(int(year)+1)}-01-01~{str(int(year)+1)}-12-31",
        "column":"szse",
        "category":"category_ndbg_szsh",
        "isHLtitle": "true",
        "sortName":"time",
        "sortType": "desc"
        }
    # 请求头
    headers =  {"Content-Length": "201","Content-Type":"application/x-www-form-urlencoded"}
    # 发起请求
    req = requests.post(url,data=data,headers=headers)
    
    if json.loads(req.text)["announcements"]:# 确保json.loads(req.text)["announcements"]非空，是可迭代对象
        for item in json.loads(req.text)["announcements"]:# 遍历announcements列表中的数据，目的是排除英文报告和报告摘要，唯一确定年度报告或者更新版
            if "摘要" not in item["announcementTitle"]:
                if "英文" not in item["announcementTitle"]:
                    if "修订" in item["announcementTitle"] or "更新" in item["announcementTitle"]:
                        adjunctUrl = item["adjunctUrl"] # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
                        pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
                        r = requests.get(pdfurl)
                        # 获取公司名称
                        company_name = company_dict.get(stock, stock)
                        # 创建公司专属文件夹：公司名称_股票代码
                        company_folder = os.path.join("年报", f"{company_name}_{stock}")
                        os.makedirs(company_folder, exist_ok=True)
                        # 新文件名格式：公司名称+股票代码+年份+年度报告
                        filename = f"{company_name}_{stock}_{year}年度报告.pdf"
                        filepath = os.path.join(company_folder, filename)
                        f = open(filepath, "wb")
                        f.write(r.content)                       
                        print(f"{company_name}_{stock}_{year}年报下载完成！") # 打印进度
                        break
                    else:
                        adjunctUrl = item["adjunctUrl"] # "finalpage/2019-04-30/1206161856.PDF" 中间部分便为年报发布日期，只需对字符切片即可
                        pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
                        r = requests.get(pdfurl)
                        # 获取公司名称
                        company_name = company_dict.get(stock, stock)
                        # 创建公司专属文件夹：公司名称_股票代码
                        company_folder = os.path.join("年报", f"{company_name}_{stock}")
                        os.makedirs(company_folder, exist_ok=True)
                        # 新文件名格式：公司名称+股票代码+年份+年度报告
                        filename = f"{company_name}_{stock}_{year}年度报告.pdf"
                        filepath = os.path.join(company_folder, filename)
                        f = open(filepath, "wb")
                        f.write(r.content)                       
                        print(f"{company_name}_{stock}_{year}年报下载完成！") # 打印进度
                        break
# 该函数主要是通过http://www.cninfo.com.cn/new/data/szse_stock.json该json数据，找到每个stock对应的orgid，并存储在字典org_dict中
def get_orgid():
    """获取股票代码与 orgId、公司名称"""
    org_dict = {}
    company_dict = {}
    url = "http://www.cninfo.com.cn/new/data/szse_stock.json"

    resp = requests.get(url)
    resp.raise_for_status()
    org_json = resp.json()["stockList"]

    for item in org_json:
        org_dict[item["code"]] = item["orgId"]
        company_dict[item["code"]] = item["zwjc"]

    return org_dict, company_dict

if __name__ == "__main__":# 程序入口
    os.makedirs("年报", exist_ok=True)  # 确保目录存在    
    # 读取需要爬取的股票代码
    pdlist = pd.read_excel("stockcode.xlsx",converters={'stockcode':str})["stockcode"]
    stock_list = pdlist.to_numpy().tolist()

    org_dict, company_dict = get_orgid()

    for stock in stock_list:# 一层循环，按股票代码循环
        for year in ["2018","2019","2020","2021","2022","2023","2024"]:#]:# 二层按年份循环
            req(stock,year,org_dict,company_dict)# 调用req函数
            time.sleep(random.randint(0,2))# 适当休眠，避免爬虫过快