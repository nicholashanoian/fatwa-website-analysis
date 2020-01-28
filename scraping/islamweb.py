# (setq python-shell-interpreter "./venv/bin/python")

import requests, pandas as pd
from bs4 import BeautifulSoup as bs
from random import sample


def get_categories():
    r = requests.get("https://www.islamweb.net/en/fatawa/?tab=1")
    soup = bs(r.text, "html.parser")

    links = soup.find_all('a')

    good_links = []
    for link in links:
        if link.find_all("i", class_="fa fa-folder"):
            n = int(link.find("span").text)
            good_links.append((link.get('href'), n))
    
    return good_links

def make_categories_list(cats):
    '''makes a list of tuples with (link, qnumber) where qnumer is the nth
    question on that page'''
    questions = []
    for link, n in cats:
        for i in range(int(n)):
            questions.append(((link), i))
    return questions


def get_question(link_and_n):
    link, n = link_and_n
    page, pos = divmod(n, 15)
    page_link = "https://www.islamweb.net" + link + "?pageno=" + str(page) + "&tab=1"
    print(page_link)

    r = requests.get(page_link)
    soup = bs(r.text, "html.parser")

    question_links = soup.select("ul.oneitems>li")

    try:
        question_link = "https://www.islamweb.net" + question_links[pos].find("a").get("href")
    except:
        question_link = "https://www.islamweb.net" + question_links[pos].find("a").get("href")

    print(question_link)
    r = requests.get(question_link)
    soup = bs(r.text, "html.parser")

    question = bs(str(soup.find_all("div", class_="mainitem")[1])
                  .split('<div class="mainitem">\n<h3 class="mainitemtitle2">\r\n\t\t\t\tQuestion\r\n\t\t\t</h3>\n')[1],
                  "html.parser").text
    answer = bs(str(soup.find_all("div", class_="mainitem")[2]).split('<div class="mainitem">\n<h3 class="mainitemtitle2">\r\n\t\t\t\tAnswer\r\n\t\t\t</h3>\n')[1], "html.parser").text
    
    return pd.DataFrame([[question_link, question, answer]], columns=["link", "question", "answer"])









cats = get_categories()

cat_list = make_categories_list(cats)

sample_qs = sample(cat_list, 100)

df = pd.DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    df = df.append(get_question(q))

df = df.reset_index(drop=True)

df.to_csv("data/islamweb.csv", index=False)
