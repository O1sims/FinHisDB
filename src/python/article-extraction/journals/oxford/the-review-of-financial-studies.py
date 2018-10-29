import re
import pickle
import os.path
import requests

from bs4 import BeautifulSoup
from datetime import datetime


DATA_PATH = '/home/owen/Code/FinHisDB/src/python/article-extraction/journals/data'

JOURNAL = 'the-review-of-financial-studies'
BASE_URL = 'https://academic.oup.com/rfs'
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"


def parse_issues_archive():
    url = BASE_URL + "/issue-archive"
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    raw_issues_list = article_soup.find("div", {"class": "widget widget-IssueYears widget-instance-OUP_Issues_Year_List"})
    raw_issue_years = raw_issues_list.find_all("div")
    years = []
    for raw_year in raw_issue_years:
        clean_year = raw_year.get_text().strip()
        years.append(url + '/' + str(clean_year))
    return years


def parse_issues_list(year_url):
    issue_links = []
    request_page = requests.get(
        url=year_url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    raw_issues_list = article_soup.find("div", {"class": "widget widget-IssuesAndVolumeListManifest widget-instance-OUP_Issues_List"})
    raw_issues = raw_issues_list.find_all("div", {"class": "customLink"})
    for issue in raw_issues:
        issue_link = issue.find("a").attrs['href']
        issue_links.append("https://academic.oup.com" + issue_link)
    return issue_links


def get_article_list(issue_url):
    article_list = []
    request_page = requests.get(
        url=issue_url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    raw_articles_list = article_soup.find("div", {"id": "resourceTypeList-OUP_Issue"})
    articles_section = raw_articles_list.find_all("section")
    for article in articles_section:
        raw_article_info = article.find("div", {"class": "al-article-items"})
        article_list.append({
            'title': raw_article_info.find("h5", {"class": "customLink item-title"}).get_text().strip(),
            'hyperlink': "https://academic.oup.com" + raw_article_info.find("a").attrs['href']
        })


def parse_artcle_details(article_url):
    request_page = requests.get(
        url=article_url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    full_abstract = article_soup.find("section", {"class": "abstract"})
    abstract = full_abstract("p")[0].get_text().strip()