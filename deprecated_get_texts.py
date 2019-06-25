'''
get_texts.py
Created by Oliver Calder, 24 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

This script takes the list of play codes (as provided at https://www.folgerdigitaltexts.org/api)
and scrapes the character list for each play from the site, in the form of URLs for each
character's individual text.

Then, the script pulls the text for each character from https://www.folgerdigitaltexts.org/{play_code}/charText/{character_code}.html
and processes it, extracting the text in lower case, free of punctuation, in a single string.

Uses the requests and bs4 (BeautifulSoup 4) libraries for pulling raw html strings and processing them, respectively.


Script can be run without arguments:
    python3 get_texts.py
in order to get texts for every character of every play.

Alternatively, a single character may be specified using the character code:
    python3 get_texts.py -c Mac_Macbeth
'''

help_string = '''
Command line options for get_texts.py:

    -h  help with possible arguments
    -c [char_code]  gets text only for specified character
    -p [play_code]  gets texts for characters only in specified play
    -ec [char_code]  excludes specified character
    -ep [play_code]  excludes specified play
    
    Future options (not yet implemented)
    -r  preserve raw text with punctuation and extra spacing
    -v  prints output to console as string
    -ws [path/to/filename]   write output to file as string
    -wj [path/to/filename]   write output to file as json

Example:
    python3 get_texts.py -v -c Mac_Macbeth -p Ham -wj my_text.json

- gets the text for the character Macbeth and for every character in Hamlet
- parses that text into letters only (by default, through omission of -r)
- formats the each character and the respective text into a dictionary object in JSON
- writes the JSON to a file specified after the -w argument, in this case my_text.json
- prints the JSON to the console
'''

import sys
import requests
import bs4

play_codes = {'AWW', 'Ant', 'AYL', 'Err', 'Cor', 'Cym', 'Ham', '1H4', '2H4', 'H5',
        '1H6', '2H6', '3H6', 'H8', 'JC', 'Jn', 'Lr', 'LLL', 'Mac', 'MM', 'MV', 'Wiv',
        'MND', 'Ado', 'Oth', 'Per', 'R2', 'R3', 'Rom', 'Shr', 'Tmp', 'Tim', 'Tit',
        'Tro', 'TN', 'TGV', 'TNK', 'WT'}

def get_chars_for_play(play_code, min_words=0):
    # TODO: Implement minimim word count cutoff for characters
    r = requests.get('https://www.folgerdigitaltexts.org/{0}/charText/'.format(play_code))
    raw_html = r.text
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    chars = set([])
    for link in soup.find_all('a'):
        char_code = link.get('href')
        chars.add(char_code)
    return chars

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

def main(chars=[], plays=[], raw=False, verbose=False, write=False, out='', string=False, dictionary=False, json=False):
    char_codes = set(chars)
    if chars = [] and plays = []:
        plays = play_codes
    else:
        plays = set(plays)
    for play in plays:
        char_codes.add(char for char in get_chars_for_play(play))
    text_dict = {}
    for char_code in char_codes:
        text = get_raw_text(char_code)
        if raw == False:
            text = simplify_text(text)


if __name__ == '__main__':
    char_code = []
    play_code = []
    r = False
    v = False
    w = False
    o = ''
    s = False
    d = False
    j = False

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-h':
            print(help_string)
            quit()
        elif sys.argv[i] == '-c':
            j = i + 1
            while j < len(sys.argv) and sys.argv[j][0] != '-':
                char_code.append(sys.argv[j])
                j += 1
        elif sys.argv[i] == '-p':
            j = i + 1
            while j < len(sys.argv) and sys.argv[j][0] != '-':
                play_code.append(sys.argv[j])
                j += 1
        elif sys.argv[i] == '-r':
            r = True
        elif sys.argv[i] == '-v':
            v = True
        elif sys.argv[i] == '-w':
            w = True
            o = sys.argv[i+1]
        elif sys.argv[i] == '-s':
            s = True
            d = False
            j = False
        elif sys.argv[i] == '-d':
            s = False
            d = True
            j = False
        elif sys.argv[i] == '-j':
            s = False
            d = False
            j = True
    main(chars=char_code, plays=play_code, raw=r, verbose=v, write=w, out=o, string=s, dictionary=d, json=j)

