'''
ここいろの記事タイトルと配列化された文章を取得するスクリプト
'''

from bs4 import BeautifulSoup
from urllib import request


# 不要な文字列を消すための変換テーブル
table = str.maketrans({
    '\r': '',
    '\n': '',
    '\u3000': '',
    '\xa0': '',
    '.': ''
})

# 新着記事

def get_new_topics_title(num):
    home_url = 'https://coco-iro.jp/'

    html = request.urlopen(home_url)
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all(attrs={"class": "item"})
    
    titles = []
    for item in items:
        titles.append(item.find(attrs={"class": "title"}).get_text().translate(table))
    titles = titles[:num]
    
    return titles

def get_new_topics_article(num):
    home_url = 'https://coco-iro.jp/'

    html = request.urlopen(home_url)
    soup = BeautifulSoup(html, "html.parser")

    items = soup.find_all(attrs={"class": "item"})

    item = items[num]
    title = item.find(attrs={"class": "title"}).get_text()
    target_url = home_url + item.get('href')[1:]
    target_html = request.urlopen(target_url)
    target_soup = soup = BeautifulSoup(target_html, "html.parser")
    article = target_soup.find(id="article")
    paragraphs = article.find_all('p')

    text = ""
    # # 不要な文字列を消すための変換テーブル
    # table = str.maketrans({
    #     '\r': '',
    #     '\n': '',
    #     '\u3000': '',
    #     '\xa0': '',
    #     '.': ''
    # })
    for paragraph in paragraphs:
        if paragraph.get("class") is not None:
            if paragraph.get("class") == 'map-open':
                continue
        text += paragraph.get_text().translate(table)
    sentences = text.split('。')
    
    return title, sentences

# ランキング

def get_ranking_title(num):
    home_url = 'https://coco-iro.jp/'

    html = request.urlopen(home_url)
    soup = BeautifulSoup(html, "html.parser")
    
    ranking_container = soup.find(attrs={"class": "ranking-container"})
    rankings = ranking_container.find_all('li')

    items = soup.find_all(attrs={"class": "item"})
    
    titles = []
    for ranking in rankings:
        titles.append(ranking.find(
            attrs={"class": "ranking-title"}).get_text().translate(table))
    titles = titles[:num]
    
    return titles


def get_ranking_article(num):
    home_url = 'https://coco-iro.jp/'

    html = request.urlopen(home_url)
    soup = BeautifulSoup(html, "html.parser")

    ranking_container = soup.find(attrs={"class": "ranking-container"})
    rankings = ranking_container.find_all('li')
    
    ranking = rankings[num]
    title = ranking.find(attrs={"class": "ranking-title"}).get_text()
    target_url = home_url + ranking.find('a').get('href')[1:]
    target_html = request.urlopen(target_url)
    target_soup = soup = BeautifulSoup(target_html, "html.parser")
    article = target_soup.find(id="article")
    paragraphs = article.find_all('p')

    text = ""
    # 不要な文字列を消すための変換テーブル
    table = str.maketrans({
        '\r': '',
        '\n': '',
        '\u3000': '',
        '\xa0': ''
    })
    for paragraph in paragraphs:
        if paragraph.get("class") is not None:
            if paragraph.get("class") == 'map-open':
                continue
        text += paragraph.get_text().translate(table)
    sentences = text.split('。')
    return title, sentences
