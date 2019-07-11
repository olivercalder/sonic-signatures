'''
File: percentages.py
Created: Oliver Calder, 11 July 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgerdigitaltexts.org/api

This script returns a dictionary containing each character code paired to a dictionary of that
character's phonemes paired to their percentage of occurrence. If one or more characters or 
plays is specified, the dictionary will be built using only the codes and phoneme percentages
for those characters. Otherwise, the script will build a dictionary containing every character
by default.

The script can sort characters by play using the -n argument. This causes a dictionary to be
returned with a key for each play mapped to a dictionary where each character code is mapped
to the phoneme dictionary for that character. This takes the form:
{'Mac':{'Mac_Macbeth':{'AA':count, 'AE':count, ...}, 'Mac_Macduff':{'AA':count, ...}, ...},
 'Ham':{'Ham_Hamlet':{'AA':count, ...}, ...}, ...}

Any play or character which is excluded using -ep or -ec, respectively, will not be included in
the dictionary.
'''

help_string = '''
Help for percentages.py:
Returns a dictionary containing the specified character codes mapped to their respective
dictionary of phonemes mapped to percentages. If no character or play codes are specified, it
returns a dictionary containing each character from every play.

Command Line Arguments:
-h               Prints help text
-l [filename]    Specifies one or more json files from which to load existing phoneme counts
-p [play_code]   Specifies one or more plays for which to include characters
-c [char_code]   Specifies one or more characters to be included in the dictionary
-ep [play_code]  Specifies one or more plays whose characters will be excluded
-ec [char_code]  Specifies one or more characters to be excluded from the dictionary
-eo              Exclude characters with role of "other"
-n               Returns a dictionary of characters nested by play, rather than intermixed
-s               Silent: Does not print to console
-wt              Writes the output to file as csv
-wj              Writes the output to file as json
-t [title]       Title: Indicates name of specific run, used in filenames
-d [path/to/dir] Specifies the directory in which to write output files
-R               Recursive cascade: Preserve write preferences for all scripts
-u               Returns dictionary of unknown percentages instead of phoneme percentages
-v               Vowels: Return vowels only
-e               Preserve emphasis marking in phonemes
-r               Preserve raw text (ie. capitalization, punctuation)
-m [min_words]   Specifies the minimum words necessary for a character to be included
'''


import counts
import sys
import copy
import os
import csv
import json


def nest_dict_by_play(percentages):
    percentages_nested = {}
    for char in percentages:
        play = char.split('_')[0]
        if play not in percentages_nested:
            percentages_nested[play] = {}
        percentages_nested[play][char] = percentages[char]
    return percentages_nested


def unnest_dict(percentages_nested):
    percentages = {}
    for play in percentages_nested:
        for char in percentages_nested[play]:
            percentages[char] = percentages_nested[play][char]
    return percentages


def is_nested(percentages):
    nested = False
    for outer_key in percentages: # Way to check if nested
        for inner_key in percentages[outer_key]:
            if type(percentages[outer_key][inner_key]) == type({}):
                nested = True
            break
        break
    return nested


def get_char_list(percentages):
    if is_nested(percentages):
        percentages = unnest_dict(percentages)
    char_list = sorted(percentages)
    return char_list


def get_list_from_percentages(percentages):
    # This method used after percentages have already been found
    # Used for both phonemes and unknowns
    if is_nested(percentages):
        percentages = unnest_dict(percentages)
    for char in percentages:
        items = sorted(percentages[char])
        break
    return items


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


def print_percentages(percentages):
    print(json.dumps(percentages))


def write_csv(percentages, title='', directory='', unknowns=False):
    if is_nested(percentages):
        percentages = unnest_dict(percentages)
    char_list = get_char_list(percentages)
    phoneme_list = get_list_from_percentages(percentages)

    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        title = title + 'unknowns_'
    filename = directory + title + 'percentages.csv'
    csvfile = open(filename, 'w', newline='')
    fieldnames = ['name'] + phoneme_list
    percentages_copy = copy.deepcopy(percentages)
    writer = csv.DictWriter(csvfile, fieldnames)
    writer.writeheader()
    for char in char_list:
        percentages_copy[char]['name'] = char
        writer.writerow(percentages_copy[char])
    csvfile.close()


def write_json(percentages, title='', directory='', unknowns=False):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    if unknowns:
        title = title + 'unknowns_'
    filename = directory + title + 'percentages.json'
    out_json = open(filename, 'w')
    json.dump(percentages, out_json)
    out_json.close()


def count_total(count_vector):
    return sum(count_vector.values())


def convert_counts_to_percentages(count_vector):
    total = count_total(count_vector)
    if total == 0:
        total = 1
    percentage_vector = {}
    for key in count_vector:
        count = count_vector[key]
        percentage = count / total
        percentage_vector[key] = percentage
    return percentage_vector


def get_percentages(counts_dict, nested=False):
    if counts.is_nested(counts_dict):
        counts_dict = coutns.unnest_dict(counts_dict)
    percentages = {}
    for char in counts_dict:
        count_vector = counts_dict[char]
        percentages[char] = convert_counts_to_percentages(count_vector)
    if nested:
        percentages = nest_dict_by_play(percentages)
    return percentages


def build_percentages(load_json_filenames=set([]), play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):

    counts_dict = {}
    for filename in load_json_filenames:
        loaded_dict = load_json(filename)
        if counts.is_nested(loaded_dict):
            loaded_dict = counts.unnest_dict(loaded_dict)
        counts_dict.update(loaded_dict)
    for char in counts_dict:
        ec.add(char)
        
    if play_codes or char_codes or not load_json_filenames:
        new_dict = counts.build_counts_dict(set([]), play_codes, char_codes, ep, ec, eo, nested, silent, wt and cascade, wj and cascade, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)
        if nested:
            new_dict = unnest_dict(new_dict)
        counts_dict.update(new_dict)

    percentages = get_percentages(counts_dict, nested)

    if not silent:
        print_percentages(percentages)
    if wt == True:
        write_csv(percentages, title, directory, unknowns=return_unknowns)
    if wj == True:
        write_json(percentages, title, directory, unknowns=return_unknowns)
    return counts


def main(load_json_filenames=set([]), play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), eo=False, nested=False, silent=False, wt=False, wj=False, title='', directory='', cascade=False, return_unknowns=False, vowels_only=False, preserve_emphasis=False, raw=False, min_words=0):
    return build_percentages(load_json_filenames, play_codes, char_codes, ep, ec, eo, nested, silent, wt, wj, title, directory, cascade, return_unknowns, vowels_only, preserve_emphasis, raw, min_words)


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
    while i + 1 < len(sys.argv) and sys.argv[i+1][0] != '-':
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
                unrecognized.append('-ce: Missing Specifier')
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
