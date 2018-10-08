#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:03:12 2018

@author: owen
"""

import re
import requests

from bs4 import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"

JOURNAL_DICT = {
    "financial history review": "https://www.cambridge.org/core/journals/financial-history-review",
    "business history review": "https://www.cambridge.org/core/journals/business-history-review",
    "journal of finance": "https://onlinelibrary.wiley.com/action/doSearch?SeriesKey=15406261&sortBy=Earliest&pageSize=20&startPage={}"
}


def get_web_page_soup(journal, path):
    url = '{}{}'.format(
        JOURNAL_DICT[journal], path)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    page_soup = BeautifulSoup(request_page.content, "lxml")
    return page_soup


def get_journal_pages(journal, all_issue_path="/all-issues"):
    page_soup = get_web_page_soup(
        journal=journal,
        path=all_issue_path)
    hyperlinks = []
    for issue_block in page_soup.find_all("li", {"class", "accordion-navigation"}):
        for word in str(issue_block).split():
            if '/issue/' in word:
                hyperlink = clean_hyperlink(hyperlink=word)
                hyperlinks.append(hyperlink)
    author_details = {}
    for i in range(len(hyperlinks[1:2])):
        print "Collecting articles from journal {}/{}".format(
                i+1, len(hyperlinks))
        article_details = get_article_details(
            journal=journal,
            issue_hyperlink=hyperlinks[i])
        author_details.update(article_details)
    return author_details


def get_article_details(journal, issue_hyperlink):
    url = '{}{}'.format(
        JOURNAL_DICT[journal],  
        issue_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    issue_soup = BeautifulSoup(request_page.content, "lxml")
    volume = issue_soup.find("span", {"class", "volume"}).get_text().strip().replace('\n', ' ')
    author_details = {volume : []}
    all_articles = issue_soup.find_all("a", {"class", "part-link"})
    for issue_block in all_articles[:len(all_articles)-2]:
        author_details[volume].append(
            get_author_details(
                journal=journal,
                article_hyperlink=issue_block.attrs['href']))
    return author_details


def get_author_details(journal, article_hyperlink):
    url = '{}{}'.format(
        JOURNAL_DICT[journal],  
        article_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    author_details = {
        'title': attribute_check(article_soup, "h1", {"class", "article-title"}),
        'doiUrl': attribute_check(article_soup, "a", {"class", "url doi"}),
        'authors': attribute_check(article_soup, "a", {"class", "more-by-this-author "}),
        'abstract': attribute_check(article_soup, "div", {"class", "abstract"}),
        'corresp': attribute_check(article_soup, "div", {"class", "corresp"}),
        'email': parse_email(article_soup=article_soup),
        'institution': attribute_check(article_soup, "institution"),
        'address': parse_address(soup=article_soup),
        'hyperlink': url
    }
    return author_details


def attribute_check(soup, tag, attrs=None):
    if attrs is None:
        raw_chunk = soup.find(tag)
    else:
        raw_chunk = soup.find(tag, attrs)
    if raw_chunk is not None:
        return raw_chunk.get_text().strip()
    else:
        return None


def parse_address(soup):
    address_array = soup.find_all("addrline")
    address = soup.find("institution")
    if address is None:
        return None
    else:
        address = address.get_text() + ', '
        for a in address_array:
            address += a.get_text() + ' '
        return address


def parse_email(article_soup):
    article_str = str(article_soup)
    k = re.search('mailto:(.*)"', article_str)
    if k is None:
        return None
    else:
        return k.group(1)


def clean_hyperlink(hyperlink):
    link = hyperlink.split('"')[1]
    return link


def flatten_author_details(author_details, email_only=False):
    d = []
    for k in author_details.keys():
        for a in author_details[k]:
            if email_only:
                d.append(a['email'])
            else:
                d.append(a)
    return d



class ScrapeWiley():
    def init():
        pass
    
    def search_journal(journal, page):
        url = JOURNAL_DICT[journal].format(page)
        request_page = requests.get(
                url=url,
                headers={'User-Agent': USER_AGENT})
        search_page_soup = BeautifulSoup(request_page.content, "lxml")
        k = search_page_soup.find_all("div", {"class": "item__body"})
        for l in k:
            if 'rapid' in l.find("span", {"class": "meta__type"}).get_text().lower() or \
                'article' in l.find("span", {"class": "meta__type"}).get_text().lower():
                    title = l.find("a", {"id": "publication_title"}).get_text()
                    raw_abstract = l.find("div", {"class": "article-section__content abstractlang_en main"})
                    abstract = raw_abstract.get_text().strip().split('\n')[0]
                    doi_url = l.find("a", {"id": "publication_title"}).attrs['href']
                    raw_authors = l.find_all("span", {"class": "hlFld-ContribAuthor"})
                    authors = []
                    for author in raw_authors:
                        authors.append(author.get_text().title())
                    





BASE_URL = "https://onlinelibrary.wiley.com"
request_page = requests.get(url="https://onlinelibrary.wiley.com/doi/10.1111/jofi.12728", headers={'User-Agent': USER_AGENT})
page_soup = BeautifulSoup(request_page.content, "lxml")


match = re.findall(r'[\w\.-]+@[\w\.-]+', str(page_soup))
list(set(match))


a = "author-info accordion-tabbed__content"