# ππ» κ°μ± λΉλ λΆμ

<br>
<br>

# ππ» description
κ΅°μ°λνκ΅ νκ΅­μ΄ κ°μ±μ¬μ μ νμ©νμ¬ mecab pos tagging μ¬μ  κ΅¬μΆ
https://github.com/park1200656/KnuSentiLex

trie tree κ΅¬μ‘°λ₯Ό νμ©νμ¬ κΈλΆμ  λΉλ labeling μμ

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

# ππ» crontab
    
    ## every 3:00 am
        sentiment_analysis.py
        
## ππ» tree
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