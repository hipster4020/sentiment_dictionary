FROM ubuntu:20.04

# 파일 복사
RUN mkdir src
RUN mkdir dict
RUN mkdir log

COPY run_batch.sh run_batch.sh
COPY requirements.txt requirements.txt

# python file
COPY sentiment_analysis.py /src/sentiment_analysis.py
COPY trie.py /src/trie.py

# dictionary
COPY data/origin_dict/neg_tag_dict.txt /dict/neg_tag_dict.txt
COPY data/origin_dict/pos_tag_dict.txt /dict/pos_tag_dict.txt

# config
COPY config.yml /src/config.yml

ENV DEBIAN_FRONTEND noninteractive

# 설치 실행
RUN apt-get update && apt-get install -y gcc wget cron gnupg vim procps python3.8 python3-pip tzdata rsyslog
RUN pip3 install -r requirements.txt

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

COPY cron.txt /etc/cron.d/scrap.cron
RUN chmod 777 /etc/cron.d/scrap.cron
RUN crontab /etc/cron.d/scrap.cron
RUN service cron start