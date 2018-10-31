import re
import pickle
import os.path
import requests

from bs4 import BeautifulSoup


JOURNAL = 'the-review-of-financial-studies'
BASE_URL = 'https://academic.oup.com/rfs'
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"

DATA_PATH = '/home/owen/Code/FinHisDB/src/python/article-extraction/journals/data'


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
    print "##### Parsing volume link: {}".format(
        year_url)
    
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
    print "### Parsing issue link: {}".format(
        issue_url)
    
    article_list = []
    request_page = requests.get(
        url=issue_url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    raw_articles_list = article_soup.find("div", {"class": "section-container"})
    articles_section = raw_articles_list.find_all("div", {"class": "al-article-item-wrap al-normal"})
    for article in articles_section:
        raw_article_info = article.find("div", {"class": "al-article-items"})
        a_title = raw_article_info.find("a")
        if "editor's choice" not in a_title.get_text().lower():
            article_list.append("https://academic.oup.com{}".format(
                a_title.attrs['href']))
        else:
            continue
    return article_list


def parse_email(soup):
    match = re.findall(r'[\w\.-]+@[\w\.-]+', str(soup))
    emails = list(set(match))
    emails = [s for s in emails if 'no-reply' not in s]
    if not emails:
        return None
    else:
        return emails[0]

    
def parse_authors(article_soup):
    authors = []
    author_names = article_soup.find_all("span", {"class": "al-author-name-more"})
    for author in author_names:
        authors.append({
            'name': author.find("a", {"class": "linked-name"}).get_text().strip(),
            'affiliation': author.find("div", {"class": "info-card-affilitation"}).get_text().strip(),
            'email': parse_email(soup=author)
        })
    return authors


def parse_title(article_soup):
    raw_title = article_soup.find("h1", {"class": "wi-article-title article-title-main"})
    if raw_title is not None:
        return raw_title.get_text().strip()
    else:
        return None
    
    
def parse_journal(article_soup):
    citation = article_soup.find("div", {"class": "ww-citation-primary"})
    journal_title = citation.find("em").get_text().strip()
    return journal_title


def parse_doi_url(article_soup):
    citation = article_soup.find("div", {"class": "ww-citation-primary"})
    doi_url = citation.find("a").attrs['href']
    return doi_url


def parse_abstract(article_soup):
    abstract_classes = [
        ["section", "astract"],
        ["div", "widget widget-ArticleFulltext widget-instance-OUP_Abstract_Article_FullText_Widget"]
    ]
    for a_class in abstract_classes:
        full_abstract = article_soup.find(a_class[0], {"class": a_class[0]})
        if full_abstract is None:
            continue
        else:
            if a_class[0] == "div":
                return full_abstract("p")[1].get_text().strip()
            else:
                return full_abstract("p")[0].get_text().strip()


def parse_metadata(article_soup):
    metadata_block = article_soup.find("div", {"class": "article-metadata"})
    if metadata_block is None:
        return None
    else:
        raw_metadata = metadata_block.find_all("a")
        metadata = []
        for data in raw_metadata:
            metadata.append(data.get_text())
        return metadata


def parse_article_details(article_url):
    print "# Parsing article link: {}".format(
        article_url)
    
    request_page = requests.get(
        url=article_url,
        headers={'User-Agent': USER_AGENT})
    article_soup = BeautifulSoup(request_page.content, "lxml")
    article_details = {
        'abstract': parse_abstract(article_soup=article_soup),
        'authors': parse_authors(article_soup=article_soup),
        'title': parse_title(article_soup=article_soup),
        'doiUrl': parse_doi_url(article_soup=article_soup),
        'volume': article_url.split('/')[5],
        'issue': article_url.split('/')[6],
        'hyperlink': article_url,
        'journal': parse_journal(article_soup=article_soup),
        'keywords': parse_metadata(article_soup=article_soup)
    }
    return article_details


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
    article_details = []
    issues_archive = parse_issues_archive()
    for volume in issues_archive:
        issue_list = parse_issues_list(year_url=volume)
        for issue in issue_list:
            article_list = get_article_list(issue_url=issue)
            for article in article_list:
                article_details.append(parse_article_details(
                    article_url=article))
