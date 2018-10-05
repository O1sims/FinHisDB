#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:03:12 2018

@author: owen
"""

import re
import json
import requests

from bs4 import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"

JOURNAL_DICT = {
    "financial history review": "https://www.cambridge.org/core/journals/financial-history-review"
}

ISSUE_LINK = "https://www.cambridge.org/core/journals/financial-history-review/core/journals/financial-history-review/issue/232EA68F292ECF1F1991E512C237C8DC"


def get_journal_page(journal):
    url = '{}{}'.format(
        JOURNAL_DICT[journal],
        "/all-issues")
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    journal_page_soup = BeautifulSoup(request_page.content, "lxml")
    issue_hyperlinks = []
    for issue_block in journal_page_soup.find_all("li", {"class", "accordion-navigation"}):
        for word in str(issue_block).split():
            if '/issue/' in word:
                cleaned_word = clean_hyperlink(hyperlink=word)
                issue_hyperlinks.append(cleaned_word)


def get_article_details(journal, issue_hyperlink):
    url = '{}{}'.format(
        JOURNAL_DICT[journal],  
        issue_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    issue_soup = BeautifulSoup(request_page.content, "lxml")
    article_links = []
    for issue_block in issue_soup.find_all("a", {"class", "part-link"}):
        article_links.append(issue_block.attrs['href'])
        

def get_author_details(journal, article_hyperlink):
    url = '{}{}'.format(
        JOURNAL_DICT[journal],  
        article_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    title = article_soup.find("h1", {"class", "article-title"}).get_text()
    doi_url = article_soup.find("a", {"class", "url doi"}).get_text()
    authors = article_soup.find("a", {"class", "more-by-this-author "}).get_text()
    abstract = article_soup.find("div", {"class", "abstract"}).get_text()
    corr = article_soup.find("div", {"class", "corresp"}).get_text()
    email = 'mailto:' in str(article_soup)


def parse_email(article_soup):
    article_str = str(article_soup)
    k = re.search('mailto:(.*)"', article_str)
    return k.group(1)
    

def clean_hyperlink(hyperlink):
    link = hyperlink.split('"')[1]
    return link
    
    
    