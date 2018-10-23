#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:03:12 2018

@author: owen
"""

import re
import ast
import json
import requests

from datetime import datetime
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



BASE_URL = "https://onlinelibrary.wiley.com"


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
        author_details = []
        for l in k:
            if 'rapid' in l.find("span", {"class": "meta__type"}).get_text().lower() or \
                'article' in l.find("span", {"class": "meta__type"}).get_text().lower():
                    doi_url = l.find("a", {"id": "publication_title"}).attrs['href']
                    authors = []
                    for author in l.find_all("span", {"class": "hlFld-ContribAuthor"}):
                        authors.append(author.get_text().title())
                    article_details = scrape_article(hyperlink=doi_url)
                    author_details.append(
                        {
                            'title': l.find("a", {"id": "publication_title"}).get_text(),
                            'abstract': parse_abstract(search_page_soup=l),
                            'doiUrl': doi_url,
                            'authors': authors,
                            'articleDetails': article_details
                        })
        return author_details
    

    def parse_abstract(search_page_soup):
        raw_abstract = search_page_soup.find("div", {"class": "article-section__content abstractlang_en main"})
        if raw_abstract is not None:
            return raw_abstract.get_text().strip().split('\n')[0]
        else:
            return None

                
    def parse_author_info(page_soup):
        raw_author_infos = page_soup.find_all("div", {"class": "author-info accordion-tabbed__content"})
        for info in raw_author_infos:
            clean_author_info = info.get_text()
            if len(clean_author_info) > 100:
                return clean_author_info
            
    def parse_emails(page_soup):
        match = re.findall(r'[\w\.-]+@[\w\.-]+', str(page_soup))
        emails = list(set(match))
        if emails == []:
            return None
        else:
            return emails
        
    def parse_volume_issue(page_soup):
        vol_iss = page_soup.find("p", {"class": "volume-issue"})
        if vol_iss is None:
            cover_label = page_soup.find("p", {"class": "cover-label"})
            if cover_label is None:
                return None
            else:
                return cover_label.get_text()
        else:
            return vol_iss.get_text()
    
    
    def parse_publication_date(page_soup):
        pub_date = page_soup.find("span", {"class": "epub-date"}).get_text()
        date_time = datetime.strptime(pub_date, '%d %B %Y')
        return date_time
    
    
    def scrape_article(hyperlink):
        url = '{}{}'.format(BASE_URL, hyperlink)
        request_page = requests.get(
                url=url,
                headers={'User-Agent': USER_AGENT})
        article_page_soup = BeautifulSoup(request_page.content, "lxml")
        article_details = {
            'authorInfo': parse_author_info(page_soup=article_page_soup),
            'emails': parse_emails(page_soup=article_page_soup),
            'volume': parse_volume_issue(page_soup=article_page_soup),
            'published': parse_publication_date(page_soup=article_page_soup)
        }
        return article_details
    





BASE_URL = 'https://www.sciencedirect.com'

journal = "journal-of-financial-economics"


class ScrapeElsevier():
    def init():
        pass

    def get_author_data(article_data):
        data = []
        for author in article_data["authors"]:
            author_name = author['givenName'] + " " + author['surname']
            if 'emails' in author.keys():
                email = author['emails'][0]
            else:
                email = None
            data.append({'authorName': author_name, 'email': email})
        return data

    def parse_abstract(hyperlink, journal):
        url = BASE_URL + hyperlink
        request_page = requests.get(
                url=url,
                headers={'User-Agent': USER_AGENT})
        article_soup = BeautifulSoup(request_page.content, "lxml")
        if journal in ["journal-of-financial-economics", 
                       "journal-of-banking-and-finance"]:
            for i in range(1,10):
                para = "spara000{}".format(i)
                abstract = article_soup.find("p", {"id": para})
                if abstract is not None:
                    return abstract.get_text().encode('utf-8')
        elif journal == "international-review-of-economics-and-finance":
            abstract = article_soup.find("p", {"id": "abspara0010"})
            if abstract is not None:
                return abstract.get_text().encode('utf-8')
        return abstract

    def parse_address(hyperlink, journal, institutions_only=False):
        url = BASE_URL + hyperlink
        request_page = requests.get(
                url=url,
                headers={'User-Agent': USER_AGENT})
        article_soup = BeautifulSoup(request_page.content, "lxml")
        raw_data = article_soup.find("script", {"type": "application/json"}).get_text().encode('utf-8')
        sd = json.loads(raw_data)
        affiliations_dict = sd['authors']['affiliations']
        if institutions_only:
            institutions = []
            for v in affiliations_dict.itervalues():
                l = len(v['$$']) - 1
                if journal in "journal-of-financial-economics":
                    institutions.append(v['$$'][l]['$$'][0]['_'])
                elif journal == "international-review-of-economics-and-finance":
                    institutions.append(v['$$'][0]['_'])
                elif journal == "journal-of-banking-and-finance":
                    institutions.append(v['$$'][l]['_'])
            return institutions
        else:
            addresses = []
            for v in affiliations_dict.itervalues():
                l = max(len(v['$$']) - 2, 0)
                addresses.append(v['$$'][l]['_'])
        return addresses

    def search_journal(journal):
        issue_links = []
        if journal == "journal-of-banking-and-finance":
            for i in range(32, 98):
                issue_links.append('/vol/{}/suppl/C'.format(i))
        elif journal == "journal-of-financial-economics":
            for i in range(130,131):
                for j in range(1,4):
                    issue_links.append('/vol/{}/issue/{}'.format(i, j))
        elif journal == "international-review-of-economics-and-finance":
            for i in range(57, 58):
                issue_links.append('/vol/{}/suppl/C'.format(i))
        author_details = []
        for link in issue_links:
            issue_url = BASE_URL + '/journal/' + journal + link
            issue_page = requests.get(
                    url=issue_url,
                    headers={'User-Agent': USER_AGENT})
            issue_page_soup = BeautifulSoup(issue_page.content, "lxml")
            raw_page_data = issue_page_soup.find("script", {"type": "application/json"}).get_text().encode('utf-8')
            literal_page_data = ast.literal_eval(raw_page_data)
            page_data = json.loads(literal_page_data)
            if journal in ["journal-of-financial-economics", "journal-of-banking-and-finance"]:
                partial_dict = page_data['articles']['ihp']['data']['issueBody']
                if 'includeItem' in partial_dict.keys():
                    article_list = partial_dict['includeItem']
                elif 'issueSec' in partial_dict.keys():
                    
                article_list = page_data['articles']['ihp']['data']['issueBody']['includeItem']
                for article in article_list:
                    if article['authors'] != []:
                        if 'issFirst' in article.keys():
                            issue = article['issFirst']
                        else:
                            issue = None
                        author_detail = {
                            'title': article['title'],
                            'doiUrl': article['doi'],
                            'authors': get_author_data(article_data=article),
                            'abstract': parse_abstract(
                                    hyperlink=article['href'], journal=journal),
                            'institutions': parse_address(
                                    hyperlink=article['href'], journal=journal, institutions_only=True),
                            'coverDate': article['coverDateStart'],
                            'journal': article['srctitle'],
                            'year': article['yearNav'],
                            'volume': article['volFirst'],
                            'issue': issue,
                            'address': parse_address(hyperlink=article['href'], journal=journal),
                            'hyperlink': "https://www.sciencedirect.com{}".format(article['href'])}
                        author_details.append(author_detail)
            elif journal == "international-review-of-economics-and-finance":
                partial_dict = page_data['articles']['ihp']['data']['issueBody']
                if 'issueSec' in partial_dict.keys():
                    article_list = partial_dict['issueSec'][1]['includeItem']
                else:
                    article_list = partial_dict['includeItem']
                for article in article_list:
                    if article['authors'] != []:
                        if 'issFirst' in article.keys():
                            issue = article['issFirst']
                        else:
                            issue = None
                        author_detail = {
                            'title': article['title'],
                            'doiUrl': article['doi'],
                            'authors': get_author_data(article_data=article),
                            'abstract': parse_abstract(
                                    hyperlink=article['href'], journal=journal),
                            'institutions': parse_address(
                                    hyperlink=article['href'], journal=journal, institutions_only=True),
                            'coverDate': article['coverDateStart'],
                            'journal': article['srctitle'],
                            'year': article['yearNav'],
                            'volume': article['volFirst'],
                            'issue': issue,
                            'address': parse_address(
                                    hyperlink=article['href'], journal=journal),
                            'hyperlink': "https://www.sciencedirect.com{}".format(article['href'])
                        }
                        author_details.append(author_detail)
        return author_details



articles = search_journal(journal)


journal = 'journal of finance'
author_details = []
for i in range(10):
    print "Parsing search page {}".format(i)
    author_details += search_journal(journal, i)

emails = []
for details in author_details:
    emails.append(details['articleDetails']['emails'])
    
    
