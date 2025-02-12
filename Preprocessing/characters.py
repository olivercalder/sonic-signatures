'''
File: characters.py
Created: Oliver Calder, 25 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a set containing all the character codes for the play or plays specified.
If no play is specified, it returns character codes for each character from every play.

The script can nest characters by play by using the -n argument. This causes a dictionary to be
returned with a key for each play mapped to a set containing all the character codes for that
play. This takes the form:
{'Mac':{'Mac_Macbeth', 'Mac_Macduff', ...}, 'Ham':{'Ham_Hamlet', ...}}

Any play or character which is excluded using -ep or -ec, respectively, will not be included
in the set of returned character codes.
'''

help_string = '''
Help for characters.py:
Returns a set containing all the character codes for the play or plays specified.
If no play is specified, it returns character codes for each character from every play.

Command Line Arguments:
-h               Prints help text
-p [play_code]   Specifies one or more plays (separated by spaces) for which to return codes
-c [char_code]   Specifies one or more characters to be included, in addition to given plays
-ep [play_code]  Specifies one or more plays whose characters will be excluded
-ec [char_code]  Specifies one or more characters to be excluded from the set
-eo              Exclude characters with role of "other"
-n               Returns a dictionary of characters nested by play, rather than a set of all
-s               Silent: Does not print to console
-wt              Writes the output to file as plain text
-wj              Writes the output to file as json
-t [title]       Title: Indicates name of specific run, used in filenames
-d [path/to/dir] Specifies directory in which to write output files
-m [min_words]   Specifies the minimum words necessary for a character to be included
'''

import sys
import os
import requests
import bs4
import csv
import json


plays = {'AWW', 'Ant', 'AYL', 'Err', 'Cor', 'Cym', 'Ham', '1H4', '2H4', 'H5',
        '1H6', '2H6', '3H6', 'H8', 'JC', 'Jn', 'Lr', 'LLL', 'Mac', 'MM', 'MV', 'Wiv',
        'MND', 'Ado', 'Oth', 'Per', 'R2', 'R3', 'Rom', 'Shr', 'Tmp', 'Tim', 'Tit',
        'Tro', 'TN', 'TGV', 'TNK', 'WT'}


def convert_set_to_dict(char_set):
    char_dict = {}
    for char in char_set:
        play = char.split('_')[0]
        if play not in char_dict:
            char_dict[play] = set([])
        char_dict[play].add(char)
    return char_dict


def convert_dict_to_set(char_dict):
    char_set = set([])
    for play in char_dict:
        for char in char_dict[play]:
            char_set.add(char)
    return char_set


def convert_dict_to_json(char_dict):
    char_json = {}
    for play in char_dict:
        char_json[play] = sorted(char_dict[play])
    return char_json


def convert_json_to_dict(char_json):
    char_dict = {}
    for play in char_json:
        char_dict[play] = set(char_json[play])
    return char_dict


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_chars(char_set):
    if type(char_set) == type({}):
        char_set = convert_dict_to_set(char_set)
    char_set = set(char_set)
    for char in char_set:
        print(char)


def write_text(char_set, title='', directory=''):
    if type(char_set) == type({}):
        char_set = convert_dict_to_set(char_set)
    char_set = set(char_set)
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'characters.txt'
    with open(filename, 'w') as out_text:
        char_list = sorted(char_set)
        for char in char_list:
            print(char, file=out_text)


def write_json(char_dict, title='', directory=''):
    if type(char_dict) != type({}):
        char_dict = convert_set_to_dict(set(char_dict))
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'characters.json'
    with open(filename, 'w') as out_json:
        char_json = convert_dict_to_json(char_dict)
        json.dump(char_json, out_json)


def get_char_dict(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, min_words=0):
    if type(char_codes) == type(''):
        char_codes = set([char_codes])
    char_set = set(char_codes)
    if type(play_codes) == type(''):
        play_codes = set([play_codes])
    elif play_codes <= set([]) and char_codes <= set([]):
        play_codes = set(plays)

    for play in play_codes:
        r = requests.get('https://www.folgerdigitaltexts.org/{0}/charText/'.format(play))
        raw_html = r.text
        soup = bs4.BeautifulSoup(raw_html, 'html.parser')

        divs = soup.find_all('div')
        i = 2   # First word count appears at index 2, first character name at index 3
        while i + 1 < len(divs):
            word_count = int(divs[i].get_text())
            link = divs[i+1].a
            suffix = link.get('href')
            char_code = suffix.split('.html')[0]
            if word_count >= min_words:
                char_set.add(char_code)
            i += 2

    if type(ep) == type(''):
        ep = set([ep])
    orig_set = char_set.copy()
    for char in orig_set:
        if char.split('_')[0] in ep:
            char_set.discard(char)
    if type(ec) == type(''):
        ec = set([ec])
    for character in ec:
        char_set.discard(character)
    if eo:
        with open('../Reference/characteristics.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['role'] == 'other':
                    char_set.discard(row['character'])

    if nested:
        return convert_set_to_dict(char_set)
    else:
        return char_set


def build_char_dict(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', min_words=0):
    char_dict = get_char_dict(play_codes, char_codes, ep, ec, eo, nested, min_words)
    if not silent:
        print_chars(char_dict)
    if wt == True:
        write_text(char_dict, title, directory)
    if wj == True:
        write_json(char_dict, title, directory)
    return char_dict


def main(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', min_words=0):
    char_dict = build_char_dict(play_codes, char_codes, ep, ec, eo, nested, silent, wt, wj, title, directory, min_words)
    return char_dict


if __name__ == '__main__':
    play_codes = set([])
    char_codes = set([])
    ep = set([])
    ec = set([])
    eo = False
    nested = False
    silent = False
    wt = False
    wj = False
    title = ''
    directory = ''
    min_words = 0

    i = 0
    while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
        i += 1
        play_codes.add(sys.argv[i])

    i += 1
    unrecognized = []
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
        elif sys.argv[i] == '-eo':
            eo = True
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
        main(play_codes, char_codes, ep, ec, eo, nested, silent, wt, wj, title, directory, min_words)
