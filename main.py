# 抓取人力銀行職缺, 分析個別工作技能清單
import bank_104
import bank_1111
import time
from urllib import request
import pandas as pd
import re
import jieba
from jieba import analyse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import imageio
import matplotlib.pyplot as plt
from collections import Counter

# The File size(>4.25MB) exceeds configured limit (2.56MB), code insight features not available
# 日誌文件過大,超過默認設定,要增加限制容量並重啟pycharm ->Help->Edit Custom Properties->加入"idea.max.intellisense.filesize=99999"
# 目標一：依照產業別列出該產業所需要的技能總表、最主要需求的技能列表 -> ok
# 目標二：各地區的1年以下工作經驗的職缺 -> ok
# 目標三：非碩博士的職缺所需要的工作技能 -> ok
# 目標四：無科系限制的職缺所需要的工作技能 -> ok
# 目標六：薪水4萬以下或不拘,所需要的工作技能 -> ok
# 目標七：嘗試結合資料視覺化 -> 文字雲 ok
# 目標五：可能需要串接資料庫,用sql語法更彈性的篩選出需要的資料 -> X


# 爬取人力銀行(1111、104)職缺資料,儲存成csv、excel及json資料
# 抓取104人力銀行職缺(工作經歷1年以下):
def find_vacancy(bank):
    start_time = time.time()
    if bank == "104":
        vac_qty = bank_104.vacancy_104()
    elif bank == "1111":
        vac_qty = bank_1111.vacancy_1111()
    end_time = time.time()
    print("Download ", vac_qty, "vacancies of", bank, ". It takes", round((end_time - start_time)/60, 2), 'minutes.')


# 計算詞頻
def count_seg_freq(seg_list):
    seg_df = pd.DataFrame(seg_list, columns=['Terminology'])
    seg_df['count'] = 1
    sef_freq = seg_df.groupby('Terminology')['count'].sum().sort_values(ascending=False)
    sef_freq = pd.DataFrame(sef_freq)
    return sef_freq


# 分析關鍵字
def analyse_kw(mode=0, *mode_item):
    # mode_dic = {0: '菜鳥', 1: '產業別', 2: '學士以下', 3: '不限科系', 4: '薪水4萬以下或面議', 5: '縣市別'}
    url = "https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.big"
    request.urlretrieve(url, "dict.big")
    jieba.set_dictionary("dict.big")
    jieba.load_userdict("venv/Dict/mix_terminologies.txt")

    total_vac = 0
    eng_kw = []
    bank_ls = ["1111", "104"]
    # 不同的人力銀行分別分析
    for bank in bank_ls:
        fn = bank + "/vacancy_python.json"
        kws = set()
        skill_all = []
        count = 1
        with open(fn, "r", encoding="utf-8") as f:
            # 完整顯示所有資料列
            pd.set_option('display.max_rows', None)
            vacancy = pd.read_json(f)
            df = pd.DataFrame(vacancy)

        if mode == 1:
            if mode_item:
                mode_item = str(mode_item[0])
                mask1 = df["industry"].str.contains(mode_item)
                mask2 = df["industry"].notnull()
                df = df[(mask1 & mask2)]
            else:
                mask1 = df["industry"].notnull()
                df = df[mask1]
        elif mode == 2:
            mask1 = df["edu_require"].str.contains("不拘|高中|專科|大學")
            mask2 = df["edu_require"].isnull()
            df = df[(mask1 | mask2)]
        elif mode == 3:
            mask1 = df["dept_require"].str.contains("不拘|商業|其他|一般|普通|軟體|網路")
            mask2 = df["dept_require"].isna()
            if bank == "104":
                mask2 = df["dept_require"].str.len() == 0
                df = df[mask2]
            else:
                df = df[(mask1 | mask2)]
        elif mode == 4:
            mask1 = df["salary"].str.contains("^月薪[23].,.*")
            mask2 = df["salary"].str.contains("面議")
            # mask2 = df["salary"].str.contains("年薪[4]??,*")
            df = df[(mask1 | mask2)]
        elif mode == 5:
            if mode_item:
                mode_item = str(mode_item[0])
                mask1 = df["com_area"].str.contains(mode_item)
            else:
                mask1 = df["com_area"].str.contains("台北市")
            df = df[mask1]
        print(bank+":", df.shape)
        print("_"*100)

        if bank == '1111':
            df.set_index("exp_require", inplace=True)
            if mode == 0:
                # 嘗試篩選出工作經驗2年以下及不拘的職缺
                df = df.loc[["工作經歷-不拘", "1年以上工作經驗"]]

            total_vac += len(df.index)
            for skill in df['skills']:
                # 目前先過濾掉語言能力的要求(匹配忽略大小寫)
                values = [val for k, val in skill.items() if k != '語言能力']  # and not re.match(r'[a-z]+', val, re.I)]
                if not skill or not values:  # 略過空資料
                    continue
                skill_all += values
        elif bank == '104':
            total_vac += len(df.index)
            for sk in df['skills']:
                if sk:
                    skill_all += sk

        for val in skill_all:
            val = val.strip().strip("..").strip("...").upper()
            val = val.replace("FAMILIAR", "").replace("COMPUTER", "").replace("SYSTEM", "").replace("WEB", "").replace("EXPERIENCE", "")
            val = val.replace("ABILITY", "").replace("JOB", "").replace("KNOWLEDGE", "").replace("SUCH", "").replace("TOOLS", "").replace("SIMILAR", "")
            val = val.replace("MS SQL", "MSSQL")
            jieba.analyse.set_stop_words('venv/Dict/stopwords.txt')
            jieba.add_word("MACHINE LEARNING")
            jieba.add_word("DEEP LEARNING")
            jieba.add_word("NODE.JS")
            jieba.suggest_freq("NODE.JS", True)
            if bank == '1111':
                val = re.sub(r"[Website]*?\(?[http?]\S+[/)$|/$]", "", val, flags=re.IGNORECASE)  # 刪除連結URL
                keywords = jieba.analyse.extract_tags(val, topK=30)
                # print("\n關鍵詞:", count,  keywords)
                for kw in keywords:
                    if re.match(r'[A-Z]+', kw):
                        eng_kw.append(kw)
                    kws.add(kw)
            elif bank == '104':
                if re.match(r'[A-Z]+', val):
                    eng_kw.append(val)

            count = count + 1

    word_freq = count_seg_freq(eng_kw)
    freq_percent = round(word_freq[:200]/len(eng_kw)*100, 1)
    freq_percent = freq_percent.rename(columns={"count": "%"})
    word_freq = pd.concat([word_freq, freq_percent], sort=False, axis=1)
    word_freq = word_freq.reset_index()
    print(word_freq[:200])
    print("Total terms:", len(word_freq))
    print("Filtered Vacancy:", total_vac)
    return eng_kw


# 產生文字雲
def word_cloud(mode=0, *mode_item):
    eng_kw = analyse_kw(mode, *mode_item)
    font_path = './venv/font/PatuaOne.ttf'
    show_words = 200

    # Default mode's image
    back_path = './venv/Image/github.jpg'
    fn_type = "fresh_0_"
    if mode == 1:
        back_path = './venv/Image/github2.jpeg'
        fn_type = "indus_1_"
        show_words = 150
        if mode_item:
            fn_type += mode_item[0] + "_"
            show_words = 100
    elif mode == 2:
        back_path = './venv/Image/explosion.png'
        fn_type = "edu_2_"
        show_words = 150
    elif mode == 3:
        back_path = './venv/Image/riot.jpg'
        fn_type = "dept_3_"
        show_words = 100
    elif mode == 4:
        back_path = './venv/Image/python.jpg'
        fn_type = "pay_4_"
        show_words = 100
    elif mode == 5:
        back_path = './venv/Image/umu.jpeg'
        fn_type = "area_5_"
        show_words = 150
        if mode_item:
            fn_type += mode_item[0] + "_"
            show_words = 100

    fn = fn_type + back_path.split("/")[-1].split(".")[0]+".png"
    back_color = imageio.imread(back_path)
    if not eng_kw:
        eng_kw.append('EMPTY RESULT.查無職缺')
    wc = WordCloud(
        max_words=show_words,
        mask=back_color,
        font_path=font_path,
        repeat=False,
        collocations=False
    ).generate_from_frequencies(Counter(eng_kw))
    if mode in [2, 3, 4, 5]:
        image_colors = ImageColorGenerator(back_color)
        wc.recolor(color_func=image_colors)

    if mode in [1, 5]:
        plt.rcParams['font.sans-serif'] = 'STHeiti'
    plt.legend(loc=1, title=fn[:-4], labels=fn_type.split("_")[0])
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    fig_path = "/Users/jiangdongzhe/Desktop/Lab1_skills/" + fn
    wc.to_file(fig_path)  # 輸出圖片


if __name__ == '__main__':
    # 1530筆 約 20分, 2310筆 約26分
    # find_vacancy("104")
    # 893筆 約 15.6分, 908筆 約13分
    # find_vacancy("1111")

    # mode_dic = {0: '菜鳥', 1: '產業別', 2: '學士以下', 3: '不限科系', 4: '薪水4萬以下或面議', 5: '縣市別'}
    # print(analyse_kw(2))
    # word_cloud()
    # word_cloud(1)  # => 全部產業的職缺, terms統計前150項
    # word_cloud(1, "金融")  # => 產業別有“金融” 的職缺, terms統計前100項
    # word_cloud(1, "光電|電子")  # => 產業別有“光電”或“電子” 的職缺, terms統計前100項
    # word_cloud(2)
    # word_cloud(3)
    # word_cloud(4)
    # word_cloud(5)
    word_cloud(5, "台中")
    # word_cloud(5, "澎湖")

