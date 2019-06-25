'''
File: get_texts.py
Created: Oliver Calder, 25 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgersdigitaltexts.org/api

This script returns a dictionary containing each character code paired to that character's
text. If one or more characters or plays is specified, the dictionary will be built using only
the codes and text for those characters. Otherwise, the script will build a dictionary
containing every character by default.

The script can sort characters by play using the -d argument. This causes a dictionary to be returned with a key for each play mapped to a dictionary where each character code is mapped to
the text for that character. This takes the form:
{'Mac':{'Mac_Macbeth':text, 'Mac_Macduff':text, ...}, 'Ham':{'Ham_Hamlet':text, ...}}

Any character or play which is excluded using -ec or -ep, respectively, will not be included in
the dictionary.
'''


import get_characters as gc


def nest_dict_by_play(text_dict):
    text_dict_nested = {}
    for char in text_dict:
        play = char.split('_')[0]
        if play not in text_dict_nested:
            text_dict_nested[play] = {}
        text_dict_nested[play][char] = text_dict[char]
    return text_dict_nested


def unnest_dict(text_dict_nested):
    text_dict = {}
    for play in text_dict_nested:
        for char in play:
            text_dict[char] = text_dict_nested[play][char]
    return text_dict


def get_char_raw_text(char_code):
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


def get_text_dict(char_codes, raw=False):
    if type(char_codes) == type({}):
        char_set = gc.convert_dict_to_set(char_codes)
    else:
        char_set = set(char_codes)
    text_dict = {}
    for char in char_set:
        text = get_char_raw_text(char)
        if not raw:
            text = simplify_text(text)
        text_dict[char] = text
    return text_dict


def get_text_dict_nested(char_codes, raw=False):
    if type(char_codes) != type({}):
        char_dict = gc.convert_set_to_dict(set(char_codes))
    text_dict_nested = {}
    for play in char_dict:
        if play not in text_dict_nested:
            text_dict_nested[play] = {}
        for char in play:
            text = get_char_raw_text(char)
            if not raw:
                text = simplify_text(text)
            text_dict_nested[play][char] = text
    return text_dict_nested


def main(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, raw=False):
    if nested:
        char_codes = gc.get_char_dict(play_codes, char_codes, ep, ec)
        text_dict = get_text_dict_nested(char_codes, raw)
    elif not nested:
        char_codes = gc.get_char_set(play_codes, char_codes, ep, ec)
        text_dict = get_text_dict(char_codes, raw)

