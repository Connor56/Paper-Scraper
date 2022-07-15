'''
Name:
    Find Magnetics Researchers
Description:
    Simple script using the paper scraper API which downloads information from
    the given authors google scholar user pages. Using this information builds
    a database which indicates the most preferred places for publication for
    the given set of authors.
'''

import paper_scraper
import pandas as pd

researcher_user_codes = [
    ['nnKCzT8AAAAJ', 'Gino Hrkac'], ['XehtsQEAAAAJ', 'Thomas Schrefl'],
    ['SEl9fCoAAAAJ', 'Anna Baldycheva'], ['IMtVJ68AAAAJ', 'Oliver Gutfleisch'],
    ['QIY9cIcAAAAJ', 'Michael Winklhofer'],
    ['fmSV_RYAAAAJ', 'Gergely Zimanyi'], ['2oz7oosAAAAJ', 'Roy Chantrell'],
    ['BlJD3A4AAAAJ', 'Richard Evans'], ['6l_xkvMAAAAJ', 'Paul Keatley'],
    ['4NDvzqoAAAAJ', 'Alexander Kovacs'], ['IcUq2-wAAAAJ', 'Kazuhiro Hono'],
    ['nC95Zy0AAAAJ', 'David Srolovitz'], ['Mue87hsAAAAJ', 'Frank Jensen'],
    ['_ZwalIwAAAAJ', 'Daan Frenkel']]

for researcher in researcher_user_codes:
    researcher[0] = (
        f"https://scholar.google.com/citations?hl=en&user={researcher[0]}"
        "&cstart=0&pagesize=50")
#researcher_user_codes = [tuple(x) for x in researcher_user_codes]
#author_data = make_paper_database('26-1-2022_magnetics_researchers')
author_data = pd.read_csv(
    "26-1-2022_magnetics_researchers/26-1-2022_magnetics_researchers"
    "-author_data")
keywords = ['perpendicular', 'magnet', 'microstructure', 'structure',
            'recording', 'Nd', 'Fe', 'crystal', 'grain', 'micromagnetic',
            'Co', 'Cu', 'finite element', 'coercivity', 'exchange spring',
            'ferromagnetic', 'simulations', 'ferrimagnetic', 'atomistic',
            'first-principles', 'first principles', 'materials', 'atomic',
            'structural', 'molecular dynamics', 'ordering', 'bcc', 'fcc',
            'particle', 'atom', 'nucleation']
print(' '.join(keywords))

author_data = paper_scraper.filter_papers(author_data, keywords)
unique_journals = paper_scraper.get_unique_journals(author_data)
journal_publication_data = paper_scraper.get_journal_publication_data(author_data, unique_journals)
with pd.option_context('display.max_rows', None, 'display.max_colwidth', None):
    print(journal_publication_data.sort_values(by=['Number of Papers', 'Total Citations'], ascending=False))
