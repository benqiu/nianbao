import requests, time, random, json
import pandas as pd
from datetime import datetime
import os
import argparse

def download_quarterly_report(stock, year, quarter, org_dict, company_dict, category_code, quarter_name):
    """下载季报的通用函数 - 使用新的披露页面筛选逻辑"""

    try:
        # 构建新的筛选地址
        org_id = org_dict[stock]
        disclosure_url = f"http://www.cninfo.com.cn/new/disclosure/stock?orgId={org_id}&stockCode={stock}#latestAnnouncement"

        print(f"  访问披露页面: {disclosure_url}")

        # 创建session并设置请求头
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': f'http://www.cninfo.com.cn/new/disclosure/stock?orgId={org_id}&stockCode={stock}'
        })

        # 根据季度设置查询时间范围
        if quarter == 1:
            se_date = f"{year}-01-01~{year}-04-30"
        elif quarter == 2:
            se_date = f"{year}-04-01~{year}-08-31"
        elif quarter == 3:
            se_date = f"{year}-07-01~{year}-10-31"
        else:
            se_date = f"{year}-10-01~{int(year)+1}-04-30"

        # 使用原始API获取公告列表，使用正确的POST请求格式
        api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

        # 构建POST请求数据
        post_data = {
            "pageNum": "1",
            "pageSize": "30",
            "tabName": "fulltext",
            "stock": f"{stock},{org_id}",
            "seDate": se_date,
            "column": "szse",
            "category": category_code,
            "isHLtitle": "true",
            "sortName": "time",
            "sortType": "desc"
        }

        # 设置正确的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.cninfo.com.cn',
            'Referer': f'http://www.cninfo.com.cn/new/disclosure/stock?orgId={org_id}&stockCode={stock}'
        }

        # 使用POST请求获取数据
        api_response = session.post(api_url, data=post_data, headers=headers)
        api_response.raise_for_status()

        announcements = api_response.json().get("announcements", [])

        if announcements:
            print(f"  找到 {len(announcements)} 条公告")
            for item in announcements:
                title = item["announcementTitle"]
                print(f"  公告标题: '{title}'")
                # 过滤条件：排除英文版、摘要等，确保是目标季度的报告
                # 基于实际报告名称格式优化匹配逻辑
                should_download = False
                if "摘要" not in title and "英文" not in title:
                    if quarter == 1:
                        # 匹配一季度相关关键词：支持"一季度报告"、"第1季度"、"第一季度"等格式
                        if any(keyword in title for keyword in ["一季度", "一季报", "第1季度", "第一季度", "1季度"]):
                            should_download = True
                            print(f"    匹配: 一季度/一季报/第1季度/第一季度")
                    elif quarter == 2:
                        # 匹配半年报相关关键词：支持"半年度报告"、"半年报"、"第2季度"等格式
                        if any(keyword in title for keyword in ["半年度", "半年报", "第2季度", "第二季度", "2季度"]):
                            should_download = True
                            print(f"    匹配: 半年度/半年报/第2季度/第二季度")
                    elif quarter == 3:
                        # 匹配三季度相关关键词：支持"三季度报告"、"三季报"、"第3季度"等格式
                        if any(keyword in title for keyword in ["三季度", "三季报", "第3季度", "第三季度", "3季度"]):
                            should_download = True
                            print(f"    匹配: 三季度/三季报/第3季度/第三季度")
                    elif quarter == 4:
                        # 匹配年报相关关键词
                        if any(keyword in title for keyword in ["年报", "年度报告"]):
                            should_download = True
                            print(f"    匹配: 年报/年度报告")

                if should_download:

                    adjunctUrl = item["adjunctUrl"]
                    print(f"    获取到的adjunctUrl: '{adjunctUrl}'")
                    pdfurl = "http://static.cninfo.com.cn/" + adjunctUrl
                    print(f"    构造的PDF URL: '{pdfurl}'")

                    # 获取PDF内容
                    pdf_response = session.get(pdfurl)
                    pdf_response.raise_for_status()

                    # 获取公司名称
                    company_name = company_dict.get(stock, stock)

                    # 保存到年报文件夹下，方便统一管理
                    company_folder = os.path.join("年报", f"{company_name}_{stock}")
                    os.makedirs(company_folder, exist_ok=True)

                    # 文件名格式：公司名称_股票代码_年份_季度报告
                    filename = f"{company_name}_{stock}_{year}{quarter_name}.pdf"
                    filepath = os.path.join(company_folder, filename)

                    with open(filepath, "wb") as f:
                        f.write(pdf_response.content)

                    print(f"  下载完成: {company_name}_{stock}_{year}{quarter_name} (已保存到年报文件夹)")
                    return True
        else:
            print(f"  未找到 {stock} 在 {year} 年的 {quarter_name}")

    except requests.exceptions.RequestException as e:
        print(f"  网络请求失败: {stock}_{year}{quarter_name} - {str(e)}")
    except json.JSONDecodeError as e:
        print(f"  JSON解析失败: {stock}_{year}{quarter_name} - {str(e)}")
    except Exception as e:
        print(f"  下载失败: {stock}_{year}{quarter_name} - {str(e)}")

    return False

def get_latest_quarterly_reports(stock, year, org_dict, company_dict):
    """下载最新年份的所有季报"""
    quarters = [
        ("category_yjdbg_szsh", "一季报"),
        ("category_bndbg_szsh", "半年报"),
        ("category_sjdbg_szsh", "三季报")
    ]

    downloaded = []
    for i, (category_code, quarter_name) in enumerate(quarters, 1):
        if download_quarterly_report(stock, year, i, org_dict, company_dict, category_code, quarter_name):
            downloaded.append(quarter_name)
        time.sleep(random.randint(1, 3))

    return downloaded

def get_orgid():
    """获取股票代码与 orgId、公司名称 - 适配新的披露页面格式"""
    org_dict = {}
    company_dict = {}

    # 使用深交所数据源
    szse_url = "http://www.cninfo.com.cn/new/data/szse_stock.json"

    try:
        # 获取深交所数据
        szse_resp = requests.get(szse_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        szse_resp.raise_for_status()
        szse_data = szse_resp.json().get("stockList", [])

        # 处理深交所数据
        for item in szse_data:
            stock_code = item.get("code", "")
            org_id = item.get("orgId", "")
            company_name = item.get("zwjc", "")

            if stock_code and org_id:
                org_dict[stock_code] = org_id
                company_dict[stock_code] = company_name

        print(f"成功获取 {len(org_dict)} 只股票的orgId信息")

    except requests.exceptions.RequestException as e:
        print(f"获取股票列表失败 - 网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"获取股票列表失败 - JSON解析错误: {str(e)}")
    except Exception as e:
        print(f"获取股票列表失败: {str(e)}")

    return org_dict, company_dict

def get_current_year():
    """获取当前年份"""
    return datetime.now().year

def main(year=None):
    """主函数 - 使用新的披露页面筛选逻辑

    Args:
        year (str, optional): 指定要下载的年份，默认为当前年份
    """
    print("=" * 60)
    print("开始下载指定年份季报 - 使用新披露页面筛选逻辑")
    print("=" * 60)

    # 创建年报目录（季报将与年报保存在同一文件夹下）
    os.makedirs("年报", exist_ok=True)

    # 获取指定年份或当前年份
    if year is None:
        current_year = str(get_current_year())
    else:
        current_year = str(year)
    print(f"目标年份: {current_year}")

    # 获取股票代码列表
    stock_list = []

    # 尝试读取Excel文件
    try:
        pdlist = pd.read_excel("stockcode.xlsx", converters={'stockcode': str})["stockcode"]
        stock_list = pdlist.to_numpy().tolist()
        print("成功从stockcode.xlsx读取股票代码")
    except FileNotFoundError:
        print("未找到stockcode.xlsx文件，尝试读取文本文件...")
        try:
            with open("stockcode.txt", "r", encoding="utf-8") as f:
                stock_list = [line.strip() for line in f if line.strip()]
            print(f"成功从stockcode.txt读取{len(stock_list)}个股票代码")
        except FileNotFoundError:
            print("未找到stockcode.txt文件，使用测试股票代码")
            stock_list = ["000001", "000002"]  # 默认测试代码
        except Exception as e:
            print(f"读取文本文件失败: {str(e)}")
            return
    except Exception as e:
        print(f"读取Excel文件失败: {str(e)}")
        return

    print(f"共 {len(stock_list)} 只股票需要处理")

    # 获取orgId和公司名称
    print("正在获取股票orgId信息...")
    org_dict, company_dict = get_orgid()

    if not org_dict:
        print("未能获取到股票orgId信息，程序终止")
        return

    # 统计下载结果
    success_count = 0
    total_reports = 0
    failed_stocks = []

    print("\n开始处理股票季报下载...")
    print("-" * 60)

    for i, stock in enumerate(stock_list, 1):
        print(f"\n[{i:3d}/{len(stock_list)}] 处理股票: {stock}")

        if stock in org_dict:
            org_id = org_dict[stock]
            company_name = company_dict.get(stock, stock)
            print(f"  公司名称: {company_name}")
            print(f"  OrgId: {org_id}")

            downloaded = get_latest_quarterly_reports(stock, str(current_year), org_dict, company_dict)
            if downloaded:
                success_count += 1
                total_reports += len(downloaded)
                print(f"  成功下载: {', '.join(downloaded)}")
            else:
                print(f"  未找到 {current_year} 年季报")
                failed_stocks.append(f"{stock} ({company_name})")
        else:
            print(f"  未找到股票 {stock} 的orgId信息")
            failed_stocks.append(f"{stock} (未知公司)")

        # 每处理完一只股票后暂停，避免请求过快
        if i < len(stock_list):
            sleep_time = random.randint(2, 5)
            print(f"  暂停 {sleep_time} 秒...")
            time.sleep(sleep_time)

    # 打印最终结果
    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print("统计结果:")
    print(f"   成功处理: {success_count}/{len(stock_list)} 只股票")
    print(f"   总共下载: {total_reports} 份季报")
    print(f"   文件保存: 年报/ 目录下 (季报与年报统一管理)")

    if failed_stocks:
        print(f"\n未成功下载的股票 ({len(failed_stocks)}只):")
        for failed in failed_stocks:
            print(f"   - {failed}")

    print("\n程序执行完毕！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="下载指定年份的季报")
    parser.add_argument("--year", "-y", type=str, help="指定要下载的年份，例如: 2023")
    args = parser.parse_args()

    main(year=2025)