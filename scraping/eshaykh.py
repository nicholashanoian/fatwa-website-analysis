# (setq python-shell-interpreter "./venv/bin/python")

import requests, pandas as pd
from bs4 import BeautifulSoup as bs
from random import sample

headers = {"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"}



def get_categories():
    r = requests.get("https://eshaykh.com/", headers=headers)
    soup = bs(r.text, 'html.parser')

    links = soup.find_all('a')
    good_links = [(link.get('href'), int(link.text.split('(')[-1][:-1]))
                  for link in links
                  if "https://eshaykh.com/category/" in link.get('href', "")
                  and "(" in link.text
                  and ")" in link.text]
    
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
    page, pos = divmod(n, 10)
    print(link + "page/" + str(page))
    r = requests.get(link + "page/" + str(page), headers=headers)
    soup = bs(r.text, 'html.parser')

    question_links = soup.find_all("h2", class_="entry-title")
    if pos < len(question_links):
        question_link = question_links[pos].find("a").get('href')
    else:
        question_link = question_links[0].find("a").get('href')

    
    print(question_link)
    r = requests.get(question_link, headers=headers)
    soup = bs(r.text, 'html.parser')

    entry = soup.find("div", class_="entry-content")


    prompt_pairs = [("Question:", "Answer:"),
                    ("Dream:", "Interpretation:"),
                    ("Request:", "Response:"),
                    ("Question", "Answer:")]

    question = None
    answer = None
    
    for q_prompt, a_prompt in prompt_pairs:
        try:
            parts = str(entry).split(a_prompt)

            # extract question and answer text
            question = bs(parts[0].split(q_prompt)[1],
                          'html.parser').text.replace("\xa0", " ")
            answer = bs(parts[1], 'html.parser').text.replace("\xa0", " ")
            break
        except:
            pass

    if question is None or answer is None:
        print("Couldn't match format!")
        return
        
       
    return pd.DataFrame([[question_link, question, answer]], columns=["link", "question", "answer"])


import requests_cache

requests_cache.install_cache('demo_cache')


cats = get_categories()

cat_list = make_categories_list(cats)
    
sample_qs = sample(cat_list, 100)

df = pd.DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    df = df.append(get_question(q))

df = df.reset_index(drop=True)

df.to_csv("data/eshaykh.csv", index=False)
