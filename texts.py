'''
File: texts.py
Created: Oliver Calder, 25 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a dictionary containing each character code paired to that character's
text. If one or more characters or plays is specified, the dictionary will be built using only
the codes and text for those characters. Otherwise, the script will build a dictionary
containing every character by default.

The script can sort characters by play using the -n argument. This causes a dictionary to be returned with a key for each play mapped to a dictionary where each character code is mapped to
the text for that character. This takes the form:
{'Mac':{'Mac_Macbeth':text, 'Mac_Macduff':text, ...}, 'Ham':{'Ham_Hamlet':text, ...}}

Any play or character which is excluded using -ep or -ec, respectively, will not be included in
the dictionary.
'''


help_string = '''
Help for texts.py:
Returns a dictionary containing the specified character codes mapped to their respective texts.
If no character or play codes are specified, it returns a dictionary containing each
character from every play.

Command Line Arguments:
-h               Prints help text
-p [play_code]   Specifies one or more plays (separated by spaces) for which to include characters
-c [char_code]   Specifies one or more characters to be included in the dictionary
-ep [play_code]  Specifies one or more plays whose characters will be excluded
-ec [char_code]  Specifies one or more characters to be excluded from the dictionary
-n               Returns a dictionary of characters nested by play, rather than intermixed
-s               Silent: Does not print to console
-wt              Writes the output to file as plain text
-wj              Writes the output to file as json
-t [title]       Title: Indicates name of specific run, used in filenames
-d [path/to/dir] Specifies the directory in which to write output files
-R               Recursive cascade: Preserve write preferences for all scripts
-r               Preserve raw text (ie. capitalization, punctuation)
-m [min_words]   Specifies the minimum words necessary for a character to be included
'''


import characters
import sys
import os
import requests
import bs4
import json


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
        for char in text_dict_nested[play]:
            text_dict[char] = text_dict_nested[play][char]
    return text_dict


def is_nested(text_dict):
    nested = False
    for key in text_dict: # Way to check arbitrary value in dictionary
        value = text_dict[key]
        if type(value) == type({}):
            nested = True
        break
    return nested


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_texts(text_dict):
    if is_nested(text_dict):
        text_dict = unnest_dict(text_dict)
    for char in text_dict:
        print()
        print(char)
        print(text_dict[char])


def write_text(text_dict, title='', directory=''):
    if is_nested(text_dict):
        text_dict = unnest_dict(text_dict)
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    for char in text_dict:
        filename = directory + title + 'text_' + char + '.txt'
        out_text = open(filename, 'w')
        print(text_dict[char], file=out_text)
        out_text.close()


def write_json(text_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'texts.json'
    out_json = open(filename, 'w')
    json.dump(text_dict, out_json)
    out_json.close()


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
    text = text.replace('—', ' ')
    text = text.replace('-', ' ')
    text = text.replace("’", "'")
    for line in text.split('\n'):
        if line != '' and line != ' ':
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
    return clean_text.rstrip().lstrip()


def get_text_dict(char_codes, nested=False, raw=False):
    if type(char_codes) == type({}):
        char_set = characters.convert_dict_to_set(char_codes)
    else:
        char_set = set(char_codes)
    text_dict = {}
    for char in char_set:
        text = get_char_raw_text(char)
        if not raw:
            text = simplify_text(text)
        text_dict[char] = text
    if nested:
        text_dict = nest_dict_by_play(text_dict)
    return text_dict


def build_text_dict(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, raw=False, min_words=0):
    char_codes = characters.build_char_dict(play_codes, char_codes, ep, ec, nested, silent, wt and cascade, wj and cascade, title, directory, min_words)
    text_dict = get_text_dict(char_codes, nested, raw)
    if not silent:
        print_texts(text_dict)
    if wt == True:
        write_text(text_dict, title, directory)
    if wj == True:
        write_json(text_dict, title, directory)
    return text_dict


def main(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, raw=False, min_words=0):
    text_dict = build_text_dict(play_codes, char_codes, ep, ec, nested, silent, wt, wj, title, directory, cascade, raw, min_words)
    return text_dict


if __name__ == '__main__':
    play_codes = set([])
    char_codes = set([])
    ep = set([])
    ec = set([])
    nested = False
    silent = False
    wt = False
    wj = False
    title = ''
    directory = ''
    cascade = False
    raw = False
    min_words = 0

    i = 0
    while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
        i += 1
        play_codes.add(sys.argv[i])

    unrecognized = []
    i += 1
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print(help_string)
            quit()
        elif sys.argv[i] == '-p':
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                play_codes.add(sys.argv[i])
        elif sys.argv[i] == '-c':
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                char_codes.add(sys.argv[i])
        elif sys.argv[i] == '-ep':
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                ep.add(sys.argv[i])
        elif sys.argv[i] == '-ec':
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                ec.add(sys.argv[i])
        elif sys.argv[i] == '-n':
            nested = True
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
        elif sys.argv[i] == '-wj':
            wj = True
        elif sys.argv[i] == '-t':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                title = sys.argv[i]
            else:
                unrecognized.append('-t: Missing Specifier')
        elif sys.argv[i] == '-d':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                directory = sys.argv[i]
            else:
                unrecognized.append('-d: Missing Specifier')
        elif sys.argv[i] == '-R':
            cascade = True
        elif sys.argv[i] == '-r':
            raw = True
        elif sys.argv[i] == '-m':
            if i+1 == len(sys.argv) or sys.argv[i+1][0] == '-':
                unrecognized.append('-m: Missing Specifier')
            elif i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                min_words = int(sys.argv[i])
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if len(unrecognized) > 0:
        print('ERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
    else:
        main(play_codes, char_codes, ep, ec, nested, silent, wt, wj, title, directory, cascade, raw, min_words)
