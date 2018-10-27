import re
import pickle
import os.path
import requests

from bs4 import BeautifulSoup


JOURNAL = "business-history-review"
JOURNAL_URL = "https://www.cambridge.org/core/journals/business-history-review"
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"
DATA_PATH = '/home/owen/Code/FinHisDB/src/python/article-extraction/journals/data'


def get_journal_pages(all_issue_path="/all-issues"):
    page_soup = get_web_page_soup(
        path=all_issue_path)
    hyperlinks = []
    for issue_block in page_soup.find_all("li", {"class", "accordion-navigation"}):
        for word in str(issue_block).split():
            if '/issue/' in word:
                hyperlink = clean_hyperlink(hyperlink=word)
                hyperlinks.append(hyperlink)
    author_details = []
    r = min(len(hyperlinks)-1, 500)
    for i in range(r):
        print "Collecting data file"
        author_details = load_pickle()
        print "Collecting articles from journal {}/{}".format(
                i+1, r)
        try:
            article_details = get_article_details(
                issue_hyperlink=hyperlinks[i])
            author_details += article_details
            print "Saving data file"
            save_pickle(author_details=author_details)
        except AttributeError:
            print "Parsing error!!"
    return author_details


def get_web_page_soup(path):
    url = '{}{}'.format(
        JOURNAL_URL, path)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    page_soup = BeautifulSoup(request_page.content, "lxml")
    return page_soup


def get_article_details(issue_hyperlink):
    url = '{}{}'.format(
        JOURNAL_URL,
        issue_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    issue_soup = BeautifulSoup(request_page.content, "lxml")
    author_details = []
    all_articles = issue_soup.find_all("a", {"class", "part-link"})
    for issue_block in all_articles[:len(all_articles)-2]:
        author_details.append(
            get_author_details(
                article_hyperlink=issue_block.attrs['href']))
    return author_details


def get_author_details(article_hyperlink):
    url = '{}{}'.format(
        JOURNAL_URL,
        article_hyperlink)
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    article_details = {
        'title': attribute_check(article_soup, "h1", {"class", "article-title"}),
        'doiUrl': attribute_check(article_soup, "a", {"class", "url doi"}),
        'authors': attribute_check(article_soup, "a", {"class", "more-by-this-author "}),
        'abstract': attribute_check(article_soup, "div", {"class", "abstract"}),
        'corresp': attribute_check(article_soup, "div", {"class", "corresp"}),
        'email': parse_email(article_soup=article_soup),
        'institution': attribute_check(article_soup, "institution"),
        'address': parse_address(soup=article_soup),
        'volume': content_attribute(article_soup, "meta", {"name": "citation_volume"}),
        'journal': content_attribute(article_soup, "meta", {"name": "citation_journal_title"}),
        'issue': content_attribute(article_soup, "meta", {"name": "citation_issue"}),
        'keywords': content_attribute(article_soup, "meta", {"name": "citation_keywords"}),
        'hyperlink': url
    }
    return article_details


def content_attribute(soup, tag, attrs):
    raw_chunk = soup.find(tag, attrs)
    if raw_chunk is not None:
        return raw_chunk.attrs['content']
    else:
        return None


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
    match = re.findall(
        r'[\w\.-]+@[\w\.-]+',
        str(article_soup))
    emails = list(set(match))
    emails = [s for s in emails if 'no-reply' not in s]
    if not emails:
        return None
    else:
        return emails


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


def extract_author_and_email(journal_list):
    author_list = []
    for iss in journal_list.keys():
        article_list = journal_list[iss]
        for article in article_list:
            if article['email'] is not None:
                author_list.append({
                    'name': article['authors'],
                    'email': article['email']
                })
    return author_list


if __name__ == '__main__':
    get_journal_pages()
