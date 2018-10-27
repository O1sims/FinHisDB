import ast
import json
import pickle
import os.path
import requests

from bs4 import BeautifulSoup


DATA_PATH = '/home/owen/Code/FinHisDB/src/python/article-extraction/journals/data'

JOURNAL = 'international-review-of-economics-and-finance'
BASE_URL = 'https://www.sciencedirect.com'
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"


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


def parse_abstract(hyperlink):
    url = BASE_URL + hyperlink
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    abstract = article_soup.find("p", {"id": "abspara0010"})
    if abstract is not None:
        return abstract.get_text().encode('utf-8')
    return abstract


def parse_address(hyperlink):
    url = BASE_URL + hyperlink
    request_page = requests.get(
        url=url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    raw_data = article_soup.find("script", {"type": "application/json"}).get_text().encode('utf-8')
    sd = json.loads(raw_data)
    affiliations_dict = sd['authors']['affiliations']
    addresses = []
    for v in affiliations_dict.itervalues():
        if '_' in v['$$'][0].keys():
            addresses.append(v['$$'][0]['_'])
        elif '$$' in v['$$'][0].keys():
            addresses.append(v['$$'][0]['$$'][0]['_'])
        else:
            addresses.append(None)
    return addresses


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


def extract_journal():
    issue_links = []
    for i in range(36, 58):
        issue_links.append('/vol/{}/suppl/C'.format(i))
    for link in issue_links:
        try:
            print "Collecting data file"
            author_details = load_pickle()
            print "Parsing issue link: {}".format(link)
            issue_url = BASE_URL + '/journal/' + JOURNAL + link
            issue_page = requests.get(
                url=issue_url,
                headers={'User-Agent': USER_AGENT})
            issue_page_soup = BeautifulSoup(issue_page.content, "lxml")
            raw_page_data = issue_page_soup.find("script", {"type": "application/json"}).get_text().encode('utf-8')
            literal_page_data = ast.literal_eval(raw_page_data)
            page_data = json.loads(literal_page_data)
            partial_dict = page_data['articles']['ihp']['data']['issueBody']
            if 'issueSec' in partial_dict.keys():
                if len(partial_dict['issueSec']) > 1:
                    article_list = partial_dict['issueSec'][1]['includeItem']
                else:
                    article_list = partial_dict['issueSec'][0]['includeItem']
            else:
                article_list = partial_dict['includeItem']
            for article in article_list:
                if article['authors']:
                    if 'issFirst' in article.keys():
                        issue = article['issFirst']
                    else:
                        issue = None
                    author_detail = {
                        'title': article['title'],
                        'doiUrl': article['doi'],
                        'authors': get_author_data(
                            article_data=article),
                        'abstract': parse_abstract(
                            hyperlink=article['href']),
                        'coverDate': article['coverDateStart'],
                        'journal': article['srctitle'],
                        'year': article['yearNav'],
                        'volume': article['volFirst'],
                        'issue': issue,
                        'address': parse_address(
                            hyperlink=article['href']),
                        'hyperlink': BASE_URL + "{}".format(article['href'])
                    }
                    author_details.append(author_detail)
                    save_pickle(author_details=author_details)
        except AttributeError:
            print "Parsing error at {}".format(link)
            continue
    return author_details


def extract_author_and_email(article_list):
    author_list = []
    for article in article_list:
        for author in article['authors']:
            if author['email'] is not None:
                author_list.append({
                    'name': author['authorName'],
                    'email': author['email']
                })
    return author_list


if __name__ == '__main__':
    extract_journal()
