# (setq python-shell-interpreter "./venv/bin/python")

import requests
from bs4 import BeautifulSoup
from random import sample
from pandas import DataFrame

# gets a dictionary of category links and number of questions per page
def get_num_per_category(): 
    r = requests.get("http://www.sistani.org/english/qa/")
    soup = BeautifulSoup(r.text, 'html.parser')

    d = dict()
    for link in soup.find_all('a'):
        title =  link.get('title')
        if title and "Number of questions" in title:
            num = str.split(title, ":")[1].strip()
            d[link.get('href')] =  num
            # print("|", link.get_text(), "|",  num, "|")

    return d

# makes a list of tuples with (link, qnumber) where qnumer is the nth
# question on that page
def make_categories_list(d):
    questions = list()
    total_questions = 0
    for k, v in d.items():
        total_questions += int(v)
        for i in range(int(v)):
            questions.append((("http://www.sistani.org" + k), i))
    return questions




def get_question(link, n):
    # get page
    r = requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')

    # get all questions, and select the nth one
    qs = soup.find_all("div", class_="one-qa")

    # we need to check to make sure the nth one exists. if it doesn't
    # get the first one and print an error
    if n < len(qs):
        target_q = str(qs[n])
    else:
        print("Error: could not find post ", n, " at ", link, ". Taking the first post instead.", sep="")
        target_q = str(qs[0])

    # split it into parts
    parts = target_q.split('<span class="nvy b">Question</span>:')[-1].split('\n<div class="b">\n<span class="nvy">Answer</span>:')
    question_text = parts[0].replace('<br/>', ' ').strip()
    answer_text = parts[1].split('\n</div>\n<div class="clr"></div>\n</div>')[0].replace('<br/>', ' ').strip()

    return DataFrame([[link, question_text, answer_text]], columns=["link", "question", "answer"])



num_per = get_num_per_category()
cat_list = make_categories_list(num_per)

sample_qs = sample(cat_list, 100)

df = DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    link, n = q
    df = df.append(get_question(link, n))

df = df.reset_index(drop=True)

df.to_csv("data/sistani-lomg.csv", index=False)






    

# print(num_per[(cat_list[sample_indicies[0]])])

