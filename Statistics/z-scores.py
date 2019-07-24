import sys
import os
import copy
import csv
import json


def print_help_string():
    print('''
Usage: python3 {} arguments

Arguments:
    -h                  Print help string
    -lt filename.csv    Loads phoneme vectors from specified csv file
    -lj filename.json   Loads phoneme vectors from specified json file
    -n                  Nests the dictionary of Z-Scores according to play
    -s                  Silent: Do not print output
    -wt                 Writes output to csv file
    -wj                 Writes output to json file
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
'''.format(sys.argv[0]))


def nest_dict_by_play(vectors):
    vectors_nested = {}
    for char in vectors:
        play = char.split('_')[0]
        if play not in vectors_nested:
            vectors_nested[play] = {}
        vectors_nested[play][char] = vectors[char]
    return vectors_nested


def unnest_dict(vectors_nested):
    vectors = {}
    for play in vectors_nested:
        for char in vectors_nested:
            vectors[char] = vectors_nested[play][char]
    return vectors


def is_nested(vectors):
    nested = False
    for outer_key in percentages:
        for inner_key in percentages[outer_key]:
            if type(percentages[outer_key][inner_key]) == type({}):
                nested = True
            break
        break
    return nested


def load_csv(filename):
    vectors = {}
    with open(filename, newline='') as csv_in:
        reader = csv.DictReader(in_csv)
        for row in reader:
            char = row.pop('character')
            vectors[char] = {}
            vectors[char].update(row)
    return vectors


def load_json(filename):
    with open(filename) as json_in:
        vectors = json.load(json_in)
        if is_nested(vectors):
            vectors = unnest_dict(vectors)
    return vectors


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def print_z_scores(z_scores):
    print(json.dumps(z_scores))


def write_csv(z_scores, title='', directory=''):
    if is_nested(z_scores):
        z_scores = unnest_dict(z_scores)
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'Z-Scores.csv'

    char_list = sorted(z_scores)
    phoneme_list = sorted(z_scores[char_list[0]])
    copied_z_scores = copy.deepcopy(z_scores)

    with open(filename, 'w', newline='') as csv_out:
        fieldnames = ['character'] + phoneme_list
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for char in char_list:
            copied_z_scores[char]['character'] = char
            writer.writerow(copied_z_scores[char])


def write_json(z_scores, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'Z-Scores.json'
    with open(filename, 'w') as out_json:
        json.dump(z_scores, out_json)


def get_phoneme_list(vectors):
    if is_nested(vectors):
        vectors = unnest_dict(vectors)
    for char in vectors:
        phonemes = sorted(vectors[char])
        break
    return phonemes


def get_means(vectors):
    if is_nested(vectors):
        vectors = unnest_dict(vectors)
    phonemes = get_phoneme_list(vectors)
    sums = {}
    for phoneme in phonemes:
        sums[phoneme] = 0
    for char in vectors:
        for phoneme in phonemes:
            sums[phoneme] += vectors[char][phoneme]
    means = {}
    for phoneme in phonemes:
        means[phoneme] = sums[phoneme] / len(vectors)
    return means


def get_variances(vectors):
    if is_nested(vectors):
        vectors = unnest_dict(vectors)
    phonemes = get_phoneme_list(vectors)
    means = get_means(vectors)
    variances = {}
    for phoneme in phonemes:
        variances[phoneme] = 0
    for char in vectors:
        for phoneme in phonemes:
            variances[phoneme] += (vectors[char][phoneme] - mean[phoneme])**2
    return variances


def get_standard_deviations(vectors):
    phonemes = get_phoneme_list(vectors)
    variances = get_variances(vectors)
    standard_deviations = {}
    for phoneme in phonemes:
        standard_deviations[phoneme] = (variances[phoneme])**(1/2)
    return standard_deviations


def get_z_scores(vectors, nested=False):
    if is_nested(vectors):
        vectors = unnest_dict(vectors)
    z_scores = {}
    means = get_means(vectors)
    standard_deviations = get_standard_deviations(vectors)
    for char in vectors:
        z_scores[char] = {}
        for phoneme in phonemes:
            z_score = (vectors[char][phoneme] - means[phoneme]) / standard_deviations[phoneme]
            z_scores[char][phoneme] = z_score
    if nested:
        z_scores = nest_dict_by_play(z_scores)
    return z_scores


def build_z_scores(in_csv='', in_json='', nested=False, silent=False, wt=False, wj=False, title='', directory=''):
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    json:', in_json)
        print_help_string()
        quit()
    if in_csv:
        vectors = load_csv(in_csv)
    elif in_json:
        vectors = load_json(in_json)
    else:
        print('ERROR: Missing input file')
        print_help_string()
        quit()
    
    z_scores = get_z_scores(vectors, nested)

    if not silent:
        print_z_scores()
    if wt:
        write_csv(z_scores)
    if wj:
        write_json(z_scores)
    return z_scores


def main(in_csv='', in_json='', nested=False, silent=False, wt=False, wj=False, title='', directory=''):
    return build_z_scores(in_csv, in_json, nested, silent, wt, wj, title, directory)


if __name__ == '__name__':
    lt = ''
    lj = ''
    nested = False
    silent = False
    wt = False
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
        elif sys.argv[i] == '-lt':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                lt = sys.argv[i]
            else:
                unrecognized.append('-lt: Missing Specifier')
        elif sys.argv[i] == '-lj':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                lj = sys.argv[i]
            else:
                unrecognized.append('-lj: Missing Specifier')
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
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if lt == '' and lj == '':
        unrecognized.append('Missing input file: Please specify with -lt or -lj')
    elif lt != '' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lt or -lj')
    if len(unrecognized) > 0:
        print('\ERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lt, lj, nested, silent, wt, wj, title, directory)
