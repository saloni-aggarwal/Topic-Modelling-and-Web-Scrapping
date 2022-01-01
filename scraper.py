# NAME(s): Saloni Aggarwal and Lekhya Rao Mummareddy

import json

import gensim as gensim
import requests
from bs4 import BeautifulSoup
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()


# Method to perform stemming and lemmatization on an article body
def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


# Method to tokenize, perform stemming and lemmatization using the method above and removing stopwords
def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))

    return result


# Site from where articles are to be downloaded
site1 = 'https://www.smithsonianmag.com/'

# Fetching homepage content from the site
page1 = requests.get(site1, params={'limit': '100'})
# Using BeautifulSoup we are pulling all the data from the site to html form
soup1 = BeautifulSoup(page1.content, "html.parser")

# finding all links from the page
links = soup1.find_all('a')
new_links = []
# for each link
for link in links:
    # checking if it has a class attribute
    if link.has_attr('class'):
        # if yes, extracting the class smart-news from the links
        if "smart-news" in link['class'][0] or "smartnews" in link['class'][0]:
            # collecting the smartnews article links
            new_links.append(link)
pagelinks = []

# creating proper full links for each link
for link in new_links:
    pagelinks.append('https://www.smithsonianmag.com' + link.get('href'))

posts = []
# this code repeats the process above to collect links for each article from the smart-news section
for i in range(1, len(pagelinks)):
    sites = requests.get(pagelinks[i])
    soup2 = BeautifulSoup(sites.content, "html.parser")
    site_articles = soup2.find_all(class_="article-list-text")

    for site in site_articles:
        link = site.find('a')
        posts.append('https://www.smithsonianmag.com' + link.get('href'))

post_text = []
title = []
author = []
date = []
# reading each article to find the detains of each article
for i in range(len(posts)):
    post = requests.get(posts[i])
    soup3 = BeautifulSoup(post.content, "html.parser")
    if soup3.find('script', type='application/ld+json') is None:
        continue
    data = json.loads(soup3.find('script', type='application/ld+json').text)
    # collecting title for each article
    title.append(data['headline'])
    # collecting published date for each article
    date.append(data['datePublished'])
    # collecting author name for each article
    if data['author']['name']:
        author.append(data['author']['name'][0])
    else:
        author.append("None")
    # collecting body text for each article
    texts = soup3.find_all(class_='articleLeft')
    for text in texts:
        t = text.text
        t = ' '.join(t.split())
    post_text.append(t)

# adding the information of all posts into a dataframe
df = pd.DataFrame(columns=['title', 'author', 'date', 'body', 'preprocessed'])
df['title'] = title
df['author'] = author
df['date'] = date
df['body'] = post_text
post_text_word = []
# print(post_text[10])

# Performing lemmatization and stemming on the list of posts
result = []
for sentence in post_text:
    print(sentence)
    result.append(preprocess(sentence))
# adding preprocessed text to dataframe
df['preprocessed'] = result
# converting the dataframe to a json file
df.to_json('articles.json')

