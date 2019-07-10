import sys
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


def write_csv(dict_list, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + title + 'confusion-matrix.csv'
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
    filename = directory + title + 'confusion-matrix.json'
    char_dict = convert_list_to_dict(dict_list)
    with open(filename, 'w') as out_json:
        json.dump(char_dict, out_json)


def classify(vector_list, class_list, new_vector):
    vector_array = np.array(new_vector_list, dtype=np.float64)
    class_array = np.array(new_class_list)
    classifier = MultinomialNB()
    classifier.fit(vector_array, class_array)

    char_vector = np.array(new_vector, dtype=np.float64, order='F')  # 'F' indicates row vector rather than column vector
    prediction = classifier.predict(char_vector)
    return prediction[0]


def hold_one_out(char_list, vector_list, class_list, char_code):
    index = char_list.index(char_code)
    new_char_list = [char for char in char_list]  # Duplicates char_list for editing
    char_code = new_char_list.pop(index)
    new_vector_list = [[count for count in vector_list[c]] for c in range(len(vector_list))]  # Duplicates vector_list for editing
    char_vector = new_vector_list.pop(index)
    new_class_list = [role for role in class_list]  # Duplicates class_list for editing
    actual = new_class_list.pop(index)
    prediction = classify(new_vector_list, new_class_list, char_vector)
    return char_code, actual, prediction


def generate_dict_list(char_list, vector_list, class_list):
    dict_list = []
    for char in char_list:
        char_code, actual, prediction = hold_one_out(char_list, vector_list, class_list, char)
        dict_list.append({'character':char_code, 'actual':class_list[i], 'predicted':prediction[0]})
    return dict_list


def build_confusion_dictionary(infile, wt=False, wj=False, title='', directory=''):
    char_list, vector_list = load_counts(infile)
    class_list = load_class_list(char_list)
    dict_list = generate_dict_list(char_list, vector_list, class_list)
    if wt:
        write_csv(dict_list, title, directory)
    if wj:
        write_json(dict_list, title, dictionary)
    char_dict = convert_list_to_dict(dict_list)
    return char_dict


def main(infile, wt=False, wj=False, title='', directory=''):
    build_confusion_dictionary(infile, wt, wj, title, directory)
    return char_dict


if __name__ == '__main__':
    infile = ''
    wt = False
    wj = False
    title = ''
    directory = ''

    i = 0
    if i + 1 < len(sys.argv) and sys.argv[i+1][0] != '-':
        i += 1
        infile = sys.argv[i]
    else:
        print('Usage: python3 {} in_filename.csv [out_filename.csv]'.format(sys.argv[0]))
        print('filename might be ../Archive/No-Others/counts.csv')
        quit()

    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] = '-h':
            print('Usage: python3 {} in_filename.csv [out_filename.csv]'.format(sys.argv[0]))
            print('filename might be ../Archive/No-Others/counts.csv')
            quit()
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
    if len(unrecognized) > 0:
        print('ERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
    else:
        main(infile, wt, wj, title, directory)
