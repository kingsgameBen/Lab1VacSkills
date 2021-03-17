from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import pandas as pd


# 從wikipedia取得程式語言清單關鍵字
def programming_lang():
    url = "https://zh.wikipedia.org/wiki/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80%E5%88%97%E8%A1%A8"
    response = urlopen(url)
    html = BeautifulSoup(response, features="html.parser")
    main_content = html.find('div', id='bodyContent').find('div', id='mw-content-text').find_all('div', class_='div-col')
    a_ls = [tag.find_all('a') for tag in main_content]
    programming_list = []
    for anchors in a_ls:
        for lang in anchors:
            programming_list.append(lang.text)
    if not os.path.exists('Dict'):
        os.makedirs('Dict')
    with open('Dict/programming.dict', 'w', encoding='utf-8')as f:
        for text in programming_list:
            f.write(text+'\n')


# 因為字詞來源於中國網站, 簡體字轉換成繁體字的操作, 暫時以手動方式轉換
def operating_sys():
    url = "https://zh.wikipedia.org/wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%97%E8%A1%A8"
    response = urlopen(url)
    html = BeautifulSoup(response, features="html.parser")
    main_content = html.find('div', id='bodyContent').find('div', id='mw-content-text').find_all('ul')
    a_ls = [li.find_all('a') for li in main_content]  # if not li.find('span')]  #不排除系統分類標題名稱
    os_ls = []
    for a in a_ls:
        for system in a:
            os_ls.append(system.text)
    if not os.path.exists('Dict'):
        os.makedirs('Dict')
    with open('Dict/operating_sys.dict', 'w', encoding='utf-8')as f:
        for text in os_ls:
            f.write(text + '\n')


# 把字典內容去掉重複並全部轉成大寫
def convert2upperset(file_name):
    file_name = 'Dict/' + file_name + '.dict'
    temp_ls = []
    with open(file_name, 'r', encoding='utf-8')as f:
        temp_ls = f.readlines()
    upper_ls = set()
    for temp in temp_ls:
        upper_ls.add(temp.upper())
    with open(file_name, 'w', encoding='utf-8')as f:
        f.writelines(upper_ls)


# 產業別列表
def industry_list():
    industry_set = set()
    for bank in ["1111", "104"]:
        file_name = "../" + bank + "/vacancy_python.json"
        with open(file_name, 'r', encoding='utf-8')as f:
            vacancy = pd.read_json(f)
        for indus in vacancy['industry']:
            industry_set.add(indus)
        print(bank, ":\n", industry_set, "\n AccumulatedQty:", len(industry_set))
    if not os.path.exists("Dict"):
        os.makedirs("Dict")
    with open("Dict/industry_list.txt", 'w', encoding='utf-8')as f:
        for ind in industry_set:
            if ind:  # 避免寫入None
                f.write(ind+'\n')
    print(len(industry_set))


# 學歷要求列表
def industry_list():
    edu_set = set()
    for bank in ["1111", "104"]:
        file_name = "../" + bank + "/vacancy_python.json"
        with open(file_name, 'r', encoding='utf-8')as f:
            vacancy = pd.read_json(f)
        for indus in vacancy['edu_require']:
            edu_set.add(indus)
        print(bank, ":\n", edu_set, "\n AccumulatedQty:", len(edu_set))
    if not os.path.exists("Dict"):
        os.makedirs("Dict")
    edu_ls = sorted(edu_set)
    with open("Dict/education_list.txt", 'w', encoding='utf-8')as f:
        for edu in edu_ls:
            if edu:  # 避免寫入None
                f.write(edu+'\n')
    print(len(edu_ls))


# 科系要求列表
def dept_list():
    dept_set = set()
    for bank in ["1111", "104"]:
        file_name = "../" + bank + "/vacancy_python.json"
        with open(file_name, 'r', encoding='utf-8')as f:
            vacancy = pd.read_json(f)
        for dept in vacancy['dept_require']:
            for d in dept:
                dept_set.add(d)
        print(bank, ":\n", dept_set, "\n AccumulatedQty:", len(dept_set))
    if not os.path.exists("Dict"):
        os.makedirs("Dict")
    dept_ls = sorted(dept_set)
    with open("Dict/department_list.txt", 'w', encoding='utf-8')as f:
        for dept in dept_ls:
            f.write(dept+'\n')
    print(len(dept_ls))


# 所有技能列表(from人力銀行的技能條件)
def skills_list():
    skills_set = set()
    for bank in ["1111", "104"]:
        file_name = "../" + bank + "/vacancy_python.json"
        with open(file_name, 'r', encoding='utf-8')as f:
            vacancy = pd.read_json(f)
        for skills in vacancy['skills']:
            for skill in skills:
                skills_set.add(skill.strip().upper())
        print(bank, ":\n", skills_set, "\n AccumulatedQty:", len(skills_set))

    if not os.path.exists("Dict"):
        os.makedirs("Dict")
    skills_ls = sorted(skills_set)
    with open("Dict/terminology_list.txt", 'w', encoding='utf-8')as f:
        for skill in skills_ls:
            if skill:  # 避免寫入None
                f.write(skill+'\n')
    print(len(skills_ls))


# 整合成一份所有技能列表(programming.dict、operating_sys.dict、terminology_list.txt => mix_terminologies.txt)
def integrated_term_list():
    terms_set = set()
    for dic in ["operating_sys.dict", "programming.dict", "terminology_list.txt"]:
        file_name = "Dict/" + dic
        with open(file_name, 'r', encoding='utf-8')as f:
            terms_ls = f.readlines()
        for term in terms_ls:
            terms_set.add(term.strip("\n").upper())
        print(dic, ":\n", terms_set, "\n AccumulatedQty:", len(terms_set))

    terms_ls = sorted(terms_set)
    with open("Dict/mix_terminologies.txt", 'w', encoding='utf-8')as f:
        for term in terms_ls:
            if term:  # 避免寫入None
                f.write(term+'\n')
    print(len(terms_ls))


# 薪資待遇列表
def sal_list():
    sal_set = set()
    for bank in ["1111", "104"]:
        file_name = "../" + bank + "/vacancy_python.json"
        with open(file_name, 'r', encoding='utf-8')as f:
            vacancy = pd.read_json(f)
        for indus in vacancy['salary']:
            sal_set.add(indus)
        print(bank, ":\n", sal_set, "\n AccumulatedQty:", len(sal_set))
    sal_ls = sorted(sal_set)
    with open("Dict/salary_list.txt", 'w', encoding='utf-8')as f:
        for sal in sal_ls:
            if sal:  # 避免寫入None
                f.write(sal+'\n')
    print(len(sal_ls))

