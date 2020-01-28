# (setq python-shell-interpreter "./venv/bin/python")

import requests, pandas as pd
from bs4 import BeautifulSoup as bs
from random import sample

def get_categories():
    r = requests.get("http://www.darulifta-deoband.com/home")
    soup = bs(r.text, "html.parser")

    cats = []
    for link in soup.find("ul", class_="sub-menu").find_all("a"):
        n = int(link.find_next("span").text.split('(')[1].split(")")[0])
        cats.append((link.get("href"), n))
    
    return cats


def make_categories_list(cats):
    '''makes a list of tuples with (link, qnumber) where qnumer is the nth
    question on that page'''
    questions = []
    for link, n in cats:
        for i in range(int(n)):
            questions.append(((link), i))
    return questions

def get_question(q):
    link, n = q
    page, pos = divmod(n, 20)
    page_link = link + "/?page=" + str(page + 1)

    print(page_link)
    r = requests.get(page_link)
    soup = bs(r.text, "html.parser")

    try:
        question_link = soup.select_one("div.qaanslist>ul").find_all("a")[pos].get("href")
    except:
        question_link = soup.select_one("div.qaanslist>ul").find_all("a")[0].get("href")

    print(question_link)
    r = requests.get(question_link)
    soup = bs(r.text, "html.parser")

    parts = soup.find_all("div", class_="lngqs")

    question = parts[0].text.replace("\xa0", " ")
    answer = parts[1].text.replace("\xa0", " ")

    
    return pd.DataFrame([[question_link, question, answer]], columns=["link", "question", "answer"])




cats = get_categories()

cat_list = make_categories_list(cats)

sample_qs = sample(cat_list, 100)


# q = get_question(sample_qs[0])



df = pd.DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    df = df.append(get_question(q))

df = df.reset_index(drop=True)

df.to_csv("data/darulifta.csv", index=False)
