'''
File: get_characters.py
Created: Oliver Calder, 25 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a set containing all the character codes for the play or plays specified.
If no play is specified, it returns character codes for each character from every play.

The script can sort characters by play by using the -d argument. This causes a dictionary to be
returned with a key for each play mapped to a set containing all the character codes for that
play. This takes the form:
{'Mac':{'Mac_Macbeth', 'Mac_Macduff', ...}, 'Ham':{'Ham_Hamlet', ...}}

Any play or character which is excluded using -ep or -ec, respectively, will not be included
in the set of returned character codes.
'''

help_string = '''
Help for get_characters.py:
Returns a set containing all the character codes for the play or plays specified.
If no play is specified, it returns character codes for each character from every play.

Command Line Arguments:
-h               Prints help text
-p [play_code]   Specifies one or more plays (separated by spaces) for which to return codes
-ep [play_code]  Specifies one or more plays which whose characters will be omitted
-ec [char_code]  Specifies one or more characters to be omitted from the set
-d               Returns a dictionary of characters sorted by play, rather than a set of all
-s               Silent: Does not print to console
-wt [path/to/filename]  Writes the output to the specified file as plain text
-wj [path/to/filename]  Writes the output to the specified file as json
'''

import os
import sys
import requests
import bs4
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
        for char in play:
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


def get_char_set(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), min_words=0):
    # TODO: implement minimum word count cutoff for characters

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
        for link in soup.find_all('a'):
            suffix = link.get('href')
            char_code = suffix.split('.html')[0]
            char_set.add(char_code)

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

    return char_set


def get_char_dict(play_codes=set([]), char_codes=set([]), ec=set([]), ep=set([]), min_words=0):
    char_set = get_char_set(play_codes, char_codes, ep, ec, min_words=0)
    char_dict = convert_set_to_dict(char_set)
    return char_dict


def main(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), dictionary=False, silent=False, wt=False, wj=False):
    char_set = get_char_set(play_codes, char_codes, ep, ec)
    char_dict = convert_set_to_dict(char_set)

    if wt != False:
        os.system('touch {}'.format(wt))
        out_text = open(wt, 'w')
    if wj != False:
        os.system('touch {}'.format(wj))
        out_json = open(wj, 'w')

    if not s or wt != False: #Ugly code, but slightly more efficient to not iterate if unneeded
        for char in char_set:
            if not s:
                print(char)
            if wt != False:
                print(char, file=out_text) 

    if wj != False:
        char_json = convert_dict_to_json(char_dict)
        json.dump(char_json, out_json)

    if wt != False:
        out_text.close()
    if wj != False:
        out_json.close()

    if not d:
        return char_set
    elif d:
        return char_dict


if __name__ == '__main__':
    play_codes = set([])
    char_codes = set([])
    ep = set([])
    ec = set([])
    d = False
    s = False
    wt = False
    wj = False

    i = 0
    while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
        i += 1
        play_codes.add(sys.argv[i])

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-h':
            print(help_string)
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
        elif sys.argv[i] == '-d':
            d = True
        elif sys.argv[i] == '-s':
            s = True
        elif sys.argv[i] == '-wt':
            if i == len(sys.argv)-1 or sys.argv[i+1][0] == '-':
                wt = 'characters.txt'
            elif i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                wt = sys.argv[i]
        elif sys.argv[i] == '-wj':
            if i == len(sys.argv)-1 or sys.argv[i+1][0] == '-':
                wj = 'characters.json'
            elif i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                wj = sys.argv[i]
    main(play_codes, char_codes, ep, ec, d, s, wt, wj)
