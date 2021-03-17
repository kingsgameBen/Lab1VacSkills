# 1111人力銀行
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
# MAC + Pycharm: SSL Certification failed 驗證機制較嚴苛 須證書代碼
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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
# .csv資料夾名稱
DIR = "./1111"


def vacancy_1111():
    # 計數職缺分頁數、職缺項目數
    pagination = 1
    count = 1

    # 搜尋結果第一頁(20筆),放在while loop 外以避免重複比對執行
    url = "https://www.1111.com.tw/search/job?ks=python"
    response = requests.get(url).text
    html = BeautifulSoup(response, features="html.parser")
    # 取得最後一頁, 3/12網站更改class naming
    # final_page = html.select('div.adv-footer > div.container > div.adv-footer__content > div.adv-footer__content-item > select > option:nth-last-of-type(1)')[0]['value']
    final_page = html.find("div", class_="srh-footer").select(
        'div.container > div.srh-footer__content > div.srh-footer__content-item > select > option')[-1]['value']
    final_page = int(final_page)
    while True:
        if pagination != 1:
            url = "https://www.1111.com.tw/search/job?ks=python&fs=1&page=" + str(pagination) + "&act=load_page"
            response = requests.get(url).text
            response = json.loads(response)['html']
            html = BeautifulSoup(response, features="html.parser")
        print(pagination, '/', final_page)

        rs = html.find_all("div", class_="item__job-info")
        for r in rs:
            # 職缺連結:-> str
            job_href = r.find("a")['href'].strip()
            response = requests.get(job_href).text
            html = BeautifulSoup(response, features="html.parser")
            # 職缺名稱:-> str
            job_name = html.find('div', class_="vacancy-header-row").find('h1').text.strip()
            # 更新日: -> str
            update_date = html.find('div', class_="vacancy-header-row").find('p', class_='update').text.split("：")[-1]
            # 公司名稱:-> str
            company = html.find('div', class_="vacancy-company-text").find('h2').find('a').text.strip()
            # 公司產業別: -> str
            if html.find('div', class_="vacancy-company-text").find('div', class_="company-category"):
                industry = html.find('div', class_="vacancy-company-text").find('div', class_="company-category").find('a').text.strip()
            else:
                # 若顯示頁面找不到產業類別,則從原始碼的特定script標籤中取出
                desc = json.loads(html.find_all("script", {"type": "application/ld+json"})[1].contents[0])[0]
                industry = desc['industry']
            main_contents = html.find('div', class_="vacancy-header-row").find('ul', class_="vacancy-description-main").find_all('p')

            # 取出職缺主要項目( 薪資、 工作經驗、 學歷、 公司地區 ):-> str
            salary, exp_require, edu_require, com_area = "", "", "", ""
            # 用包含式逐項取出職缺主要項目內容依序放入清單的變數中
            [salary, exp_require, edu_require, com_area] = [spans.select('span:nth-of-type(2)')[0].text.strip() for spans in main_contents]

            # 先找到職缺詳細內容的大區塊作為基準點,在依此尋找各項資料
            all_info = html.find('section', id="Job-Detail").find('div', class_="container").find('div', class_="row").find('div', id="job-detail-info")
            # 工作內容
            detail_block = all_info.find('div', class_="job-detail-info").find('div', class_="job-detail-info-content").find_all("p")
            # 用包含式將工作內容區塊的所有 段落標籤 移除: -> list
            job_content = [con.text.strip() for con in detail_block]
            # 工作制度/性質
            type_block = all_info.select(".job-detail-panel > .job-detail-panel-content")[0]
            # 用包裹式取出 職務類別 的清單:-> list
            job_type = [a['title'] for a in type_block.select("dl > dd > span.category > a")]
            # 要求條件
            # 條件標題:-> list
            require_titles = all_info.select(".job-detail-panel > .job-detail-panel-content")[2].find('dl').find_all('dt')
            # print([t.text.strip(':') for t in require_titles])
            require_block = all_info.select(".job-detail-panel > .job-detail-panel-content")[2].find('dl')
            # 科系限制:->str(不拘) or list
            departments = require_block.select('dd > span')[3]
            # 若有科系要求則以 list 存入,不拘 則直接以 str 儲存
            if departments.find_all('a'):
                dept_require = [dept['title'] for dept in departments.find_all('a')]
            else:
                dept_require = departments.text.strip()
            # 其他要求條件(0~多項條件):-> dict
            skills = {}
            if len(require_titles) > 4:
                # 去除 latin1的不間斷空格、\r\n換行、\t縮排、縮減大量空格
                extra_requires = [dd.text.replace('\xa0', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('     ', '').strip() for dd in require_block.select('dt + dd')[4:]]
                for i in require_titles[4:]:
                    idx = i.text.strip('：')
                    skills[idx] = extra_requires[require_titles.index(i)-4]
            # 福利制度
            benefit_tags, benefit_desc = "", ""
            if all_info.find('div', id='service-button-point'):
                benefit_block = all_info.find('div', id='service-button-point').find('div', class_='job-detail-panel-content')
                # 福利制度的標籤(不抓取法定項目的福利):-> list
                if benefit_block.select('a'):
                    benefit_tags = [item['title'] for item in benefit_block.select('a') if item['title'] != 'legal']
                # 其他福利制度的說明:->str
                if benefit_block.select('div.list-box-full > p'):
                    benefit_desc = benefit_block.select('div.list-box-full > p')[0].text.strip()

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
            table['benefit_tags'].append(benefit_tags)
            table['benefit_desc'].append(benefit_desc)

            print()
            print(count, '職缺：', job_href)
            print('工作：', job_name)
            print('更新日', update_date)
            print('公司,產業別：', company, industry)
            # print('地點：', com_area)
            # print(edu_require)
            # print(exp_require)
            # print(salary)
            # print(job_content)
            # print(job_type)
            # print(dept_require)
            # print(skills)
            # print(benefit_tags)
            # print(benefit_desc)
            print('--'*100)
            count = count + 1

        pagination = pagination + 1
        # 判斷是否超過最終頁, 若超過則跳出for loop 及 while loop
        if pagination > final_page:
            file_name = "vacancy_python"
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            df = pd.DataFrame(table)
            csv_fn = DIR+"/"+file_name+".csv"
            df.to_csv(csv_fn, encoding="utf-8", index=False)
            # 儲存JSON資料(一個JSON檔儲存全部職缺)
            json_fn = DIR + "/" + file_name + ".json"
            with open(json_fn, "w", encoding="utf-8") as f:
                json.dump(table, f, ensure_ascii=False, indent=4)
            print("="*30, "Procedure End", "="*30)

            excel_fn = DIR+"/"+file_name+".xlsx"
            df.to_excel(excel_fn)
            count = count - 1
            return count


