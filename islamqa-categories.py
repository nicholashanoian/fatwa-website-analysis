import requests
from bs4 import BeautifulSoup as bs
import random

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





with open('sidebar.html', 'r') as file:
    data = file.read().replace('\n', '')

sidebar = bs(data)
# i = 0
d = dict()
for topic in sidebar.select("#top > li"):
    title = topic.select_one("a").text
    num_fatwas = 0
    for link in topic.find_all('a'):
        print(link.get('href'))
        num_fatwas += get_num_posts(link.get('href'))
    d[title] = num_fatwas
    # i += 1

print(d)


