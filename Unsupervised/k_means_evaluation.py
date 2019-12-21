import sys
import os
import csv
import json
from collections import OrderedDict


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -lc filename.csv    Loads classifications from specified csv file
    -lj filename.json   Loads classifications from specified json file
    -c class_id         Specifies the class id (ie. status, role, gender, etc.)
    -s                  Silent: Do not print output
    -wt                 Writes output to text file
    -wc                 Writes output to csv files
    -wj                 Writes output to json file
    -v                  Verbose: Include more detail in printed and written reports
    -n name             Name of matrix, used in printing but not in filenames
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
    -zc filename.csv    Loads Z-scores from specified csv file
    -zj filename.json   Loads Z-scores from specified json file
'''.format(sys.argv[0]))


class ConfusionMatrix:
    def __init__(self, char_dict=None, class_id=None, name=None):
        self.data = OrderedDict()
        self.matrix = OrderedDict()
        self.char_matrix = OrderedDict()
        self.class_id = ''
        self.name = ''
        self.z_scores = OrderedDict()
        if char_dict and class_id:
            self.build(char_dict, class_id, name)
        if name:
            self.name = name

    def build(self, char_dict, class_id, name=None):
        self.class_id = class_id
        if name:
            self.name = name
        self.data = OrderedDict(char_dict)
        self.matrix = OrderedDict()
        self.char_matrix = OrderedDict()
        self.z_scores = OrderedDict()
        for c in self.get_classes():
            self.matrix[c] = OrderedDict()
            self.char_matrix[c] = OrderedDict()
            for group in self.get_groups():
                count = 0
                self.char_matrix[c][group] = []
                for char in self.get_characters():
                    if char_dict[char][class_id] == c:
                        if char_dict[char]['k_means_cluster'] == group:
                            count += 1
                            self.char_matrix[c][group].append(char)
                self.matrix[c][group] = count
        return self

    def load_csv(self, filename):
        char_dict = OrderedDict()
        with open(filename, newline='') as csv_in:
            reader = csv.DictReader(csv_in)
            for entry in reader:
                char = entry['character']
                char_dict[char] = entry
        self.data = char_dict
        return self

    def load_json(self, filename):
        char_dict = OrderedDict()
        with open(filename) as json_in:
            char_dict = json.load(json_in)
        self.data = char_dict
        return self


    def pretty_matrix(self, matrix=None, name='', percents=False):
        if not matrix:
            matrix = self.matrix
        if not name:
            name = self.name
        if not name:
            name = 'K Means Matrix'
        lines = []
        dash_width = (76 - len(name)) // 2
        title = '{:^80}'.format(name)
        lines.append(title)
        lines.append('')
        lines.append('{:^80}'.format('rows : classes :: columns : groups'))
        lines.append('')
        classes = self.get_classes()
        groups = self.get_groups()
        line = '{:^10}|' + ('{:^10}|' * len(groups))  # Separated so that inner borders can be removed
        header_args = [''] + groups
        newline = line.format(*header_args)
        lines.append('{:^80}'.format(line.format(*header_args)))
        break_args = ['—'*10] * (len(classes) + 1)
        lines.append('{:^80}'.format(line.format(*break_args)))
        if percents:
            counts_line = '{:^10}|' + ('{:^10.2%}|' * len(groups))  # Separated so that inner borders can be removed
        else:
            counts_line = line
        for c in classes:
            values = [matrix[c][group] for group in groups]
            row_args = [c] + values
            lines.append('{:^80}'.format(counts_line.format(*row_args)))
            break_args = ['—'*10] * (len(groups) + 1)
            lines.append('{:^80}'.format(line.format(*break_args)))
        lines.append('\n')
        return '\n'.join(lines)

    def print_matrix(self, matrix=None, name='', percents=False):
        print(self.pretty_matrix(self, name, percents))


    def get_characters(self):
        return sorted(self.data)

    def get_classes(self):
        characters = self.get_characters()
        classes = set()
        for char in characters:
            classes.add(self.data[char][self.class_id])
        return sorted(classes)

    def get_groups(self):
        characters = self.get_characters()
        groups = set()
        for char in characters:
            groups.add(self.data[char]['k_means_cluster'])
        return sorted(groups)
    

    def get_matrix(self):
        return self.matrix

    def get_character_matrix(self):
        return self.char_matrix

    def get_percent_matrix(self):
        total = self.get_total()
        if total == 0:
            total = 1
        classes = self.get_classes()
        groups = self.get_groups()
        percent_matrix = OrderedDict()
        for c in classes:
            percent_matrix[c] = OrderedDict()
            for group in groups:
                percent_matrix[c][group] = self.matrix[c][group] / total
        return percent_matrix

    def get_percent_matrix_given_class(self):
        classes = self.get_classes()
        groups = self.get_groups()
        percent_matrix = OrderedDict()
        for c in classes:
            percent_matrix[c] = OrderedDict()
            class_total = self.get_class_total(c)
            if class_total == 0:
                class_total = 1
            for group in groups:
                percent_matrix[c][group] = self.matrix[c][group] / class_total
        return percent_matrix

    def get_percent_matrix_given_group(self):
        classes = self.get_classes()
        groups = self.get_groups()
        percent_matrix = OrderedDict()
        for c in classes:
            percent_matrix[c] = OrderedDict()
            for group in groups:
                group_total = self.get_group_total(group)
                if group_total == 0:
                    group_total = 1
                percent_matrix[c][group] = self.matrix[c][group] / group_total
        return percent_matrix

    def get_total(self):
        classes = self.get_classes()
        groups = self.get_groups()
        total = 0
        for c in classes:
            for group in groups:
                total += self.matrix[c][group]
        return total

    def get_class_total(self, c):
        groups = self.get_groups()
        total = 0
        for group in groups:
            total += self.matrix[c][group]
        return total

    def get_group_total(self, group):
        classes = self.get_classes()
        total = 0
        for c in classes:
            total += self.matrix[c][group]
        return total

    def get_class_percent(self, c):
        total = self.get_total()
        if total == 0:
            total = 1
        class_total = self.get_class_total(c)
        return class_total / total

    def get_group_percent(self, group):
        total = self.get_total()
        if total == 0:
            total = 1
        group_total = self.get_group_total(group)
        return group_total / total

    def get_class_characters(self, c):
        characters = []
        groups = self.get_groups()
        for group in groups:
            characters += self.char_matrix[c][group]
        return sorted(characters)

    def get_group_characters(self, group):
        characters = []
        classes = self.get_classes()
        for c in classes:
            characters += self.char_matrix[c][group]
        return sorted(characters)


    def get_character_z_scores(self, char_code):
        return self.z_scores[char]

    def get_class_z_scores(self, c):
        class_characters = self.get_class_characters(c)
        phoneme_list = sorted(self.z_scores[self.get_characters()[0]])
        sums = OrderedDict()
        means = OrderedDict()
        for phoneme in phoneme_list:
            sums[phoneme] = 0
            for char in class_characters:
                sums[phoneme] += self.z_scores[char][phoneme]
            if len(class_characters) > 0:
                means[phoneme] = sums[phoneme] / len(class_characters)
            else:
                means[phoneme] = 'N/A'
        class_z_scores = means
        return class_z_scores

    def get_group_z_scores(self, group):
        group_characters = self.get_group_characters(c)
        phoneme_list = sorted(self.z_scores[self.get_characters()[0]])
        sums = OrderedDict()
        means = OrderedDict()
        for phoneme in phoneme_list:
            sums[phoneme] = 0
            for char in group_characters:
                sums[phoneme] += self.z_scores[char][phoneme]
            if len(group_characters) > 0:
                means[phoneme] = sums[phoneme] / len(group_characters)
            else:
                means[phoneme] = 'N/A'
        group_z_scores = means
        return group_z_scores


    def get_summary(self, verbose=False):
        lines = []
        title = 'Summary: {}'.format(self.name)
        lines.append('{:^80}\n\n'.format(title))
        line = '{:>38} = {:<39}'
        percent_line = '{:>38} = {:<39.2%}'
        lines.append(self.pretty_matrix(name='K Means Matrix'))

        classes = self.get_classes()
        groups = self.get_groups()

        if verbose:
            lines.append(line.format('Total samples', self.get_total()))
            lines.append('')
            for c in classes:
                lines.append(line.format('Total class "{}"'.format(c), self.get_class_total(c)))
            lines.append('\n')
            for group in groups:
                lines.append(line.format('Total group "{}"'.format(group), self.get_group_total(group)))
            lines.append('\n')

        percent_matrix = self.get_percent_matrix()
        lines.append(self.pretty_matrix(percent_matrix, 'Percent Matrix', True))

        if verbose:
            for c in classes:
                lines.append(percent_line.format('Percent class "{}"'.format(c), self.get_class_percent(c)))
            lines.append('\n')
            for group in groups:
                lines.append(percent_line.format('Percent group "{}"'.format(group), self.get_group_percent(group)))
            lines.append('\n')

        percent_matrix_class = self.get_percent_matrix_given_class()
        lines.append(self.pretty_matrix(percent_matrix_class, 'Percent Matrix with Total of Each Class = 100%', True))

        percent_matrix_group = self.get_percent_matrix_given_group()
        lines.append(self.pretty_matrix(percent_matrix_group, 'Percent Matrix with Total of Each Group = 100%', True))


        if self.z_scores:
            lines.append('\n{:^80}\n\n'.format('Class Average Z-Scores'))
            for c in classes:
                lines.append('{:^80}'.format('Class "{}" Average Z-Scores:'.format(c)))
                class_z_scores = self.get_class_z_scores(c)
                phoneme_list = sorted(class_z_scores)
                line = ''
                for phoneme in phoneme_list:
                    if len(line) >= 80:
                        lines.append(line)
                        line = ''
                    if type(class_z_scores[phoneme]) == type('a'):
                        line += '{:>3}: {:<5}  '.format(phoneme, class_z_scores[phoneme])
                    else:
                        line += '{:>3}: {:5.2f}  '.format(phoneme, class_z_scores[phoneme])
                if line:
                    lines.append(line)
                lines.append('\n')

            lines.append('\n{:^80}\n\n'.format('Group Average Z-Scores'))
            for group in groups:
                lines.append('{:^80}'.format('Group "{}" Average Z-Scores:'.format(group)))
                group_z_scores = self.get_group_z_scores(group)
                phoneme_list = sorted(class_z_scores)
                line = ''
                for phoneme in phoneme_list:
                    if len(line) >= 80:
                        lines.append(line)
                        line = ''
                    if type(group_z_scores[phoneme]) == type('a'):
                        line += '{:>3}: {:<5}  '.format(phoneme, group_z_scores[phoneme])
                    else:
                        line += '{:>3}: {:5.2f}  '.format(phoneme, group_z_scores[phoneme])
                if line:
                    lines.append(line)
                lines.append('\n')

            lines.append('\n')

        if verbose:
            lines.append('\n{:^80}\n\n'.format('Characters:'))
            for c in classes:
                for group in groups:
                    lines.append('{:^80}\n'.format('Class "{}" in Group "{}":'.format(c, group)))
                    chars = self.char_matrix[c][group]
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

    def get_csv(self, matrix=None):
        if not matrix:
            matrix = self.matrix
        lines = []
        classes = list(matrix.keys())
        groups = list(matrix[classes[0]].keys())
        lines.append(','.join(['R:C::C:G'] + classes))
        for c in classes:
            values = [str(matrix[c][group]) for group in groups]
            lines.append(','.join([c] + values))
        return '\n'.join(lines)

    def get_json(self):
        out_dict = {}
        out_dict['name'] = self.name
        out_dict['data'] = self.data
        out_dict['matrix'] = self.matrix
        out_dict['character_matrix'] = self.char_matrix
        if self.z_scores:
            out_dict['z_scores'] = self.z_scores
        out_dict['percent_matrix'] = self.get_percent_matrix()
        out_dict['percent_matrix_given_class'] = self.get_percent_matrix_given_class()
        out_dict['percent_matrix_given_group'] = self.get_percent_matrix_given_group()
        out_dict['total'] = self.get_total(),
        out_dict['classes'] = {}
        classes = self.get_classes()
        for c in classes:
            out_dict['classes'][c] = {}
            out_dict['classes'][c]['total'] = self.get_class_total(c)
            out_dict['classes'][c]['percent'] = self.get_class_percent(c)
            out_dict['classes'][c]['characters'] = self.get_class_characters(c)
            if self.z_scores:
                out_dict['classes'][c]['z_scores'] = self.get_class_z_scores(c)
        out_dict['groups'] = {}
        groups = self.get_groups()
        for group in groups:
            out_dict['groups'][group] = {}
            out_dict['groups'][group]['total'] = self.get_group_total(group)
            out_dict['groups'][group]['percent'] = self.get_group_percent(group)
            out_dict['groups'][group]['characters'] = self.get_group_characters(group)
            if self.z_scores:
                out_dict['groups'][group]['z_scores'] = self.get_group_z_scores(group)
        return out_dict


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
        filename = directory + title + 'k-means-matrix.txt'
        with open(filename, 'w') as outfile:
            print(self.get_summary(verbose), file=outfile)

    def write_csv(self, title='', directory=''):
        if directory != '':
            directory = directory.rstrip('/') + '/'
            self.create_directory(directory)
        if title:
            title += '_'
        counts_filename = directory + title + 'k-means-matrix-counts.csv'
        with open(counts_filename, 'w') as outfile:
            print(self.get_csv(), file=outfile)
        percents_filename = directory + title + 'k-means-matrix-percents.csv'
        with open(percents_filename, 'w') as outfile:
            print(self.get_csv(self.get_percent_matrix()), file=outfile)
        percents_given_class_filename = directory + title + 'k-means-matrix-percents-given-class.csv'
        with open(percents_given_class_filename, 'w') as outfile:
            print(self.get_csv(self.get_percent_matrix_given_class()), file=outfile)
        percents_given_group_filename = directory + title + 'k-means-matrix-percents-given-group.csv'
        with open(percents_given_group_filename, 'w') as outfile:
            print(self.get_csv(self.get_percent_matrix_given_group()), file=outfile)

    def write_json(self, title='', directory=''):
        out_dict = self.get_json()
        if directory != '':
            directory = directory.rstrip('/') + '/'
            self.create_directory(directory)
        if title:
            title += '_'
        filename = directory + title + 'k-means-matrix.json'
        with open(filename, 'w') as outfile:
            json.dump(out_dict, outfile)


def main(in_csv='', in_json='', class_id='', silent=False, wt=False, wc=False, wj=False, verbose=False, name='', title='', directory='', z_csv='', z_json=''):
    if in_csv and in_json:
        print('ERROR: Conflicting input files')
        print_help_string()
        quit()
    if class_id == '':
        print('ERRPR: Missing class id')
        print_help_string()
        quit()
    if z_csv and z_json:
        print('ERROR: Conflicting Z-score input files')
        print_help_string()
        quit()
    if title and not name:
        name = title

    matrix = ConfusionMatrix()
    if in_csv:
        matrix.load_csv(in_csv)
    elif in_json:
        matrix.load_json(in_json)

    matrix.build(matrix.data, class_id, name)

    if z_csv:
        matrix.load_z_scores_csv(z_csv)
    elif z_json:
        matrix.load_z_scores_json(z_json)

    if not silent:
        matrix.print_summary(verbose)
    if wt:
        matrix.write_text(title, directory, verbose)
    if wc:
        matrix.write_csv(title, directory)
    if wj:
        matrix.write_json(title, directory)


if __name__ == '__main__':
    lc = ''
    lj = ''
    class_id = ''
    silent = False
    wt = False
    wc = False
    wj = False
    verbose = False
    name = ''
    title = ''
    directory = ''
    zc = ''
    zj = ''

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
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
        elif sys.argv[i] == '-wc':
            wc = True
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
        elif sys.argv[i] == '-zc':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                zc = sys.argv[i]
            else:
                unrecognized.append('-zc: Missing Specifier')
        elif sys.argv[i] == '-zj':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                zj = sys.argv[i]
            else:
                unrecognized.append('-zj: Missing Specifier')
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if lc == '' and lj == '':
        unrecognized.append('Missing input file: Please specify with -lc or -lj')

    elif lc != '' and lj != '':
        unrecognized.append('Conflicting input files: Please include only one of -lc or -lj')

    if class_id == '':
        unrecognized.append('Missing class id: Please specify with -c')

    if zc != '' and zj != '':
        unrecognized.append('Conflicting Z-score input files: Please include only one of -zc or -zj')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lc, lj, class_id, silent, wt, wc, wj, verbose, name, title, directory, zc, zj)
