'''
get_char_urls.py
Created by Oliver Calder, 24 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

This script scrapes the URLs for the text of each character from https://www.folgerdigitaltexts.org/{play_code}/charText/
Uses requests and bs4 libraries for pulling raw html and processing it, respectively.

TODO: Implement minimum word count cutoff for characters
'''

import sys
import requests
import bs4

def get_urls_for_play(play_code, min_words=0):
    # TODO: Implement minimim word count cutoff for characters
    r = requests.get('https://www.folgerdigitaltexts.org/{0}/charText/'.format(play_code))
    raw_html = r.text
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    urls = []
    for link in soup.find_all('a'):
        suffix = link.get('href')
        urls.append('https://www.folgerdigitaltexts.org/{0}/charText/{1}'.format(play_code, suffix))
    return urls

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 {} play_code'.format(sys.argv[0]))
        quit()
    else:
        urls = get_urls_for_play(sys.argv[1])
        print(urls)

if __name__ == '__main__':
    main()
