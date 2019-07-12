import sys
import copy
import os
import csv
import json
import numpy as np
from sklearn.naive_bayes import MultinomialNB


def convert_list_to_dict(dict_list):
    char_dict = {}
    for item in dict_list:
        char_code = item['character']
        char_dict[char_code] = item
    return char_dict


def load_class_list(char_list):
    class_dict = {}
    with open('../Information/characteristics.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_dict[row['character']] = row
    class_list = []
    for char in char_list:
        class_list.append(class_dict[char]['role'])
    return class_list


def load_counts(filename):
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


def classify(vector_list, class_list, test_vectors):
    vector_array = np.array(vector_list, dtype=np.float64)
    class_array = np.array(class_list)
    classifier = MultinomialNB()
    classifier.fit(vector_array, class_array)

    test_array = np.array(test_vectors, dtype=np.float64, order='F')  # 'F' indicates row vector rather than column vector
    predictions = classifier.predict(test_array)
    return predictions


def twofold_classify(vector_list, class_list, test_vectors):
    initial_vector_list = vector_list
    initial_class_list = []
    final_vector_list = []
    final_class_list = []
    for i in range(len(class_list)):
        if class_list[i] == 'other':
            initial_class_list.append('other')
        else:
            initial_class_list.append('non-other')
            final_vector_list.append(vector_list[i])
            final_class_list.append(class_list[i])

    initial_vector_array = np.array(initial_vector_list, dtype=np.float64)
    initial_class_array = np.array(initial_class_list)
    initial_classifier = MultinomialNB()
    initial_classifier.fit(initial_vector_array, initial_class_array)

    final_vector_array = np.array(final_vector_list, dtype=np.float64)
    final_class_array = np.array(final_class_list)
    final_classifier = MultinomialNB
    final_classifier.fit(final_vector_array, final_class_array)

    predictions = []
    for vector in test_vectors:
        test_vector = np.array(vector, dtype=np.float, order='F')  # 'F' indicates row vector rather than column vector
        initial_prediction = initial_classifier.predict(test_vector)
        if initial_prediction[0] == 'other':
            predictions.append('other')
        else:
            final_prediction = final_classifier.predict(test_vector)
            predictions.append(final_prediction[0])
    return predictions


def hold_one_out(char_list, vector_list, class_list, char_code, twofold=False):
    index = char_list.index(char_code)
    new_char_list = copy.deepcopy(char_list)
    char_code = new_char_list.pop(index)
    new_vector_list = copy.deepcopy(vector_list)
    char_vector = new_vector_list.pop(index)
    new_class_list = copy.deepcopy(class_list)
    actual = new_class_list.pop(index)
    if twofold:
        prediction = twofold_classify(new_vector_list, new_class_list, [char_vector])[0]
    else:
        prediction = classify(new_vector_list, new_class_list, [char_vector])[0]
    return char_code, actual, prediction


def generate_dict_list(char_list, vector_list, class_list, twofold=False):
    dict_list = []
    for char in char_list:
        char_code, actual, prediction = hold_one_out(char_list, vector_list, class_list, char, twofold)
        dict_list.append({'character':char_code, 'actual':actual, 'predicted':prediction})
    return dict_list


def build_confusion_dictionary(infile, silent=False, wt=False, wj=False, title='', directory='', twofold=False):
    char_list, vector_list = load_counts(infile)
    class_list = load_class_list(char_list)
    dict_list = generate_dict_list(char_list, vector_list, class_list, twofold)
    if not silent:
        print_results(dict_list)
    if wt:
        write_csv(dict_list, title, directory)
    if wj:
        write_json(dict_list, title, directory)
    char_dict = convert_list_to_dict(dict_list)
    return char_dict


def main(infile, silent=False, wt=False, wj=False, title='', directory='', twofold=False):
    char_dict = build_confusion_dictionary(infile, silent, wt, wj, title, directory, twofold)
    return char_dict


if __name__ == '__main__':
    infile = ''
    silent = False
    wt = False
    wj = False
    title = ''
    directory = ''
    twofold = False

    i = 0
    if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
        i += 1
        infile = sys.argv[i]

    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print('Usage: python3 {} input_filename.csv [-wt] [-wj] [-t title] [-d directory] [-2]'.format(sys.argv[0]))
            print('filename might be ../Archive/No-Others/percentages.csv')
            quit()
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
        elif sys.argv[i] == '-2':
            twofold = True
        i += 1

    if infile == '':
        print('ERROR: Missing input file')
        print('Usage: python3 {} input_filename.csv [-wt] [-wj] [-t title] [-d directory] [-2]'.format(sys.argv[0]))
        print('filename might be ../Archive/No-Others/percentages.csv')

    elif len(unrecognized) > 0:
        print('ERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
    else:
        main(infile, silent, wt, wj, title, directory, twofold)
