import logging
import re
import time
from logging import handlers

import hydra
import pandas as pd
import pymysql
import swifter
from konlpy.tag import Mecab
from sqlalchemy import create_engine

from trie import Trie

# log setting
carLogFormatter = logging.Formatter("%(asctime)s,%(message)s")

carLogHandler = handlers.TimedRotatingFileHandler(
    filename="../log/labeling.log",
    when="midnight",
    interval=1,
    encoding="utf-8",
)
carLogHandler.setFormatter(carLogFormatter)
carLogHandler.suffix = "%Y%m%d"

scarp_logger = logging.getLogger()
scarp_logger.setLevel(logging.INFO)
scarp_logger.addHandler(carLogHandler)


def processing(content):
    result = re.sub(r"[a-zA-Z가-힣]+뉴스", "", str(content))
    result = re.sub(r"[a-zA-Z가-힣]+ 뉴스", "", result)
    result = re.sub(r"[a-zA-Z가-힣]+newskr", "", result)
    result = re.sub(r"[a-zA-Z가-힣]+Copyrights", "", result)
    result = re.sub(r"[a-zA-Z가-힣]+ Copyrights", "", result)
    result = re.sub(r"\s+Copyrights", "", result)
    result = re.sub(r"[a-zA-Z가-힣]+com", "", result)
    result = re.sub(r"[가-힣]+ 기자", "", result)
    result = re.sub(r"[가-힣]+기자", "", result)
    result = re.sub(r"[가-힣]+ 신문", "", result)
    result = re.sub(r"[가-힣]+신문", "", result)
    result = re.sub(r"데일리+[가-힣]", "", result)
    result = re.sub(r"[가-힣]+투데이", "", result)
    result = re.sub(r"[가-힣]+미디어", "", result)
    result = re.sub(r"[가-힣]+ 데일리", "", result)
    result = re.sub(r"[가-힣]+데일리", "", result)
    result = re.sub(r"[가-힣]+ 콘텐츠 무단", "", result)
    result = re.sub(r"전재\s+변형", "전재", result)
    result = re.sub(r"[가-힣]+ 전재", "", result)
    result = re.sub(r"[가-힣]+전재", "", result)
    result = re.sub(r"[가-힣]+배포금지", "", result)
    result = re.sub(r"[가-힣]+배포 금지", "", result)
    result = re.sub(r"\s+배포금지", "", result)
    result = re.sub(r"\s+배포 금지", "", result)
    result = re.sub(r"[a-zA-Z가-힣]+.kr", "", result)
    result = re.sub(r"/^[a-z0-9_+.-]+@([a-z0-9-]+\.)+[a-z0-9]{2,4}$/", "", result)
    result = re.sub(r"[\r|\n]", "", result)
    result = re.sub(r"\[[^)]*\]", "", result)
    result = re.sub(r"\([^)]*\)", "", result)
    result = re.sub(r"[^ ㄱ-ㅣ가-힣A-Za-z0-9.]", "", result)
    result = (
        result.replace("뉴스코리아", "")
        .replace("및", "")
        .replace("Copyright", "")
        .replace("저작권자", "")
        .replace("ZDNET A RED VENTURES COMPANY", "")
    )
    result = result.strip()

    return result


def data_load(**kwargs):
    try:
        logging.info("dataload start")
        pymysql.install_as_MySQLdb()

        engine_conn = "mysql://%s:%s@%s/%s" % (
            kwargs.get("user"),
            kwargs.get("passwd"),
            kwargs.get("host"),
            kwargs.get("db"),
        )
        engine = create_engine(engine_conn)

        data = pd.read_sql(
            "select id, content from table where sentiment is null limit 10000;",
            engine,
        )
        data["content"] = data.content.apply(processing)
        df = data.drop_duplicates()

        logging.info("dataload end")

        return df

    except Exception as e:
        logging.info(e)


# mecab
m = Mecab("/usr/local/lib/mecab/dic/mecab-ko-dic")


# trie skill on sentiment dictionary
def sentiment_dict():
    # http://dilab.kunsan.ac.kr/knusl.html
    # KNU 한국어 감성사전
    with open("/dict/pos_tag_dict.txt", "r") as f:
        pos_tag_dict = []
        for readline in f:
            line_strip = readline.strip()
            pos_tag_dict.append(str(line_strip))

    with open("/dict/neg_tag_dict.txt", "r") as f:
        neg_tag_dict = []
        for readline in f:
            line_strip = readline.strip()
            neg_tag_dict.append(str(line_strip))

    global pos_trie, neg_trie

    pos_trie = Trie()
    for word in pos_tag_dict:
        pos_trie.insert(word)

    neg_trie = Trie()
    for word in neg_tag_dict:
        neg_trie.insert(word)


# positive, negative rate
def pos_rate(content):
    sentence = content.split(".")
    tag_list = [m.pos(v) for v in sentence]

    value_list = []
    for tag in tag_list:
        value_list.append(
            [
                i[0] + "/" + i[1]
                for i in tag
                if i[1]
                not in [
                    "VCP",
                    "VCN",
                    "MM",
                    "MAJ",
                    "IC",
                    "JK",
                    "JX",
                    "JC",
                    "JKS",
                    "JKC",
                    "JKG",
                    "JKO",
                    "JKB",
                    "JKV",
                    "JKQ",
                ]
            ]
        )

    # dict check
    pos = []
    for value in value_list:
        search_word = []
        for i in value:
            search_word.append(i)
            search = " ".join(search_word)
            temp = pos_trie.search(search)
            if temp:
                if pos_trie.search(search):
                    pos.append(search)
            else:
                search_word = []

    # rate
    rate = 0
    tot_count = len(sum(tag_list, []))
    if tot_count != rate:
        rate = len(pos) / tot_count

    return rate


def neg_rate(content):
    sentence = content.split(".")
    tag_list = [m.pos(v) for v in sentence]

    value_list = []
    for tag in tag_list:
        value_list.append(
            [
                i[0] + "/" + i[1]
                for i in tag
                if i[1]
                not in [
                    "VCP",
                    "VCN",
                    "MM",
                    "MAJ",
                    "IC",
                    "JK",
                    "JX",
                    "JC",
                    "JKS",
                    "JKC",
                    "JKG",
                    "JKO",
                    "JKB",
                    "JKV",
                    "JKQ",
                ]
            ]
        )

    # dict check
    pos = []
    for value in value_list:
        search_word = []
        for i in value:
            search_word.append(i)
            search = " ".join(search_word)
            temp = neg_trie.search(search)
            if temp:
                if neg_trie.search(search):
                    pos.append(search)
            else:
                search_word = []

    # rate
    rate = 0
    tot_count = len(sum(tag_list, []))
    if tot_count != rate:
        rate = len(pos) / tot_count

    return rate


def update(query, param, **kwargs):
    conn = pymysql.connect(
        user=kwargs.get("user"),
        passwd=kwargs.get("passwd"),
        db=kwargs.get("db"),
        host=kwargs.get("host"),
        port=kwargs.get("port"),
        charset="utf8",
        use_unicode=True,
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.executemany(query, param)
    conn.commit()
    logging.info("update end")


@hydra.main(config_name="config.yml")
def main(cfg):
    try:
        # start time
        start = time.time()

        # dataload
        df = data_load(**cfg.DATABASE)

        # sentiment dict
        sentiment_dict()

        # sentiment classification
        df["pos_rate"] = df.content.swifter.apply(pos_rate)
        df["neg_rate"] = df.content.swifter.apply(neg_rate)

        # labeling
        label_not_dup_list = []

        for i in range(len(df)):
            if df.pos_rate[i] > df.neg_rate[i]:
                label = "긍정"
            elif df.pos_rate[i] < df.neg_rate[i]:
                label = "부정"
            else:
                label = "중립"
            label_not_dup_list.append(label)
        df.insert(4, "sentiment", label_not_dup_list)

        logging.info(df.head())

        # dataframe to update query
        query = "update table set sentiment=%s where id=%s;"
        param = []
        for i in range(len(df)):
            temp = (df["sentiment"][i], df["id"][i])
            param.append(temp)

        update(query, param, **cfg.DATABASE)

        # end time
        logging.info("time :" + str(time.time() - start))

    except Exception as e:
        logging.info(e)
        return 200


if __name__ == "__main__":
    main()
