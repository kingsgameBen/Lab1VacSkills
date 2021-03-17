# 104銀行 python相關職缺
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
import time
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

table = {
        "job_name": [],
        "job_href": [],
        "update_date": [],
        "company": [],
        "com_area": [],
        "industry": [],
        "exp_require": [],
        "edu_require": [],
        "skills": [],
        "dept_require": [],
        "salary": [],
        "job_content": [],
        "job_type": [],
        "benefit_tags": [],
        "benefit_desc": []
    }
DIR = "./104"


def vacancy_104():
    # 計數職缺分頁數、職缺項目數
    pagination = 1
    count = 1
    while True:
        # 只取得工作經歷<1年的python職缺
        url_1year = "https://www.104.com.tw/jobs/search/?keyword=python&page=" + str(pagination) + "&jobexp=1"
        response = requests.get(url_1year).text
        html = BeautifulSoup(response, features="html.parser")

        # 取出第2個沒有src屬性的script標籤,其內容中有totalPage的總頁數資料,
        # 目前無法透過.text或.contents取得totalPage, 改成用while True + 該page取不到ResultSet來終止迴圈
        rs = html.find("div", id="main-content").find("div", id="js-job-content").select("article.job-list-item")
        # 以還能不能取得職缺項目, 判斷是否停止搜尋, 停止while迴圈前儲存所有資料
        if not rs:
            file_name = "vacancy_python"
            csv_fn = DIR+"/"+file_name+".csv"
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            df = pd.DataFrame(table)
            df.to_csv(csv_fn, encoding="utf-8", index=False)
            # 儲存JSON資料(一個JSON檔儲存全部職缺)
            json_fn = DIR+"/"+file_name+".json"
            with open(json_fn, "w", encoding="utf-8") as f:
                json.dump(table, f, ensure_ascii=False, indent=4)
            print("="*30, "Procedure End", "="*30)

            excel_fn = DIR+"/"+file_name+".xlsx"
            df.to_excel(excel_fn)
            count = count - 1
            return count

        # start_time = time.time()
        # 建立網址清單,使用grequests的imap()平行發送多個請求
        # href_ls = ["https:" + r.find("a")['href'].strip() for r in rs]
        # reqs = [grequests.get(href) for href in href_ls]
        # responses = grequests.imap(reqs, grequests.Pool(len(reqs)))
        for r in rs:
            # 直接取得父元素下第一個取得的<a>, 職缺連結:-> str
            job_href = "https:" + r.find("a")['href'].strip()
            response = requests.get(job_href).text
            html = BeautifulSoup(response, features="html.parser")
            # print(html)
            titles = html.find("title").text.split("｜")
            # 職缺名稱
            job_name = titles[0].strip()
            # 公司名稱
            company = titles[1].strip()
            # 公司地區
            com_area = titles[2].split("－")[0]
            # 網頁原始碼只有部分資料, 完整資料是透過json帶進來的,做法有別於1111, 須以JSON方式操作
            # 以？分割並透過取段操作取得顯示網址列的職缺ID - 長度4~5碼英數字, 放入職缺內容的JSON真實網址
            json_id = job_href.split("?")[0].split("/")[-1]
            json_url = "https://www.104.com.tw/job/ajax/content/" + json_id
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
                'Referer': 'https://www.104.com.tw/job/' + json_id + '?jobsource=jolist_a_relevance'
            }

            response = requests.get(json_url, headers=headers)
            json_data = json.loads(response.text)["data"]
            # 更新日期、產業別、學歷條件、工作經驗、薪資、工作內容、職務類別、科系條件、工作技能、福利制度
            update_date = json_data["header"]["appearDate"]
            industry = json_data["industry"]
            edu_require = json_data["condition"]["edu"]
            exp_require = json_data["condition"]["workExp"]
            salary = json_data["jobDetail"]["salary"]
            job_content = json_data["jobDetail"]["jobDescription"].strip()
            job_type = [cate["description"] for cate in json_data["jobDetail"]["jobCategory"]]
            dept_require = json_data["condition"]["major"]
            skills = [special["description"] for special in json_data["condition"]["specialty"]]
            benefit_desc = json_data["welfare"]["welfare"]

            table['job_name'].append(job_name)
            table['job_href'].append(job_href)
            table['update_date'].append(update_date)
            table['company'].append(company)
            table['industry'].append(industry)
            table['com_area'].append(com_area)
            table['edu_require'].append(edu_require)
            table['exp_require'].append(exp_require)
            table['salary'].append(salary)
            table['job_content'].append(job_content)
            table['job_type'].append(job_type)
            table['dept_require'].append(dept_require)
            table['skills'].append(skills)
            table['benefit_tags'].append(None)
            table['benefit_desc'].append(benefit_desc)

            print()
            print('Page:', pagination)
            print(count, job_href)
            print(job_name)
            print(update_date)
            print('公司,產業別：', company, industry)
            # print('地點：', com_area)
            # print(edu_require)
            # print(exp_require)
            # print(salary)
            # print(job_content)
            # print(job_type)
            # print(dept_require)
            # print(skills)
            # print(benefit_desc)
            print('-' * 100)
            count = count + 1

        pagination = pagination + 1

