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
    -lt filename.csv    Loads phoneme vectors from given csv file
    -lj filename.json   Loads phoneme vectors from given json file
    -c class_id         Specifies the class (role, gender, genre, social class) to predict
    -s                  Silent: Do not print output
    -wt                 Writes output to csv file
    -wj                 Writes output to json file
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
    -2 class            Performs twofold classification, with specified class as cutoff
                            First: Predict "[class]" or non-"[class]"
                            Second: Of the non-"[class]"s, predict from remaining classes

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


def load_class_list(char_list, class_id):
    class_dict = {}
    with open('../Reference/characteristics.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_dict[row['character']] = row
    class_list = []
    for char in char_list:
        class_list.append(class_dict[char][class_id])
    return class_list


def load_csv(filename):
    char_list = []
    vector_list = []
    with open(filename, newline='') as csv_in:
        reader = csv.reader(csv_in)
        for line in reader:
            char_list.append(line[0])  # Saves ordering of characters for later reference
            vector_list.append(line[1:])  # Strips name from vector
    char_list = char_list[1:]  # Strips "name" from list of character codes
    vector_list = vector_list[1:]  # Strips header from vector list
    return char_list, vector_list


def load_json(filename):
    with open(filename) as json_in:
        char_dict = json.load(json_in)
    char_list = sorted(char_dict)
    phoneme_list = sorted(char_dict[char_list[0]])
    vector_list = []
    for char in char_list:
        dict_vector = char_dict[char]
        vector = []
        for phoneme in phoneme_list:
            vector.append(dict_vector[phoneme])
        vector_list.append(vector)
    return char_list, vector_list


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


def classify(vector_list, class_list, test_vectors):
    any_percent = False
    for vector in vector_list:
        for count in vector:
            count = float(count)
            if count != int(count) and count <= 1.0 and count >= 0.0:
                any_percent = True

    new_vector_list = []
    for vector in vector_list:
        new_vector = []
        for count in vector:
            count = float(count)
            if any_percent:
                new_vector.append(int(count * 100000))
            else:
                new_vector.append(int(count))
        new_vector_list.append(new_vector)

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

    vector_array = np.array(new_vector_list, dtype=np.float64)
    class_array = np.array(class_list)
    classifier = MultinomialNB()
    classifier.fit(vector_array, class_array)

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

    new_vector_list = []
    for vector in vector_list:
        new_vector = []
        for count in vector:
            count = float(count)
            if any_percent:
                new_vector.append(int(count * 100000))
            else:
                new_vector.append(int(count))
        new_vector_list.append(new_vector)

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

    initial_vector_array = np.array(initial_vector_list, dtype=np.float64)
    initial_class_array = np.array(initial_class_list)
    initial_classifier = MultinomialNB()
    initial_classifier.fit(initial_vector_array, initial_class_array)

    final_vector_array = np.array(final_vector_list, dtype=np.float64)
    final_class_array = np.array(final_class_list)
    final_classifier = MultinomialNB()
    final_classifier.fit(final_vector_array, final_class_array)

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


def hold_one_play_out(char_list, vector_list, class_list, play_code, twofold=''):
    new_char_list = copy.deepcopy(char_list)
    new_vector_list = copy.deepcopy(vector_list)
    new_class_list = copy.deepcopy(class_list)

    char_codes = []
    test_vectors = []
    actuals = []
    predictions = []

    i = 0
    while i < len(new_char_list):
        if new_char_list[i].split('_')[0] == play_code:
            char_codes.append(new_char_list.pop(i))
            actuals.append(new_class_list.pop(i))
            test_vectors.append(new_vector_list.pop(i))
        else:
            i += 1

    if twofold:
        predictions = twofold_classify(new_vector_list, new_class_list, test_vectors, twofold)
    else:
        predictions = classify(new_vector_list, new_class_list, test_vectors)
    return char_codes, actuals, predictions


def generate_dict_list(char_list, vector_list, class_list, twofold=''):
    dict_list = []
    for char in char_list:
        char_code, actual, prediction = hold_one_out(char_list, vector_list, class_list, char, twofold)
        dict_list.append({'character':char_code, 'actual':actual, 'predicted':prediction})
    return dict_list


def generate_play_dict(char_list, vector_list, class_list, twofold=''):
    play_dict = {}
    play_codes = set()
    for char in char_list:
        play_codes.add(char.split('_')[0])
    for play in play_codes:
        char_codes, actuals, predictions = hold_one_play_out(char_list, vector_list, class_list, play, twofold)
        play_dict[play] = [{'character':char_codes[i], 'actual':actuals[i], 'predicted':predictions[i]} for i in range(len(char_codes))]
    return play_dict


def build_confusion_dictionary(in_csv='', in_json='', class_id='', twofold='', silent=False, wt=False, wj=False, title='', directory=''):
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print('    csv:', in_csv)
        print('    JSON:', in_json)
        print_help_string()
        quit()
    if in_csv:
        char_list, vector_list = load_csv(in_csv)
    elif in_json:
        char_list, vector_list = load_json(in_json)
    class_list = load_class_list(char_list, class_id)

    dict_list = generate_dict_list(char_list, vector_list, class_list, twofold)

    if not silent:
        print_results(dict_list)
    if wt:
        write_csv(dict_list, title, directory)
    if wj:
        write_json(dict_list, title, directory)
    char_dict = convert_list_to_dict(dict_list)
    return char_dict


def build_play_confusion_dictionary(in_csv='', in_json='', class_id='', twofold='', silent=False, wt=False, wj=False, title='', directory=''):
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
        char_list, vector_list = load_csv(in_csv)
    elif in_json:
        char_list, vector_list = load_json(in_json)
    class_list = load_class_list(char_list, class_id)
    
    play_dict = generate_play_dict(char_list, vector_list, class_list, twofold)

    if not silent:
        print_play_results(play_dict)
    if wt:
        write_play_csv(play_dict, title, directory)
    if wj:
        write_play_json(play_dict, title, directory)
    new_play_dict = {}
    for play in play_dict:
        new_play_dict[play] = convert_list_to_dict(play_dict[play])
    return new_play_dict


def main(in_csv='', in_json='', class_id='', twofold='', plays=False, silent=False, wt=False, wj=False, title='', directory=''):
    if plays:
        dictionary = build_play_confusion_dictionary(in_csv, in_json, class_id, twofold, silent, wj, title, directory)
    else:
        dictionary = build_confusion_dictionary(in_csv, in_json, class_id, twofold, silent, wt, wj, title, directory)
    return dictionary


if __name__ == '__main__':
    lt = ''
    lj = ''
    class_id = ''
    twofold = ''
    plays = False
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
        elif sys.argv[i] == '-p':
            plays = True
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

    if not class_id:
        unrecognized.append('Missing class id: Please specify with -c')

    if lt == '' and lj == '':
        unrecognized.append('Missing input file: Please specify with -lt or -lj')

    elif lt !='' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lt or -lj')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lt, lj, class_id, twofold, plays, silent, wt, wj, title, directory)
