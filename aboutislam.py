# (setq python-shell-interpreter "./venv/bin/python")

import requests, pandas as pd
from bs4 import BeautifulSoup as bs
from random import sample

import requests_cache                     
requests_cache.install_cache('demo_cache')

def get_categories():
    r = requests.get("http://aboutislam.net/ask-the-scholar/")
    soup = bs(r.text, "html.parser")

    # manually gotten earlier
    frequencies = [178, 24, 9, 44, 26, 57, 358, 229, 47, 102, 8, 198, 68, 8, 10, 136, 140, 5, 35, 4, 16, 16]

    links = [link.get("value") for link in
             soup.find("div", class_="live-fatwa-select").find_all("option")[1:1+len(frequencies)]]
        
    return list(zip(links, frequencies))


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
    page,pos = divmod(n, 12)
    link_parts = link.split('?')
    page_link = link_parts[0] + "page/%s/?" % (page + 1) + link_parts[1]

    print(page_link)
    r = requests.get(page_link)
    soup = bs(r.text, "html.parser")

    links = soup.select("div.ask-the-scholar-sub-cat>article>h3>a")
    try:
        question_link = links[pos].get("href")
    except:
        try:
            question_link = links[0].get("href")
        except:
            print("Could not find any questions")
            return

    print(question_link)
    r = requests.get(question_link)
    soup = bs(r.text, "html.parser")    

    question = bs(str(soup.select_one("table").find_all("tr")[2]).split('<tr><td> Question</td><td>')[1], "html.parser").text.strip()
    answer = soup.find("div", class_="entry").text.replace("\xa0", " ")

    return pd.DataFrame([[question_link, question, answer]], columns=["link", "question", "answer"])




cats = get_categories()

cat_list = make_categories_list(cats)

sample_qs = sample(cat_list, 100)


# q = get_question(sample_qs[0])



df = pd.DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    df = df.append(get_question(q))

df = df.reset_index(drop=True)

df.to_csv("data/aboutislam.csv", index=False)
