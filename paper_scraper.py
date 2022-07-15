'''
Name:
    Paper Scraper
Description:
    Contains functions that allow you to scrape research information off the
    internet.

    Currently Covers:
    1. Scraping the google scholar user pages of a group of researchers and
       analysing the patterns in their publications.
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import random
import numpy as np
import time
from matplotlib import pyplot as plt
import cProfile, pstats, io
from pstats import SortKey


def html_download(addresses, folder_name):
    '''
    Downloads the html code found at the given addresses and stores them in
    folder. Addresses should have the format of (Url, Name).
    '''
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    for address in addresses:
        wait_time = get_wait_time()
        print('Author:', address[1], 'Wait Time:', wait_time)
        time.sleep(wait_time)
        response = requests.get(address[0])
        file_name = address[1].replace(' ', '_')+'.html'
        with open(folder_name+'/'+file_name, 'w') as f:
            f.write(response.text)


def make_paper_database(folder):
    '''
    Takes in a folder of Google Scholar User pages as html files and scrapes
    their publication information. Returns this information as a pandas
    dataframe.
    '''
    authors = [x for x in os.listdir(folder) if not folder in x]
    author_data = []
    for author in authors:
        with open(folder+'/'+author, 'r') as f:
            html_code = f.read()
            paper_data = get_researcher_data(html_code)
            author_data.append(paper_data)
    author_data = pd.concat(author_data, ignore_index=True)
    author_data.to_csv(folder+f"/{folder}-author_data")
    return author_data


def get_researcher_data(html_code):
    '''
    Takes in the html code of a researcher's google scholar page and scrapes
    the data pertaining to each paper they have been listed as an author of.
    This information is then placed into a pandas dataframe and returned.
    '''
    soup = BeautifulSoup(html_code, 'html.parser')
    researcher_scraped = soup.find_all('div', attrs={'id': 'gsc_prf_in'})
    researcher_scraped = researcher_scraped[0].text
    paper_rows = soup.find_all('tr', attrs={'class': 'gsc_a_tr'})
    paper_data = get_row_data(paper_rows, researcher_scraped)
    return paper_data


def get_row_data(paper_rows, researcher_scraped):
    '''
    Takes in all the rows from the html document, each of which represent a
    paper (or publication). Collects the data from each row pertaining to its
    specific paper. Data collected: Title, Journal, Authors, Citations, and
    Year of Publication. Returns this information as a pandas DataFrame.
    '''
    title_list = []
    journal_list = []
    authors_list = []
    citations_list = []
    year_list = []
    for row in paper_rows:
        title_authors_journal = row.contents[0]
        title = title_authors_journal.contents[0].text.strip()
        title_list.append(title)
        authors = title_authors_journal.contents[1].text
        authors = [x.strip() for x in authors.split(',') if not '...' in x]
        authors_list.append(authors)
        journal = title_authors_journal.contents[2].text
        journal_match = re.compile(r"([^\d(,]+)")
        journal = journal_match.match(journal)
        if journal == None:
            journal = ''
        else:
            journal = journal.group().strip()
        journal_list.append(journal)
        citations = row.contents[1].text.replace('*', '')
        citations_list.append(citations)
        year = row.contents[2].text
        year_list.append(year)
    paper_data = pd.DataFrame(
        {'Title': title_list,
         'Journal': journal_list,
         'Authors': authors_list,
         'Citations': citations_list,
         'Year': year_list,
         'Researcher Scraped': [researcher_scraped]*len(year_list)})
    return paper_data


def get_wait_time():
    '''
    Calculates the time to wait inbetween requests to the google scholar web
    page. Attempts to make it appear like human behaviour by behaving semi
    randomly, but still putting in requests every 20 seconds or so.
    '''
    wait_time = random.gauss(10, 2)
    addition = random.random()*20
    random_integers = [random.randint(1, 10) for x in range(100)]
    random_integer = np.random.choice(random_integers)
    round_to = random.randrange(1, 10, 1)
    wait_time = np.abs(np.round(wait_time+addition+random_integer, round_to))
    return wait_time


def filter_papers(author_data, keywords, show_removed=False):
    '''
    Filters out papers that don't contain any of the keywords provided in their
    title. To show the papers removed by this filter set show_removed to True.
    Keeping track of what is removed and what isn't can help you create your
    keyword list.
    '''
    paper_titles = author_data['Title'].str.lower()
    title_mask = [
        [True if x in title else False for x in keywords]
        for title in paper_titles]
    title_mask = [True if True in x else False for x in title_mask]
    if show_removed:
        print('Total Papers:', author_data.shape[0],
              'Removed Papers:', np.sum(np.invert(title_mask)),
              'New Total:', np.sum(title_mask))
        with pd.option_context(
                'display.max_rows', None, 'display.max_colwidth', None):
            print(author_data[np.invert(title_mask)]['Title'])
    return author_data[title_mask]


def count_upper(word):
    '''
    Counts the number of times an uppercase letter occurs within a word.
    '''
    return len(re.findall(re.compile(r"[A-Z]"), word))


def get_unique_journals(author_data):
    '''
    Takes in author data gets a list of all the Journals those authors have
    published in where each entry is the list is a unique journal. The
    capitalisation of journal names isn't always consistent, when a choice must
    be made on which capitalisation style to use, the style with greater
    capitalisation is chosen.
    '''
    journals = author_data['Journal']
    unique_journals = journals.unique().astype(str)
    mask = []
    for journal in unique_journals:
        duplicates = unique_journals[
            np.char.lower(unique_journals) == journal.lower()]
        if len(duplicates) == 1:
            mask.append(duplicates[0])
            continue
        upper_case = [count_upper(x) for x in duplicates]
        mask.append(duplicates[np.argmax(upper_case)])
    return unique_journals[[x in mask for x in unique_journals]]


def get_journal_publication_data(author_data, journals):
    '''
    Finds the number of times a collection of authors have published in a list
    of provided journals. Produces a pandas DataFrame of this information, so
    that trends in publication can be analysed.
    '''
    total_citations = []
    number_of_papers = []
    citations_per_paper = []
    for name in journals:
        citations = author_data[
            author_data['Journal'].str.lower() == name.lower()]
        summed_citations = citations['Citations'].sum()
        total_citations.append(summed_citations)
        number = citations.shape[0]
        number_of_papers.append(number)
        citations_per_paper.append(summed_citations/number)
    journal_publication_data = pd.DataFrame({
        'Journal': journals,
        'Total Citations': total_citations,
        'Number of Papers': number_of_papers,
        'Citations Per Paper': citations_per_paper})
    return journal_publication_data
