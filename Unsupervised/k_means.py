import sys
import os
import csv
import json
import numpy as np
from sklearn.cluster import KMeans


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -h                  Prints help string
    -lc filename.csv    Loads phoneme vectors from specified csv file
    -lj filename.json   Loads phoneme vectors from specified json file
    -e class            Exclude characters of the given class
    -ec char_code       Exclude the given character
    -ep play_code       Exclude characters from the given play
    -mw wordcount       Exclude characters with a word count less than wordcount
    -s                  Silent: Do not print output
    -wc                 Writes output to csv file
    -wj                 Writes output to json file
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files

Sample Filenames:
    ../Archive/Emphasis-Min-500/counts.csv
    ../Archive/No-Others/percentages.json
'''.format(sys.argv[0]))


def load_class_dict():
    class_dict = {}
    with open('../Reference/characteristics.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_dict[row['character']] = row
    return class_dict


def load_char_list():
    return sorted(load_class_dict())


def load_class_list(char_list):
    class_dict = load_class_dict()
    class_list = []
    for char in char_list:
        class_list.append(class_dict[char][class_id])
    return class_list


def filter_char_list(char_list, excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0):
    class_dict = load_class_dict()
    filtered_list = []
    for char in char_list:
        if set([class_dict[char][key] for key in class_dict[char].keys() if key not in ['character', 'word_count']]) & excluded_classes == set():
            if char not in excluded_chars:
                if char.split('_')[0] not in excluded_plays:
                    if int(class_dict[char]['word_count']) >= min_words:
                        filtered_list.append(char)
    return filtered_list


def load_vector_list_csv(filename, filtered_list):
    char_set = set(filtered_list)
    char_list = []
    vector_list = []
    with open(filename, newline='') as csv_in:
        reader = csv.reader(csv_in)
        for line in reader:
            char = line[0]
            if char in char_set:
                vector_list.append(line[1:])  # Strips name from vector
    return vector_list


def load_vector_list_json(filename, filtered_list):
    with open(filename) as json_in:
        char_dict = json.load(json_in)
    phoneme_list = sorted(char_dict[char_list[0]])
    vector_list = []
    for char in filtered_list:
        dict_vector = char_dict[char]
        vector = []
        for phoneme in phoneme_list:
            vector.append(dict_vector[phoneme])
        vector_list.append(vector)
    return vector_list


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_results(k_means_dict, class_id='status'):
    for char in sorted(k_means_dict):
        print('{:>40}:   class: {:<10}   K_Means Group: {:<10}'.format(char, k_means_dict[char][class_id], k_means_dict[char]['k_means_cluster']))


def write_csv(k_means_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'k-means-dictionary.csv'
    with open(filename, 'w', newline='') as csv_out:
        characters = sorted(k_means_dict)
        fieldnames = ['character'] + sorted(k_means_dict[characters[0]].keys())
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        for char in characters:
            out_dict = {'character':char}
            out_dict.update(k_means_dict[char])
            writer.writerow(out_dict)


def write_json(k_means_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'k-means-dictionary.json'
    with open(filename, 'w') as out_json:
        json.dump(k_means_dict, out_json)


def classify(k, vector_list):
    vector_array = np.array(vector_list, dtype=np.float64)
    classifier = KMeans(k)
    cluster_list = classifier.fit_predict(vector_array)
    return cluster_list


def generate_k_means_dict(k, char_list, vector_list, class_dict):
    k_means_dict = {}
    cluster_list = classify(k, vector_list)
    for i in range(len(char_list)):
        char = char_list[i]
        cluster = cluster_list[i]
        k_means_dict[char] = {}
        k_means_dict[char].update(class_dict[char])
        k_means_dict[char]['k_means_cluster'] = str(cluster)
    return k_means_dict


def build_k_means_dictionary(k=0, in_csv='', in_json='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, silent=False, wc=False, wj=False, title='', directory=''):
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    json:', in_json)
        print_help_string()
        quit()

    class_dict = load_class_dict()
    all_chars = sorted(load_class_dict())
    char_list = filter_char_list(all_chars, excluded_classes, excluded_chars, excluded_plays, min_words)

    if in_csv:
        vector_list = load_vector_list_csv(in_csv, char_list)
    elif in_json:
        vector_list = load_vector_list_json(in_json, char_list)
    else:
        print('ERROR: Missing input file')
        print_help_string()
        quit()

    k_means_dict = generate_k_means_dict(k, char_list, vector_list, class_dict)

    if not silent:
        print_results(k_means_dict)
    if wc:
        write_csv(k_means_dict, title, directory)
    if wj:
        write_json(k_means_dict, title, directory)
    return k_means_dict


def main(k=0, in_csv='', in_json='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, silent=False, wc=False, wj=False, title='', directory=''):
    dictionary = build_k_means_dictionary(k, in_csv, in_json, excluded_classes, excluded_chars, excluded_plays, min_words, silent, wc, wj, title, directory)
    return dictionary


if __name__ == '__main__':
    k = 0
    lc = ''
    lj = ''
    excluded_classes = set()
    excluded_chars = set()
    excluded_plays = set()
    min_words = 0
    silent = False
    wc = False
    wj = False
    title = ''
    directory = ''

    if len(sys.argv) == 1:
        print_help_string()
        quit()

    i = 1
    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print_help_string()
            quit()
        elif sys.argv[i] == '-k':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                k = int(sys.argv[i])
            else:
                unrecognized.append('-k: Missing Specifier')
        elif sys.argv[i] == '-lc':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                lc = sys.argv[i]
            else:
                unrecognized.append('-lc: Missing Specifier')
        elif sys.argv[i] == '-lj':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                lj = sys.argv[i]
            else:
                unrecognized.append('-lj: Missing Specifier')
        elif sys.argv[i] == '-e':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                excluded_classes.add(sys.argv[i])
            else:
                unrecognized.append('-e: Missing Specifier')
        elif sys.argv[i] == '-ec':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                excluded_chars.add(sys.argv[i])
            else:
                unrecognized.append('-ec: Missing Specifier')
        elif sys.argv[i] == '-ep':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                excluded_plays.add(sys.argv[i])
            else:
                unrecognized.append('-ep: Missing Specifier')
        elif sys.argv[i] == '-mw':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                min_words = int(sys.argv[i])
            else:
                unrecognized.append('-mw: Missing Specifier')
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wc':
            wc = True
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
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if k == 0:
        unrecognized.append('Missing k for K Means: Please specify with -k')

    if lc == '' and lj == '':
        unrecognized.append('Missing input file: Please specify with -lc or -lj')

    elif lc != '' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lc or -lj')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(k, lc, lj, excluded_classes, excluded_chars, excluded_plays, min_words, silent, wc, wj, title, directory)
