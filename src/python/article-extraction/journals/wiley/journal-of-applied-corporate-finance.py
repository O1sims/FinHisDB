import re
import pickle
import os.path
import requests

from bs4 import BeautifulSoup
from datetime import datetime


JOURNAL = "journal-of-applied-corporate-finance"
BASE_URL = "https://onlinelibrary.wiley.com"
JOURNAL_URL = "https://onlinelibrary.wiley.com/action/doSearch?SeriesKey=17456622&sortBy=Earliest&pageSize=20&startPage={}"
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"
DATA_PATH = '/home/owen/Code/FinHisDB/src/python/article-extraction/journals/data'


def search_journal(page):
    url = JOURNAL_URL.format(page)
    request_page = requests.get(
            url=url,
            headers={'User-Agent': USER_AGENT})
    search_page_soup = BeautifulSoup(request_page.content, "lxml")
    k = search_page_soup.find_all("div", {"class": "item__body"})
    author_details = []
    for article_box in k:
        try:
            if 'rapid' in article_box.find("span", {"class": "meta__type"}).get_text().lower() or \
                            'article' in article_box.find("span", {"class": "meta__type"}).get_text().lower():
                    authors = []
                    doi_url = article_box.find("a", {"id": "publication_title"}).attrs['href']
                    for author in article_box.find_all("span", {"class": "hlFld-ContribAuthor"}):
                        authors.append(author.get_text().title())
                    article_details = scrape_article(hyperlink=doi_url)
                    author_details.append({
                        'title': article_box.find("a", {"id": "publication_title"}).get_text(),
                        'abstract': article_details['abstract'],
                        'doiUrl': doi_url,
                        'authors': authors,
                        'emails': article_details['emails'],
                        'volume': article_details['volume'],
                        'published': article_details['published'],
                        'authorInfo': article_details['authorInfo'],
                        'hyperlink': '{}{}'.format(BASE_URL, doi_url)
                    })
        except AttributeError:
            print "Failure to parse an article in page {}!".format(page)
    return author_details


def scrape_article(hyperlink):
    url = '{}{}'.format(BASE_URL, hyperlink)
    request_page = requests.get(
            url=url,
            headers={'User-Agent': USER_AGENT})
    article_page_soup = BeautifulSoup(request_page.content, "lxml")
    article_details = {
        'abstract': parse_abstract(search_page_soup=article_page_soup),
        'authorInfo': parse_author_info(page_soup=article_page_soup),
        'emails': parse_emails(page_soup=article_page_soup),
        'volume': parse_volume_issue(page_soup=article_page_soup),
        'published': parse_publication_date(page_soup=article_page_soup)
    }
    return article_details


def parse_abstract(search_page_soup):
    abstract_classes = [
        "article-section article-section__abstract",
        "article-section__content abstractlang_en main",
        "article-section__content en main"
    ]
    for abstract_class in abstract_classes:
        raw_abstract = search_page_soup.find("div", {"class": abstract_class})
        if raw_abstract is None:
            continue
        else:
            return raw_abstract.get_text().strip()
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
    emails = [s for s in emails if 'no-reply' not in s]
    if not emails:
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


def load_pickle():
    data_file = '{}/{}.pickle'.format(
        DATA_PATH, JOURNAL)
    if os.path.isfile(data_file):
        with open(data_file, 'rb') as f:
            return pickle.load(f)
    else:
        return []


def save_pickle(author_details):
    data_file = '{}/{}.pickle'.format(
        DATA_PATH, JOURNAL)
    with open(data_file, 'wb') as f:
        pickle.dump(author_details, f,
                    protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    to_search_page = 5
    article_list = load_pickle()
    for i in range(0, to_search_page):
        print "Parsing search page {}/{}".format(
            i, to_search_page - 1)
        article_list += search_journal(i)
        save_pickle(author_details=article_list)
