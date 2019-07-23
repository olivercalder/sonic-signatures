import sys
from collections import OrderedDict
import os
import csv
import json
import numpy as np
import classification


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -lt filename.csv    Loads classifications from given csv file
    -lj filename.json   Loads classifications from given json file
    -s                  Silent: Do not print output
    -wt                 Writes output to csv file
    -wj                 Writes output to json file
    -v                  Verbose: Include more detail in printed and written reports
    -n name             Name of matrix, used in printing but not in filenames
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
'''.format(sys.argv[0]))


def count_total(char_dict):
    return len(char_dict)

def count_correct(char_dict):
    characters = sorted(char_dict)
    correct = 0
    for char in characters:
        if char_dict[char]['actual'] == char_dict[char]['predicted']:
            correct += 1
    return correct

def percent_correct(char_dict):
    total = count_total(char_dict)
    correct = count_correct(char_dict)
    percent = correct / total
    return percent


def count_actual(char_dict, actual):
    characters = sorted(char_dict)
    count = 0
    for char in characters:
        if char_dict[char]['actual'] == actual:
            count += 1
    return count

def count_predicted(char_dict, predicted):
    characters = sorted(char_dict)
    count = 0
    for char in characters:
        if char_dict[char]['predicted'] == predicted:
            count += 1
    return count

def count_pair(char_dict, actual, predicted):
    characters = sorted(char_dict)
    count = 0
    for char in characters:
        if char_dict[char]['actual'] == actual:
            if char_dict[char]['predicted'] == predicted:
                count += 1
    return count


def get_confusion_matrix(char_dict, name=None):
    matrix = ConfusionMatrix()
    matrix.build(char_dict, name)
    return matrix

def get_counts_matrix(char_dict, name=None):
    matrix = ConfusionMatrix()
    matrix.build(char_dict, name)
    return matrix.get_matrix()

def get_percents_matrix(char_dict, name=None):
    matrix = ConfusionMatrix()
    matrix.build(char_dict, name)
    return matrix.get_percent_matrix()


def pretty_matrix(matrix, name='Confusion Matrix', percents=False):
    CM = ConfusionMatrix()
    return CM.pretty_matrix(matrix, name, percents)

def print_matrix(matrix, name='Confusion Matrix', percents=False):
    print(pretty_matrix(matrix, name))


class ConfusionMatrix:
    def __init__(self, char_dict=None, name=None):
        self.data = OrderedDict()
        self.matrix = OrderedDict()
        self.char_matrix = OrderedDict()
        self.name = ''
        if char_dict:
            self.build(char_dict, name)
        if name:
            self.name = name

    def build(self, char_dict, name=None):
        if name:
            self.name = name
        self.data = OrderedDict(char_dict)
        self.matrix = OrderedDict()
        self.char_matrix = OrderedDict()
        for actual in self.get_classes():
            self.matrix[actual] = OrderedDict()
            self.char_matrix[actual] = OrderedDict()
            for predicted in self.get_classes():
                count = 0
                self.char_matrix[actual][predicted] = []
                for char in self.get_characters():
                    if char_dict[char]['actual'] == actual:
                        if char_dict[char]['predicted'] == predicted:
                            count += 1
                            self.char_matrix[actual][predicted].append(char)
                self.matrix[actual][predicted] = count
        return self

    def load_csv(self, filename, name=None):
        if name:
            self.name = name
        char_dict = OrderedDict()
        with open(filename, newline='') as csv_in:
            reader = csv.DictReader(csv_in)
            for entry in reader:
                char = entry['character']
                char_dict[char] = entry
        self.build(char_dict, name)
        return self

    def load_json(self, filename, name=None):
        if name:
            self.name = name
        char_dict = OrderedDict()
        with open(filename) as json_in:
            char_dict = json.load(json_in)
        self.build(char_dict, name)
        return self

    def pretty_matrix(self, matrix=None, name='', percents=False):
        if not matrix:
            matrix = self.matrix
        if not name:
            name = self.name
        if not name:
            name = 'Confusion Matrix'
        lines = []
        dash_width = (76 - len(name)) // 2
        title = '{:^80}'.format(name)
        lines.append(title)
        lines.append('')
        lines.append('{:^80}'.format('rows : actual :: columns : predicted'))
        lines.append('')
        classes = list(matrix.keys())
        line = '{:^10}|' + ('{:^10}|' * len(classes))  # Separated so that inner borders can be removed
        header_args = [''] + classes
        newline = line.format(*header_args)
        lines.append('{:^80}'.format(line.format(*header_args)))
        break_args = ['—'*10] * (len(classes) + 1)
        lines.append('{:^80}'.format(line.format(*break_args)))
        if percents:
            counts_line = '{:^10}|' + ('{:^10.2%}|' * len(classes))  # Separated so that inner borders can be removed
        else:
            counts_line = line
        for actual in classes:
            values = [matrix[actual][predicted] for predicted in classes]
            row_args = [actual] + values
            lines.append('{:^80}'.format(counts_line.format(*row_args)))
            break_args = ['—'*10] * (len(classes) + 1)
            lines.append('{:^80}'.format(line.format(*break_args)))
        lines.append('\n')
        return '\n'.join(lines)

    def print_matrix(self, matrix=None, name='', percents=False):
        print(self.pretty_matrix(matrix, name, percents))

    def __repr__(self):
        return 'ConfusionMatrix({})'.format(self.data)

    def __str__(self):
        return self.pretty_matrix(self.matrix)

    def __lt__(self, other):
        return self.get_overall_accuracy() < other.get_overall_accuracy()

    def __le__(self, other):
        return self.get_average_accuracy() <= other.get_average_accuracy()

    def __gt__(self, other):
        return self.get_overall_accuracy() > other.get_overall_accuracy()

    def __ge__(self, other):
        return self.get_average_accuracy() >= other.get_average_accuracy()

    def __eq__(self, other):
        return self.get_characters() == other.get_characters()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.get_characters():
            return self.data[key]
        elif key in self.get_classes():
            return self.matrix[key]
        elif type(key) == type(tuple()):
            return self.matrix[key[0]][key[1]]
        else:
            print("\nERROR: Unrecognized key '{}' in ConfusionMatrix.__getitem__()".format(key))
            print('Valid keys include:')
            print('    character strings')
            print('    class strings')
            print('    class tuples: (actual, predicted)')
            quit()

    def get_data(self):
        return self.data

    def get_name(self):
        return self.name

    def get_characters(self):
        return sorted(self.data)

    def get_classes(self):
        characters = self.get_characters()
        classes = set()
        for char in characters:
            classes.add(self.data[char]['actual'])
        return sorted(classes)

    def get(self, key1, key2=None):
        if key2:
            keytuple = (key1, key2)
            return self.__getitem__(keytuple)
        else:
            return self.__getitem__(key1)

    def get_matrix(self):
        return self.matrix

    def get_character_matrix(self):
        return self.char_matrix

    def get_percent_matrix(self):
        total = self.get_total()
        if total == 0:
            total = 1
        classes = self.get_classes()
        percent_matrix = OrderedDict()
        for actual in classes:
            percent_matrix[actual] = OrderedDict()
            for predicted in classes:
                percent_matrix[actual][predicted] = self.matrix[actual][predicted] / total
        return percent_matrix

    def get_percent_matrix_given_actual(self):
        classes = self.get_classes()
        percent_matrix = OrderedDict()
        for actual in classes:
            percent_matrix[actual] = OrderedDict()
            class_total = self.get_class_total(actual, 'actual')
            if class_total == 0:
                class_total = 1
            for predicted in classes:
                percent_matrix[actual][predicted] = self.matrix[actual][predicted] / class_total
        return percent_matrix

    def get_percent_matrix_given_predicted(self):
        classes = self.get_classes()
        percent_matrix = OrderedDict()
        for actual in classes:
            percent_matrix[actual] = OrderedDict()
            for predicted in classes:
                class_total = self.get_class_total(predicted, 'predicted')
                if class_total == 0:
                    class_total = 1
                percent_matrix[actual][predicted] = self.matrix[actual][predicted] / class_total
        return percent_matrix

    def get_total(self):
        classes = self.get_classes()
        total = 0
        for actual in classes:
            for predicted in classes:
                total += self.matrix[actual][predicted]
        return total

    def get_class_total(self, c1, actual_or_predicted='actual'):
        total = 0
        for c2 in self.get_classes():
            if actual_or_predicted == 'actual':
                total += self.matrix[c1][c2]
            elif actual_or_predicted == 'predicted':
                total += self.matrix[c2][c1]
        return total

    def get_class_percent(self, c, actual_or_predicted='actual'):
        total = self.get_total()
        if total == 0:
            total = 1
        class_total = self.get_class_total(c, actual_or_predicted)
        return class_total / total

    def get_total_correct(self):
        correct = 0
        for c in self.get_classes():
            correct += self.matrix[c][c]
        return correct

    def get_class_correct(self, c):
        return self.matrix[c][c]

    def get_overall_accuracy(self):
        total = self.get_total()
        if total == 0:
            total = 1
        correct = self.get_total_correct()
        return correct / total

    def get_average_accuracy(self):
        classes = self.get_classes()
        weighted_percent_matrix = self.get_percent_matrix_given_actual()
        accuracy_sum = 0.0
        for c in classes:
            accuracy_sum += weighted_percent_matrix[c][c]
        return accuracy_sum / len(classes)

    def get_class_accuracy(self, c, actual_or_predicted='actual'):
        classes = self.get_classes()
        class_total = self.get_class_total(c, actual_or_predicted)
        if class_total == 0:
            class_total = 1
        correct = self.matrix[c][c]
        return correct / class_total

    def get_class_characters(self, c1, actual_or_predicted='actual'):
        characters = []
        for c2 in self.get_classes():
            if actual_or_predicted == 'actual':
                characters += self.char_matrix[c1][c2]
            elif actual_or_predicted == 'predicted':
                characters += self.char_matrix[c2][c1]
        return characters

    def get_class_precision(self, c):
        correct = self.get_class_correct(c)
        predicted = self.get_class_total(c, 'predicted')
        return correct / predicted

    def get_class_recall(self, c):
        correct = self.get_class_correct(c)
        actual = self.get_class_total(c, 'actual')
        return correct / actual

    def get_f1(self):
        f1_sum = 0.0
        classes = self.get_classes()
        for c in classes:
            f1_sum += self.get_class_f1(c)
        avg_f1 = f1_sum / len(classes)
        return avg_f1

    def get_class_f1(self, c):
        correct = self.get_class_correct(c)
        actual = self.get_class_total(c, 'actual')
        predicted = self.get_class_total(c, 'predicted')
        f1 = 2 * correct / (actual + predicted)
        return f1

    def get_mcc(self):
        mcc_sum = 0.0
        classes = self.get_classes()
        for c in classes:
            mcc_sum += self.get_class_mcc(c)
        avg_mcc = mcc_sum / len(classes)
        return avg_mcc

    def get_class_mcc(self, c1):
        classes = self.get_classes()
        classes.remove(c1)
        tp = self.matrix[c1][c1]
        fp = 0
        fn = 0
        for c2 in classes[1:]:
            fp += self.matrix[c1][c2]
            fn += self.matrix[c2][c1]
        tn = self.get_total() - tp - fp - fn

        numerator = (tp * tn) - (fp * fn)
        denominator = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))**(-1)
        return numerator / denominator

    def get_summary(self, verbose=False):
        lines = []
        title = 'Summary: {}'.format(self.name)
        lines.append('{:^80}\n\n'.format(title))
        line = '{:>38} = {:<39}'
        percent_line = '{:>38} = {:<39.2%}'
        overall_accuracy = percent_line.format('Overall accuracy', self.get_overall_accuracy())
        lines.append('{:^80}'.format(overall_accuracy))
        average_accuracy = percent_line.format('Average accuracy', self.get_average_accuracy())
        lines.append('{:^80}\n'.format(average_accuracy))
        average_f1 = percent_line.format('Average F1 score', self.get_f1())
        lines.append('{:^80}'.format(average_f1))
        average_mcc = percent_line.format('Average MCC', self.get_mcc())
        lines.append('{:^80}\n\n'.format(average_mcc))
        lines.append(self.pretty_matrix(name='Confusion Matrix'))

        classes = self.get_classes()

        if verbose:
            lines.append(line.format('Total samples', self.get_total()))
            lines.append('')
            for c in classes:
                lines.append(line.format('Total actual "{}"'.format(c), self.get_class_total(c, 'actual')))
                lines.append(line.format('Total predicted "{}"'.format(c), self.get_class_total(c, 'predicted')))
            lines.append('\n')

        percent_matrix = self.get_percent_matrix()
        lines.append(self.pretty_matrix(percent_matrix, 'Percent Matrix', True))

        if verbose:
            for c in classes:
                lines.append(percent_line.format('Percent actual "{}"'.format(c), self.get_class_percent(c, 'actual')))
                lines.append(percent_line.format('Percent predicted "{}"'.format(c), self.get_class_percent(c, 'predicted')))
            lines.append('\n')

        percent_matrix_actual = self.get_percent_matrix_given_actual()
        lines.append(self.pretty_matrix(percent_matrix_actual, 'Percent Matrix with Total of Each Actual Class = 100%', True))

        if verbose:
            for c in classes:
                lines.append(percent_line.format('Percent correct of actual "{}"'.format(c), self.get_class_accuracy(c, 'actual')))
            lines.append('\n')

        percent_matrix_predicted = self.get_percent_matrix_given_predicted()
        lines.append(self.pretty_matrix(percent_matrix_predicted, 'Percent Matrix with Total of Each Predicted Class = 100%', True))

        if verbose:
            for c in classes:
                lines.append(percent_line.format('Percent correct of predicted "{}"'.format(c), self.get_class_accuracy(c, 'predicted')))
            lines.append('\n')

            lines.append('{:^80}'.format('F1 Scores:'))
            for c in classes:
                lines.append(percent_line.format('F1 score for "{}"'.format(c), self.get_class_f1(c)))
            lines.append('\n')

            lines.append('{:^80}'.format('Matthews Correlation Coefficients:'))
            for c in classes:
                lines.append(percent_line.format('MCC score for "{}"'.format(c), self.get_class_mcc(c)))
            lines.append('\n')

            lines.append('\n{:^80}\n\n'.format('Characters:'))
            for c1 in classes:
                for c2 in classes:
                    lines.append('{:^80}\n'.format('Actual "{}" Predicted as "{}":'.format(c1, c2)))
                    chars = self.char_matrix[c1][c2]
                    i = 0
                    line = ''
                    for i in range(len(chars)):
                        if len(line + '\t\t' + chars[i]) > 80:
                            lines.append(line.lstrip('\t'))
                            line = ''
                        line += '\t\t' + chars[i]
                    lines.append(line.lstrip('\t'))
                    lines.append('\n')

        return '\n'.join(lines)

    def create_directory(self, directory):
        if not os.path.isdir(directory):
            path = directory.rstrip('/').split('/')
            for i in range(len(path)):
                path_chunk = '/'.join(path[:i+1])
                if not os.path.isdir(path_chunk):
                    os.mkdir(path_chunk)

    def print_summary(self, verbose=False):
        print(self.get_summary(verbose))

    def write_text(self, title='', directory='', verbose=False):
        if directory != '':
            directory = directory.rstrip('/') + '/'
            self.create_directory(directory)
        if title:
            title += '_' 
        filename = directory + title + 'confusion-matrix.txt'
        with open(filename, 'w') as outfile:
            print(self.get_summary(verbose), file=outfile)

    def write_json(self, title='', directory=''):
        out_dict = {}
        out_dict['name'] = self.name
        out_dict['data'] = self.data
        out_dict['overall_accuracy'] = self.get_overall_accuracy()
        out_dict['average_accuracy'] = self.get_average_accuracy()
        out_dict['f1'] = self.get_f1()
        out_dict['mcc'] = self.get_mcc()
        out_dict['matrix'] = self.matrix
        out_dict['character_matrix'] = self.char_matrix
        out_dict['percent_matrix'] = self.get_percent_matrix()
        out_dict['percent_matrix_given_actual'] = self.get_percent_matrix_given_actual()
        out_dict['percent_matrix_given_predicted'] = self.get_percent_matrix_given_predicted()
        out_dict['total'] = self.get_total(),
        out_dict['classes'] = {}
        classes = self.get_classes()
        for c in classes:
            out_dict['classes'][c] = {}
            out_dict['classes'][c]['total_actual'] = self.get_class_total(c, 'actual')
            out_dict['classes'][c]['total_predicted'] = self.get_class_total(c, 'predicted')
            out_dict['classes'][c]['percent_actual'] = self.get_class_percent(c, 'actual')
            out_dict['classes'][c]['percent_predicted'] = self.get_class_percent(c, 'predicted')
            out_dict['classes'][c]['accuracy_actual'] = self.get_class_accuracy(c, 'actual')
            out_dict['classes'][c]['accuracy_predicted'] = self.get_class_accuracy(c, 'predicted')
            out_dict['classes'][c]['actual_characters'] = self.get_class_characters(c, 'actual')
            out_dict['classes'][c]['predicted_characters'] = self.get_class_characters(c, 'predicted')
            out_dict['classes'][c]['f1'] = self.get_class_f1(c)
            out_Dict['classes'][c]['mcc'] = self.get_class_mcc(c)
        if directory != '':
            directory = directory.rstrip('/') + '/'
            self.create_directory(directory)
        if title:
            title += '_'
        filename = directory + title + 'confusion-matrix.json'
        with open(filename, 'w') as outfile:
            json.dump(out_dict, outfile)


def main(in_csv='', in_json='', silent=False, wt=False, wj=False, verbose=False, name='', title='', directory=''):
    if title and not name:
        name = title
    matrix = ConfusionMatrix()
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print_help_string()
        quit()
    if in_csv:
        matrix.load_csv(in_csv, name)
    elif in_json:
        matrix.load_json(in_json, name)
    if not silent:
        matrix.print_summary(verbose)
    if wt:
        matrix.write_text(title, directory, verbose)
    if wj:
        matrix.write_json(title, directory)
    overall_accuracy = matrix.get_overall_accuracy()
    average_accuracy = matrix.get_average_accuracy()
    return overall_accuracy, average_accuracy


if __name__ == '__main__':
    lt = ''
    lj = ''
    silent = False
    wt = False
    wj = False
    verbose = False
    name = ''
    title = ''
    directory = ''

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
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
        elif sys.argv[i] == '-wj':
            wj = True
        elif sys.argv[i] == '-v':
            verbose = True
        elif sys.argv[i] == '-n':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                name = sys.argv[i]
            else:
                unrecognized.append('-n: Missing Specifier')
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

    elif lt !='' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lt or -lj')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lt, lj, silent, wt, wj, verbose, name, title, directory)
