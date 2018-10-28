
import json
import pickle
import os.path



# Need the paths to base and data directories
BASE_PATH = '/home/owen/Code/FinHisDB/'
DATA_PATH = BASE_PATH + 'src/python/article-extraction/journals/data'


def read_university_domains():
    domains = BASE_PATH + 'src/world_universities_domains.json'
    with open(domains) as k:
        university_domains = json.load(k)
    return university_domains


def load_pickle(journal):
    data_file = '{}/{}.pickle'.format(
        DATA_PATH, journal)
    if os.path.isfile(data_file):
        with open(data_file, 'rb') as f:
            return pickle.load(f)
    else:
        return []


## EXTRACTING AUTHOR AND EMAIL

# Elsivier
# This typically has a nested {author: , email: } structure

elsivier_journals = [
    "journal-of-banking-and-finance",
    "international-review-of-economics-and-finance",
    "journal-of-financial-economics",
    "journal-of-international-economics"
]

cambridge_journals = [
    "financial-history-review",
    "business-history-review"
]


def extract_elsivier(journal):
    author_emails = []
    articles = load_pickle(journal=journal)
    for article in articles:
        for author in article['authors']:
            if author['email'] is not None:
                author_emails.append({
                    'author': author['authorName'],
                    'email': author['email']
                })
    return author_emails


def extract_cambridge(journal):
    author_emails = []
    articles = load_pickle(journal=journal)
    for article in articles:
        if article['email'] is not None:
            author_emails.append({
                'author': article['authors'],
                'email': article['email'][0]
            })
    return author_emails
    

author_emails = []
for journal in elsivier_journals:
    author_emails += extract_elsivier(journal=journal)
    





def save_json(article_list, journal):
    with open(DATA_PATH + "/json/" + journal + ".json", 'w') as outfile:
        json.dump(article_list, outfile, indent=4)
        
        


# Extract only emails from certain countries
countries = [
    'united kingdom',
    'italy',
    'germany',
    'poland',
    'france',
    'netherlands',
    'ireland'
]


usable_domains = []
subset_universities = []
university_domains = read_university_domains()
for university in university_domains:
    university_country = university['country'].encode('utf-8')
    if university_country.lower() in countries:
        subset_universities.append(university)
        usable_domains += university['domains']    


subset_authors = []
for author in author_emails:
    email_domain = author['email'].split('@')[1]
    if email_domain in usable_domains:
        subset_authors.append(author)





