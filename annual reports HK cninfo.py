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
        "column":"hke",
        "searchkey":"年报",
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
# 该函数主要是通过http://www.cninfo.com.cn/new/data/szse_stock.json该json数据，找到每个stock对应的orgid和公司名称，并存储在字典中
def get_orgid():
    org_dict = {}
    company_dict = {}  # 新增：存储公司名称的字典
    org_json = requests.get("https://www.cninfo.com.cn/new/data/hke_stock.json").json()["stockList"]

    for i in range(len(org_json)):
        org_dict[org_json[i]["code"]] = org_json[i]["orgId"]
        company_dict[org_json[i]["code"]] = org_json[i]["zwjc"]  # 获取公司名称

    return org_dict, company_dict

if __name__ == "__main__":
    os.makedirs("年报", exist_ok=True)  # 确保目录存在

    # 读取并补齐港股代码
    pdlist = pd.read_excel("hkstockcode.xlsx", converters={'stockcode': str})["stockcode"]
    stock_list = [code.zfill(5) for code in pdlist.tolist()]  # ← 这里自动补0

    org_dict, company_dict = get_orgid()

    for stock in stock_list:
        if stock not in org_dict:
            print(f"⚠️ 跳过 {stock}（未在 hke_stock.json 中找到 orgId）")
            continue
        for year in ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
            req(stock, year, org_dict, company_dict)
            time.sleep(random.uniform(1, 3))