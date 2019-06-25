'''
get_character_text.py
Created by Oliver Calder, 24 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

This script pulls text for a single character from https://www.folgerdigitaltexts.org/{play_code}/charText/{character_code}.html
Uses requests and bs4 libraries for pulling raw html and processing it, respectively.
'''

import sys
import requests
import bs4

def get_raw_text(char_code):
    play_code = char_code.split('_')[0]
    # char_code looks something like "Mac_Macbeth" (without the double quotes)
    # play_code thus looks something like "Mac" (without the double quotes)
    r = requests.get('https://www.folgerdigitaltexts.org/{0}/charText/{1}.html'.format(play_code, char_code))
    raw_html = r.text
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    text = soup.get_text()
    return text

def simplify_text(text):
    clean_text = ''
    text.replace('—', ' ')
    text.replace('-', ' ')
    for line in text.split('\n'):
        if line != '':
            words = line.split(' ')
            clean_line = ''
            for word in words:
                if word != '':
                    clean_word = ''
                    for char in word:
                        if char.isalpha() or char == "'":
                            clean_word = clean_word + char.lower()
                    clean_line = clean_line + clean_word + ' '
            clean_text = clean_text + clean_line
    return clean_text.rstrip()

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 {} char_code'.format(sys.argv[0]))
        quit()
    else:
        raw_text = get_raw_text(sys.argv[1])
        print('#####raw text:#####')
        print(raw_text)
        clean_text = simplify_text(raw_text)
        print('#####clean text:#####')
        print(clean_text)

if __name__ == '__main__':
    main()
