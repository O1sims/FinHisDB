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
    "financial history review": "https://www.cambridge.org/core/journals/financial-history-review/all-issues"
}


def get_journal_page(journal):
    url = '{}'.format(
        JOURNAL_DICT[journal])
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    page_soup = BeautifulSoup(request_page.content, "lxml")
    issue_links = []
    for issue_block in page_soup.find_all("li", {"class", "accordion-navigation"}):
        for word in str(issue_block).split():
            if '/issue/' in word:
                issue_links.append(word)


def clean_hyperlink(hyperlink):
    re.compile('"([^"]*)"', hyperlink)
    return hyperlink.split('"')[1]
    
    
    
    
    a = page_soup.find_all("li", {"class", "accordion-navigation"})
    b = a[0]
    
    len(b.find_all("li")[0])
    
    if request_page.status_code == 200:
        page_soup = BeautifulSoup(request_page.content, "lxml")
    else:
        raise ValueError(
            'Page not found: The request received a {} status code'.format(
                request_page.status_code))


def 
