# 👉🏻 감성 빈도 분석

<br>
<br>

# 👉🏻 description
군산대학교 한국어 감성사전을 활용하여 mecab pos tagging 사전 구축
https://github.com/park1200656/KnuSentiLex

trie tree 구조를 활용하여 긍부정 빈도 labeling 작업

<br>
<br>

## **docker container(sentiment)**
### **- how to use**
<br>
sudo docker build --tag sentiment .
<br>
sudo docker run -d -it --cpus=1 --restart always --name sentiment sentiment

<br>
<br>

# 👉🏻 crontab
    
    ## every 3:00 am
        sentiment_analysis.py
        
## 👉🏻 tree
 * [tree-md]
 * [data]
   * [neg_dict.txt]
   * [neg_tag_dict.txt]
   * [pos_dict.txt]
   * [pos_tag_dict.txt]
 * [cron.txt]
 * [Dockerfile]
 * [README.md]
 * [requirements.txt]
 * [run_batch.sh]
 * [sentiment_analysis.py]
 * [sentiment_dict_pos_tagging.ipynb]
 * [trie.py]