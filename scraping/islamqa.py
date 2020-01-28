import requests
from bs4 import BeautifulSoup as bs
from random import sample
import math
from pandas import DataFrame

# estimates the number of fatwas in each general category at islamqa.info

# (run-python "venv/bin/python -i")




def get_num_posts(url):
    r = requests.get(url)
    soup = bs(r.text)
    last_page_a = soup.find("a", {"rel":"last"})
    # extract 6 from "https://islamqa.info/en/categories/topics/3/basic-tenets-of-faith?page=6"
    # print(last_page_a)
    if last_page_a:
        num_pages = int(str.split(str.split(last_page_a.get('href'), "?")[1], "=")[1])
        # paginated to 15 per page, take a guess at how many are on last page
        return 15 * (num_pages - 1) + random.randint(1,15)
    else:
        # just one page
        return random.randint(1,15)



def get_categories_list():
    with open('sidebar.html', 'r') as file:
        data = file.read().replace('\n', '')

    sidebar = bs(data)
    # i = 0
    categories_list = []
    for topic in sidebar.select("#top > li"):
        title = topic.select_one("a").text
        num_fatwas = 0
        for link in topic.find_all('a'):
            print(link.get('href'))
            for i in range(get_num_posts(link.get('href'))):
                categories_list.append((link.get('href'), i))
    return categories_list

def get_question(link, n):
    # because 15 results per page
    page, index = divmod(n, 15)
    r = requests.get(link + "?page=" + str(page))
    soup = bs(r.text, 'html.parser')

    post_links = soup.find_all("a", class_="card post-card")
    if index < len(post_links):
        print(post_links[index].get('href'))
        r = requests.get(post_links[index].get('href'))
    else:
        print("could not find post", n, "on page", page, "of", link, ". Using first post on page instead")
        r = requests.get(post_links[0].get('href'))

    soup = bs(r.text, 'html.parser')
    question = soup.find("section", class_="single_fatwa__question").find("div", class_="content").text.replace("\xa0\n\n", "\n").strip()
    answer = soup.find("section", class_="single_fatwa__answer").find("div", class_="content").text.replace("\xa0\n\n", "\n").strip()
    return DataFrame([[link, question, answer]], columns=["link", "question", "answer"])
    
    

# categories_list = get_categories_list()

random.seed(1)
sample_qs = sample(categories_list, 1000)

df = DataFrame(columns=["link", "question", "answer"])
    
for q in sample_qs:
    link, n = q
    df = df.append(get_question(link, n))

df = df.reset_index(drop=True)

df.to_csv("data/islamqa-long.csv", index=False)
