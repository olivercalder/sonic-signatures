'''
File: phonemes.py
Created: Oliver Calder, 26 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a dictionary containing each character code paired to that character's
text in the form of a list of phonemes. If one or more characters or plays is specified, the
dictionary will be built using only the codes and phonemes for those characters. Otherwise,
the script will build a dictionary containing every character by default.

The script can sort characters by play using the -n argument. This causes a dictionary to be
returned with a key for each play mapped to a dictionary where each character code is mapped to
the phoneme list for that character. This takes the form:
{'Mac':{'Mac_Macbeth':phonemes, 'Mac_Macduff':phonemes, ...}, 'Ham':{'Ham_Hamlet':phonemes, ...}}

Any play or character which is excluded using -ep or -ec, respectively, will not be included in
the dictionary.
'''

help_string = '''
Help for phonemes.py:
Returns a dictionary containing the specified character codes mapped to their respective
phonemes in a list. If no character or play codes are specified, it returns a dictionary
containing each character from every play.

Command Line Arguments:
-h               Prints help text
-l [filename]    Specifies one or more json files from which to load existing text data
-p [play_code]   Specifies one or more plays for which to include characters
-c [char_code]   Specifies one or more characters to be included in the dictionary
-ep [play_code]  Specifies one or more plays whose characters will be excluded
-ec [char_code]  Specifies one or more characters to be excluded from the dictionary
-eo              Exclude characters with role of "other"
-n               Returns a dictionary of characters nested by play, rather than intermixed
-s               Silent: Does not print to console
-wt              Writes the output to file as plain text
-wj              Writes the output to file as json
-t [title]       Title: Indicates name of specific run, used in filenames
-d [path/to/dir] Specifies the directory in which to write output files
-R               Recursive cascade: Preserve write preferences for all scripts
-u               Return list of unknown words instead of phoneme list
-v               Vowels: Return vowels only
-e               Preserve emphasis marking in phonemes
-r               Preserve raw text (ie. capitalization, punctuation)
-m [min_words]   Specifies the minimum words necessary for a character to be included
'''


import texts
import sys
import os
import json
import nltk
# nltk.download('cmudict')
# OR
# $ python3 -m nltk.downloader [-d /usr/share/nltk_data] cmudict


vowels = {'A', 'E', 'I', 'O', 'U'}


def nest_dict_by_play(phoneme_dict):
    phoneme_dict_nested = {}
    for char in phoneme_dict:
        play = char.split('_')[0]
        if play not in phoneme_dict_nested:
            phoneme_dict_nested[play] = {}
        phoneme_dict_nested[play][char] = phoneme_dict[char]
    return phoneme_dict_nested


def unnest_dict(phoneme_dict_nested):
    phoneme_dict = {}
    for play in phoneme_dict_nested:
        for char in phoneme_dict_nested[play]:
            phoneme_dict[char] = phoneme_dict_nested[play][char]
    return phoneme_dict


def is_nested(phoneme_dict):
    nested = False
    for key in phoneme_dict: # Way to check arbitrary value in dictionary
        value = phoneme_dict[key]
        if type(value) == type({}):
            nested = True
        break
    return nested


def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as json_in:
            return json.load(json_in)
    else:
        print("ERROR: File '{}' does not exist".format(filename))
        print('Exiting...')
        quit()


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_phonemes(phoneme_dict):
    if is_nested(phoneme_dict):
        phoneme_dict = unnest_dict(phoneme_dict)
    for char in phoneme_dict:
        print()
        print(char)
        print(phoneme_dict[char])


def write_text(phoneme_dict, title='', directory='', unknowns=False):
    if is_nested(phoneme_dict):
        phoneme_dict = unnest_dict(phoneme_dict)
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        title = title + 'unknowns_'
    else:
        title = title + 'phonemes_'
    for char in phoneme_dict:
        filename = directory + title + char + '.txt'
        out_text = open(filename, 'w')
        print(phoneme_dict[char], file=out_text)
        out_text.close()


def write_json(phoneme_dict, title='', directory='', unknowns=False):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        filename = directory + title + 'unknowns.json'
    else:
        filename = directory + title + 'phonemes.json'
    out_json = open(filename, 'w')
    json.dump(phoneme_dict, out_json)
    out_json.close()


def convert_text_to_phonemes(text, return_unknowns=False, vowels_only=False, preserve_emphasis=False):
    d = nltk.corpus.cmudict.dict()
    phonemes = []
    unknowns = []
    for w in text.split():
        word = w.lower()
        if word in d and not return_unknowns:
            word_phonemes = d[word][0]
            for phon in word_phonemes:
                if phon[0] in vowels or not vowels_only:
                    if phon[-1].isdigit() and not preserve_emphasis:
                        phonemes.append(phon[:-1])
                    else:
                        phonemes.append(phon)
        elif word not in d:
            unknowns.append(word)
    if return_unknowns:
        return unknowns
    else:
        return phonemes


def get_phoneme_dict(text_dict, nested=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False):
    if texts.is_nested(text_dict):
        text_dict = texts.unnest_dict(text_dict)
    phoneme_dict = {}
    for char in text_dict:
        phoneme_dict[char] = convert_text_to_phonemes(text_dict[char], return_unknowns, vowels_only, preserve_emphasis)
    if nested:
        phoneme_dict = nest_dict_by_play(phoneme_dict)
    return phoneme_dict


def build_phoneme_dict(load_json_filenames=set([]), play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):
    text_dict = {}
    for filename in load_json_filenames:
        new_dict = load_json(filename)
        if texts.is_nested(new_dict):
            new_dict = texts.unnest_dict(new_dict)
        text_dict.update(new_dict)
    for char in text_dict:
        ec.add(char)

    if play_codes or char_codes or not load_json_filenames:
        new_text_dict = texts.build_text_dict(play_codes, char_codes, ep, ec, eo, nested, silent, wt and cascade, wj and cascade, title, directory, cascade, raw, min_words)
        if nested:
            unnest_dict(new_text_dict)
        text_dict.update(new_text_dict)

    phoneme_dict = get_phoneme_dict(text_dict, nested, return_unknowns, vowels_only, preserve_emphasis)
    if not silent:
        print_phonemes(phoneme_dict)
    if wt == True:
        write_text(phoneme_dict, title, directory, unknowns=return_unknowns)
    if wj == True:
        write_json(phoneme_dict, title, directory, unknowns=return_unknowns)
    return phoneme_dict


def main(load_json_filenames=set([]), play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):
    return build_phoneme_dict(load_json_filenames, play_codes, char_codes, ep, ec, eo, nested, silent, wt, wj, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)


if __name__ == '__main__':
    load_json_filenames = set([])
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
    cascade = False
    return_unknowns = False
    vowels_only = False
    preserve_emphasis = False
    raw = False
    others = False
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
        elif sys.argv[i] == '-l':
            tmp = i
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                load_json_filenames.add(sys.argv[i])
            if i == tmp:
                unrecognized.append('-l: Missing Specifier')
        elif sys.argv[i] == '-p':
            tmp = i
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                play_codes.add(sys.argv[i])
            if i == tmp:
                unrecognized.append('-p: Missing Specifier')
        elif sys.argv[i] == '-c':
            tmp = i
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                char_codes.add(sys.argv[i])
            if i == tmp:
                unrecognized.append('-c: Missing Specifier')
        elif sys.argv[i] == '-ep':
            tmp = i
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                ep.add(sys.argv[i])
            if i == tmp:
                unrecognized.append('-ep: Missing Specifier')
        elif sys.argv[i] == '-ec':
            tmp = i
            while i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                ec.add(sys.argv[i])
            if i == tmp:
                unrecognized.append('-ec: Missing Specifier')
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
        elif sys.argv[i] == '-R':
            cascade = True
        elif sys.argv[i] == '-u':
            return_unknowns = True
        elif sys.argv[i] == '-v':
            vowels_only = True
        elif sys.argv[i] == '-e':
            preserve_emphasis = True
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
        main(load_json_filenames, play_codes, char_codes, ep, ec, eo, nested, silent, wt, wj, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)
