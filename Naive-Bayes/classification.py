import sys
import copy
import os
import csv
import json
import numpy as np
from sklearn.naive_bayes import MultinomialNB


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -h                  Prints help string
    -lc filename.csv    Loads phoneme vectors from specified csv file
    -lj filename.json   Loads phoneme vectors from specified json file
    -c class_id         Specifies the class (role, gender, genre, status) to predict
    -e class            Exclude characters of the given class
    -ec char_code       Exclude the given character
    -ep play_code       Exclude characters from the given play
    -mw wordcount       Exclude characters with a word count less than wordcount
    -cd                 Class Dictionary: Hold out one class at a time
                            Classify characters from each class after training
                            the model on characters from all other classes.
                            Thus, model predicts to which of the other classes the
                            given character most corresponds.
    -pd                 Play Dictionary: Hold out one play at a time
                            Classify characters from each play after training
                            the model on characters from all other plays.
    -s                  Silent: Do not print output
    -wc                 Writes output to csv file
    -wj                 Writes output to json file
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
    -2 class            Performs twofold classification, with specified class as cutoff
                            First: Predict "<class>" or non-"<class>"
                            Second: Of the non-"<class>"s, predict from remaining classes

Sample Filenames:
    ../Archive/Emphasis-Min-500/counts.csv
    ../Archive/No-Others/percentages.json
'''.format(sys.argv[0]))


def convert_list_to_dict(dict_list):
    char_dict = {}
    for item in dict_list:
        new_item = copy.deepcopy(item)
        char_code = new_item['character']
        del new_item['character']
        char_dict[char_code] = new_item
    return char_dict


def convert_dict_to_list(char_dict):
    dict_list = list(char_dict.values())
    return dict_list


def load_class_dict():
    class_dict = {}
    with open('../Reference/characteristics.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_dict[row['character']] = row
    return class_dict


def load_char_list(filename=None, csv_or_json=None):
    if filename:
        if csv_or_json == 'csv' or filename[-4:] == '.csv':
            char_set = set()
            with open(filename, newline='') as csv_in:
                reader = csv.DictReader(csv_in)
                for row in reader:
                    char_set.add(row['character'])
            return sorted(char_set)
        else:
            with open(filename) as json_in:
                char_dict = json.load(json_in)
            return sorted(char_dict)
    else:
        return sorted(load_class_dict())


def load_class_list(char_list, class_id):
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


def print_results(dict_list):
    for entry in dict_list:
        print(entry)


def print_class_results(class_dict):
    for c in sorted(class_dict):
        print(c)
        for entry in class_dict[c]:
            print(entry)
        print()


def print_play_results(play_dict):
    for play in play_dict:
        print(play)
        for entry in play_dict[play]:
            print(entry)
        print()


def write_csv(dict_list, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'results-dictionary.csv'
    csv_out = open(filename, 'w', newline='')
    fieldnames = ['character', 'actual', 'predicted']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    for entry in dict_list:
        writer.writerow(entry)
    csv_out.close()


def write_class_csv(class_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'class-results-dictionary.csv'
    csv_out = open(filename, 'w', newline='')
    fieldnames = ['character', 'actual', 'predicted']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    for c in sorted(class_dict):
        for entry in class_dict[c]:
            writer.writerow(entry)
    csv_out.close()


def write_play_csv(play_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'play-results-dictionary.csv'
    csv_out = open(filename, 'w', newline='')
    fieldnames = ['character', 'actual', 'predicted']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    for play in sorted(play_dict):
        for entry in play_dict[play]:
            writer.writerow(entry)
    csv_out.close()


def write_json(dict_list, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'results-dictionary.json'
    char_dict = convert_list_to_dict(dict_list)
    with open(filename, 'w') as out_json:
        json.dump(char_dict, out_json)


def write_class_json(class_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'class-results-dictionary.json'
    new_class_dict = {}
    for c in class_dict:
        new_class_dict[c] = convert_list_to_dict(class_dict[c])
    with open(filename, 'w') as out_json:
        json.dump(new_class_dict, out_json)


def write_play_json(play_dict, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'play-results-dictionary.json'
    new_play_dict = {}
    for play in play_dict:
        new_play_dict[play] = convert_list_to_dict(play_dict[play])
    with open(filename, 'w') as out_json:
        json.dump(new_play_dict, out_json)


def get_classifier(vector_list, class_list, percentages=False):
    new_vector_list = []
    for vector in vector_list:
        new_vector = []
        for count in vector:
            count = float(count)
            if percentages:
                new_vector.append(int(count * 100000))
            else:
                new_vector.append(int(count))
        new_vector_list.append(new_vector)

    vector_array = np.array(new_vector_list, dtype=np.float64)
    class_array = np.array(class_list)
    classifier = MultinomialNB()
    classifier.fit(vector_array, class_array)
    return classifier


def classify(vector_list, class_list, test_vectors):
    any_percent = False
    for vector in vector_list:
        for count in vector:
            count = float(count)
            if count != int(count) and count <= 1.0 and count >= 0.0:
                any_percent = True

    classifier = get_classifier(vector_list, class_list, any_percent)

    new_test_vectors = []
    for vector in test_vectors:
        new_vector = []
        for count in vector:
            count = float(count)
            if any_percent:
                new_vector.append(int(count * 100000))
            else:
                new_vector.append(int(count))
        new_test_vectors.append(new_vector)        

    test_array = np.array(new_test_vectors, dtype=np.float64)
    predictions = classifier.predict(test_array)
    return predictions


def twofold_classify(vector_list, class_list, test_vectors, twofold_class):
    any_percent = False
    for vector in vector_list:
        for count in vector:
            count = float(count)
            if count != int(count) and count <= 1.0 and count >= 0.0:
                any_percent = True

    new_test_vectors = []
    for vector in test_vectors:
        new_vector = []
        for count in vector:
            count = float(count)
            if any_percent:
                new_vector.append(int(count * 100000))
            else:
                new_vector.append(int(count))
        new_test_vectors.append(new_vector)        

    initial_vector_list = new_vector_list
    initial_class_list = []
    final_vector_list = []
    final_class_list = []
    for i in range(len(class_list)):
        if class_list[i] == twofold_class:
            initial_class_list.append(twofold_class)
        else:
            initial_class_list.append('non-' + twofold_class)
            final_vector_list.append(new_vector_list[i])
            final_class_list.append(class_list[i])

    initial_classifier = get_classifier(initial_vector_list, initial_class_list, any_percent)
    final_classifier = get_classifier(final_vector_list, final_class_list, any_percent)

    predictions = []
    for vector in new_test_vectors:
        test_vector = np.array([vector], dtype=np.float)
        initial_prediction = initial_classifier.predict(test_vector)
        if initial_prediction[0] == twofold_class:
            predictions.append(twofold_class)
        else:
            final_prediction = final_classifier.predict(test_vector)
            predictions.append(final_prediction[0])
    return predictions


def hold_one_out(char_list, vector_list, class_list, char_code, twofold=''):
    index = char_list.index(char_code)

    new_char_list = copy.deepcopy(char_list)
    new_vector_list = copy.deepcopy(vector_list)
    new_class_list = copy.deepcopy(class_list)

    char_code = new_char_list.pop(index)
    char_vector = new_vector_list.pop(index)
    actual = new_class_list.pop(index)

    test_vectors = []
    test_vectors.append(char_vector)
    if twofold:
        prediction = twofold_classify(new_vector_list, new_class_list, test_vectors, twofold)[0]
    else:
        prediction = classify(new_vector_list, new_class_list, test_vectors)[0]
    return char_code, actual, prediction


def hold_one_class_out(char_list, vector_list, class_list, class_id, twofold=''):
    new_char_list = []
    new_vector_list = []
    new_class_list = []

    test_char_list = []
    test_vectors = []
    actuals = []
    predictions = []

    char_set = set(filter_char_list(char_list, excluded_classes=set([class_id])))

    for i in range(len(char_list)):
        char = char_list[i]
        if char in char_set:
            new_char_list.append(char_list[i])
            new_vector_list.append(vector_list[i])
            new_class_list.append(class_list[i])
        else:
            test_char_list.append(char_list[i])
            actuals.append(class_list[i])
            test_vectors.append(vector_list[i])

    if twofold:
        predictions = twofold_classify(new_vector_list, new_class_list, test_vectors, twofold)
    else:
        predictions = classify(new_vector_list, new_class_list, test_vectors)
    return test_char_list, actuals, predictions


def hold_one_play_out(char_list, vector_list, class_list, play_code, twofold=''):
    new_char_list = []
    new_vector_list = []
    new_class_list = []

    test_char_list = []
    test_vectors = []
    actuals = []
    predictions = []

    for i in range(len(char_list)):
        char = char_list[i]
        if char.split('_')[0] != play_code:
            new_char_list.append(char_list[i])
            new_vector_list.append(vector_list[i])
            new_class_list.append(class_list[i])
        else:
            test_char_list.append(char_list[i])
            actuals.append(class_list[i])
            test_vectors.append(vector_list[i])

    if twofold:
        predictions = twofold_classify(new_vector_list, new_class_list, test_vectors, twofold)
    else:
        predictions = classify(new_vector_list, new_class_list, test_vectors)
    return test_char_list, actuals, predictions


def generate_dict_list(char_list, vector_list, class_list, twofold=''):
    dict_list = []
    for char in char_list:
        char_code, actual, prediction = hold_one_out(char_list, vector_list, class_list, char, twofold)
        dict_list.append({'character':char_code, 'actual':actual, 'predicted':prediction})
    return dict_list


def generate_class_dict(char_list, vector_list, class_list, twofold=''):
    class_dict = {}
    classes = set(class_list)
    for c in sorted(classes):
        char_codes, actuals, predictions = hold_one_class_out(char_list, vector_list, class_list, c, twofold)
        class_dict[c] = [{'character':char_codes[i], 'actual':actuals[i], 'predicted':predictions[i]} for i in range(len(char_codes))]
    return class_dict


def generate_play_dict(char_list, vector_list, class_list, twofold=''):
    play_dict = {}
    play_codes = set()
    for char in char_list:
        play_codes.add(char.split('_')[0])
    for play in play_codes:
        char_codes, actuals, predictions = hold_one_play_out(char_list, vector_list, class_list, play, twofold)
        play_dict[play] = [{'character':char_codes[i], 'actual':actuals[i], 'predicted':predictions[i]} for i in range(len(char_codes))]
    return play_dict


def build_confusion_dictionary(in_csv='', in_json='', class_id='', twofold='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, silent=False, wc=False, wj=False, title='', directory=''):
    if not class_id:
        print('ERROR: Missing class id')
        print_help_string()
        quit()
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    JSON:', in_json)
        print_help_string()
        quit()

    if in_csv:
        all_chars = load_char_list(in_csv, 'csv')
    else:
        all_chars = load_char_list(in_json, 'json')
    char_list = filter_char_list(all_chars, excluded_classes, excluded_chars, excluded_plays, min_words)

    if in_csv:
        vector_list = load_vector_list_csv(in_csv, char_list)
    elif in_json:
        vector_list = load_vector_list_json(in_json, char_list)
    else:
        print('ERROR: Missing input file')
        print_help_string()
        quit()

    class_list = load_class_list(char_list, class_id)

    dict_list = generate_dict_list(char_list, vector_list, class_list, twofold)

    if not silent:
        print_results(dict_list)
    if wc:
        write_csv(dict_list, title, directory)
    if wj:
        write_json(dict_list, title, directory)
    char_dict = convert_list_to_dict(dict_list)
    return char_dict


def build_class_confusion_dictionary(in_csv='', in_json='', class_id='', twofold='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, silent=False, wc=False, wj=False, title='', directory=''):
    if not class_id:
        print('ERROR: Missing class id')
        print_help_string()
        quit()
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    JSON:', in_json)
        print_help_string()
        quit()

    all_chars = load_char_list()
    char_list = filter_char_list(all_chars, excluded_classes, excluded_chars, excluded_plays, min_words)
    
    if in_csv:
        vector_list = load_vector_list_csv(in_csv, char_list)
    elif in_json:
        vector_list = load_vector_list_json(in_json, char_list)
    else:
        print('ERROR: Missing input file')
        print_help_string()
        quit()

    class_list = load_class_list(char_list, class_id)
    
    class_dict = generate_class_dict(char_list, vector_list, class_list, twofold='')

    if not silent:
        print_class_results(class_dict)
    if wc:
        write_class_csv(class_dict, title, directory)
    if wj:
        write_class_json(class_dict, title, directory)
    new_class_dict = {}
    for c in class_dict:
        new_class_dict[c] = convert_list_to_dict(class_dict[c])
    return new_class_dict


def build_play_confusion_dictionary(in_csv='', in_json='', class_id='', twofold='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, silent=False, wc=False, wj=False, title='', directory=''):
    if not class_id:
        print('ERROR: Missing class id')
        print_help_string()
        quit()
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    JSON:', in_json)
        print_help_string()
        quit()

    all_chars = load_char_list()
    char_list = filter_char_list(all_chars, excluded_classes, excluded_chars, excluded_plays, min_words)

    if in_csv:
        vector_list = load_vector_list_csv(in_csv, char_list)
    elif in_json:
        vector_list = load_vector_list_json(in_json, char_list)
    else:
        print('ERROR: Missing input file')
        print_help_string()
        quit()

    class_list = load_class_list(char_list, class_id)
    
    play_dict = generate_play_dict(char_list, vector_list, class_list, twofold)

    if not silent:
        print_play_results(play_dict)
    if wc:
        write_play_csv(play_dict, title, directory)
    if wj:
        write_play_json(play_dict, title, directory)
    new_play_dict = {}
    for play in play_dict:
        new_play_dict[play] = convert_list_to_dict(play_dict[play])
    return new_play_dict


def main(in_csv='', in_json='', class_id='', twofold='', excluded_classes=set(), excluded_chars=set(), excluded_plays=set(), min_words=0, classes=False, plays=False, silent=False, wc=False, wj=False, title='', directory=''):
    if classes and plays:
        print('ERROR: Cannot build class dictionary and play dictionary at the same time')
        print_help_string()
        quit()
    if classes:
        dictionary = build_class_confusion_dictionary(in_csv, in_json, class_id, twofold, excluded_classes, excluded_chars, excluded_plays, min_words, silent, wc, wj, title, directory)
    elif plays:
        dictionary = build_play_confusion_dictionary(in_csv, in_json, class_id, twofold, excluded_classes, excluded_chars, excluded_plays, min_words, silent, wc, wj, title, directory)
    else:
        dictionary = build_confusion_dictionary(in_csv, in_json, class_id, twofold, excluded_classes, excluded_chars, excluded_plays, min_words, silent, wc, wj, title, directory)
    return dictionary


if __name__ == '__main__':
    lc = ''
    lj = ''
    class_id = ''
    twofold = ''
    excluded_classes = set()
    excluded_chars = set()
    excluded_plays = set()
    min_words = 0
    plays = False
    classes = False
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
        elif sys.argv[i] == '-c':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                class_id = sys.argv[i]
            else:
                unrecognized.append('-c: Missing Specifier')
        elif sys.argv[i] == '-2':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                twofold = sys.argv[i]
            else:
                unrecognized.append('-2: Missing Specifier')
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
        elif sys.argv[i] == '-cd':
            classes = True
        elif sys.argv[i] == '-pd':
            plays = True
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

    if not class_id:
        unrecognized.append('Missing class id: Please specify with -c')

    if lc == '' and lj == '':
        unrecognized.append('Missing input file: Please specify with -lc or -lj')

    elif lc != '' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lc or -lj')

    if plays and classes:
        unrecognized.append('Conflicting classification formats: Please include at most one of -pd and -cd')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lc, lj, class_id, twofold, excluded_classes, excluded_chars, excluded_plays, min_words, classes, plays, silent, wc, wj, title, directory)
