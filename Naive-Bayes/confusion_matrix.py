import sys
import csv
import numpy as np
from sklearn.naive_bayes import MultinomialNB


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


def main(infile, outfile='confusion-dict.csv'):
    char_list = []
    vector_list = []

    with open(infile, newline='') as csv_in:
        reader = csv.reader(csv_in)
        for line in reader:
            char_list.append(line[0])  # Saves ordering of characters for later reference
            vector_list.append(line[1:])  # Strips name from vector
    char_list = char_list[1:]  # Strips "name" from list of character codes
    vector_list = vector_list[1:]  # Strips header from vector list

    class_list = load_class_list(char_list)

    csv_out = open(outfile, 'w', newline='')
    fieldnames = ['character', 'actual', 'predicted']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)

    for i in range(len(char_list)):
        char_code = char_list[i]
        new_char_list = [char for char in char_list]  # Duplicates char_list for editing
        new_char_list.pop(i)
        new_vector_list = [[count for count in vector_list[c]] for c in range(len(vector_list))]  # Duplicates vector_list for editing
        new_vector_list.pop(i)
        new_class_list = [role for role in class_list]  # Duplicates class_list for editing
        new_class_list.pop(i)

        vector_array = np.array(new_vector_list)
        print(vector_array)
        classifier = MultinomialNB()
        classifier.fit(vector_array, new_class_list)
        prediction = classifier.predict(vector_list[i])
        writer.writerow({'character':char_code, 'actual':class_list[i], 'predicted':prediction})
    csv_out.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python3 {} in_filename.csv [out_filename.csv]'.format(sys.argv[0]))
        print('filename might be ../Archive/No-Others/counts.csv')
        quit()
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2]
        main(infile, outfile)
