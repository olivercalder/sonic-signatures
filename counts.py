'''
File: counts.py
Created: Oliver Calder, 26 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a dictionary containing each character code paired to a dictionary of that
character's phonemes paired to their counts. If one or more characters or plays is specified,
the dictionary will be built using only the codes and phoneme counts for those characters.
Otherwise, the script will build a dictionary containing every character by default.

The script can sort characters by play using the -n argument. This causes a dictionary to be
returned with a key for each play mapped to a dictionary where each character code is mapped
to the phoneme dictionary for that character. This takes the form:
{'Mac':{'Mac_Macbeth':{'AA':count, 'AE':count, ...}, 'Mac_Macduff':{'AA':count, ...}, ...},
 'Ham':{'Ham_Hamlet':{'AA':count, ...}, ...}, ...}

Any play or character which is excluded using -ep or -ec, respectively, will not be included in
the dictionary.
'''

help_string = '''
Help for counts.py:
Returns a dictionary containing the specified character codes mapped to their respective
dictionary of phonemes mapped to counts. If no character or play codes are specified, it
returns a dictionary containing each character from every play.

Command Line Arguments:
-h               Prints help text
-p [play_code]   Specifies one or more plays (separated by spaces) for which to include characters
-c [char_code]   Specifies one or more characters to be included in the dictionary
-ep [play_code]  Specifies one or more plays whose characters will be excluded
-ec [char_code]  Specifies one or more characters to be excluded from the dictionary
-n               Returns a dictionary of characters nested by play, rather than intermixed
-s               Silent: Does not print to console
-wt              Writes the output to file as csv
-wj              Writes the output to file as json
-t [title]       Title: Indicates name of specific run, used in filenames
-d [path/to/dir] Specifies the directory in which to write output files
-R               Recursive cascade: Preserve write preferences for all scripts
-u               Returns dictionary of unknown words as well as phoneme dictionary as tuple
-v               Vowels: Return vowels only
-e               Preserve emphasis marking in phonemes
-r               Preserve raw text (ie. capitalization, punctuation)
-m [min_words]   Specifies the minimum words necessary for a character to be included
'''


import phonemes
import sys
import os
import time
import csv
import json


phoneme_codes = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'B', 'CH', 'D', 'DH', 'EH', 'ER', 'EY',
        'F', 'G', 'HH', 'IH', 'IY', 'JH', 'K', 'L', 'M', 'N', 'NG', 'OW', 'OY', 'P', 'R',
        'S', 'SH', 'T', 'TH', 'UH', 'UW', 'V', 'W', 'Y', 'Z', 'ZH']


vowels = {'A', 'E', 'I', 'O', 'U'}


def nest_dict_by_play(counts_dict):
    counts_dict_nested = {}
    for char in counts_dict:
        play = char.split('_')[0]
        if play not in counts_dict_nested:
            counts_dict_nested[play] = {}
        counts_dict_nested[play][char] = counts_dict[char]
    return counts_dict_nested


def unnest_dict(counts_dict_nested):
    counts_dict = {}
    for play in counts_dict_nested:
        for char in counts_dict_nested[play]:
            counts_dict[char] = counts_dict_nested[play][char]
    return counts_dict


def is_nested(counts_dict):
    nested = False
    for outer_key in counts_dict: # Way to check if nested
        for inner_key in counts_dict[outer_key]:
            if type(counts_dict[outer_key][inner_key]) == type({}):
                nested = True
            break
        break
    return nested


def get_char_list(phoneme_counts):
    if is_nested(phoneme_counts):
        phoneme_counts = unnest_dict(phoneme_counts)
    char_list = sorted(phoneme_counts)
    return char_list


def get_unknowns_list(unknowns_dict):
    # This method used to compile ordered set of all words before counts have been found
    if phonemes.is_nested(unknowns_dict):
        unknowns_dict = phonemes.unnest_dict(unknowns_dict)
    unknowns = set([])
    for char in unknowns_dict:
        unknowns |= set(unknowns_dict[char])
    unknowns_list = sorted(unknowns)
    return unknowns_list


def get_list_from_counts(counts):
    # This method used after counts have already been found
    # Used for both phonemes and unknowns
    if is_nested(counts):
        counts = unnest_dict(counts)
    for char in counts:
        items = sorted(counts[char])
        break
    return items


def convert_dict_to_tuple_list(counts_dict):
    keys = sorted(counts_dict)
    sorted_tuples = [(key, counts_dict[key]) for key in keys]
    return sorted_tuples


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_counts(counts):
    print(json.dumps(counts))


def write_text(phoneme_counts, title='', directory='', unknowns=False):
    if is_nested(phoneme_counts):
        phoneme_counts = unnest_dict(phoneme_counts)
    char_list = get_char_list(phoneme_counts)
    phoneme_list = get_list_from_counts(phoneme_counts)

    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        title = title + 'unknowns_'
    filename = directory + title + 'counts.csv'
    csvfile = open(filename, 'w', newline='')
    fieldnames = ['name'] + phoneme_list
    writer = csv.DictWriter(csvfile, fieldnames)
    writer.writeheader()
    for char in char_list:
        phoneme_counts[char]['name'] = char
        writer.writerow(phoneme_counts[char])
    csvfile.close()


def write_json(phoneme_counts, title='', directory='', unknowns=False):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        title = title + 'unknowns_'
    filename = directory + title + 'counts.json'
    out_json = open(filename, 'w')
    json.dump(phoneme_counts, out_json)
    out_json.close()


def count_phoneme_list(phoneme_list, vowels_only=False, preserve_emphasis=False):
    phoneme_counts = {}
    for phoneme in phoneme_codes:
        if phoneme[0] in vowels or not vowels_only:
            if preserve_emphasis:
                if phoneme[0] in vowels:
                    for i in range(3):
                        phon = phoneme + str(i)
                        count = phoneme_list.count(phon)
                        phoneme_counts[phon] = count
            else:
                count = phoneme_list.count(phoneme)
                phoneme_counts[phoneme] = count
    return phoneme_counts


def count_unknowns_list(unknowns_list, unknowns=[]):
    unknowns_counts = {}
    if unknowns == []:
        unknowns = sorted(set(unknowns_list))
    for unknown in unknowns:
        count = unknowns_list.count(unknown)
        unknowns_counts[unknown] = count
    return unknowns_counts


def get_phoneme_counts(phoneme_dict, nested=False, vowels_only=False, preserve_emphasis=False):
    if phonemes.is_nested(phoneme_dict):
        phoneme_dict = phonemes.unnest_dict(phoneme_dict)
    counts_dict = {}
    for char in phoneme_dict:
        counts_dict[char] = count_phoneme_list(phoneme_dict[char], vowels_only, preserve_emphasis)
    if nested:
        counts_dict = nest_dict_by_play(counts_dict)
    return counts_dict


def get_unknowns_counts(unknowns_dict, nested=False):
    if phonemes.is_nested(unknowns_dict):
        unknowns_dict = phonemes.unnest_dict(unknowns_dict)
    counts_dict = {}
    unknowns_list = get_unknowns_list(unknowns_dict)
    for char in unknowns_dict:
        counts_dict[char] = count_unknowns_list(unknowns_dict[char], unknowns=unknowns_list)
    if nested:
        counts_dict = nest_dict_by_play(counts_dict)
    return counts_dict


def build_phoneme_counts(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):

    if return_unknowns:
        phoneme_dict, unknowns_dict = phonemes.build_phoneme_dict(play_codes, char_codes, ep, ec, nested, silent, wt and cascade, wj and cascade, title, directory, cascade, True, vowels_only, preserve_emphasis, raw, min_words)
        unknowns_counts = get_unknowns_counts(unknowns_dict, nested)
    else:
        phoneme_dict = phonemes.build_phoneme_dict(play_codes, char_codes, ep, ec, nested, silent, wt and cascade, wj and cascade, title, directory, cascade, False, vowels_only, preserve_emphasis, raw, min_words)

    phoneme_counts = get_phoneme_counts(phoneme_dict, nested, vowels_only, preserve_emphasis)

    if not silent:
        print_counts(phoneme_counts)
        if return_unknowns:
            print_counts(unknowns_counts)
    if wt == True:
        write_text(phoneme_counts, title, directory)
        if return_unknowns:
            write_text(unknowns_counts, title, directory, unknowns=True)
    if wj == True:
        write_json(phoneme_counts, title, directory)
        if return_unknowns:
            write_json(unknowns_counts, title, directory, unknowns=True)
    if return_unknowns:
        return phoneme_counts, unknowns_counts
    else:
        return phoneme_counts


def main(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):
    return build_phoneme_counts(play_codes, char_codes, ep, ec, nested, silent, wt, wj, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)


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
    return_unknowns = False
    vowels_only = False
    preserve_emphasis = False
    raw = False
    min_words = 0

    i = 0
    while i + 1 < len(sys.argv) and sys.argv[i+1][0] != '-':
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
        main(play_codes, char_codes, ep, ec, nested, silent, wt, wj, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)
