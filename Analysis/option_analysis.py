import os
import sys
import csv
sys.path.append('../Reference')
from archive_combinations import get_boolean_options, get_iterable_options


def print_help_string():
    print('''
Usage: python3 {} -lc filename [arguments]

Arguments:
    -h              Prints help string
    -lc filename    Name of file to analyze 
                        ie. ../Results/role/results_role_overall_sorted.csv
    -s              Silent: Do not print output
    -wt             Write output to text file
    -wc             Write output to csv file
    -t title        Title of run, used in output filename
    -d directory    Directory in which to write output files
'''.format(sys.argv[0]))


def load_csv(filename):
    results = []
    with open(filename, newline='') as infile:
        reader = csv.reader(infile)
        count = 0
        for row in reader:
            if count != 0:
                name = row[0]
                overall = float(row[1])
                average = float(row[2])
                f1 = float(row[3])
                mcc = float(row[4])
                results.append([name, overall, average, f1, mcc])
            count += 1
    return results


def get_summary(analysis, title=''):
    lines = []
    header = 'Summary of Options:'
    if title:
        header += ' {}'.format(title)
    lines.append('{:^80}\n\n'.format(header))

    percent_line = '{:>16}:   overall = {:<6.2%}   average = {:<6.2%}   f1 = {:<6.2%}   mcc = {:<6.2%}'
    for option in analysis:
        option_lines = analysis[option]
        for line in option_lines:
            lines.append(percent_line.format(*line))
        lines.append('')

    return '\n'.join(lines)


def print_analysis(analysis, title=''):
    print(get_summary(analysis, title))


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/') + '/'
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def write_summary(analysis, title='', directory=''):
    summary = get_summary(analysis, title)
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title:
        title += '_'
    filename = directory + title + 'option_analysis.txt'
    with open(filename, 'w') as outfile:
        print(summary, file=outfile)


def write_csv(analysis, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title:
        title += '_'
    filename = directory + title + 'option_analysis.csv'
    with open(filename, 'w') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['option', 'overall', 'average', 'f1', 'mcc'])
        for option in analysis:
            option_lines = analysis[option]
            for line in option_lines:
                writer.writerow(line)


def get_boolean_analysis(results):
    boolean_analysis = {}
    boolean_options = get_boolean_options()
    for option in boolean_options:
        boolean_analysis[option] = []

        true_overall_sum = 0.0
        true_average_sum = 0.0
        true_f1_sum = 0.0
        true_mcc_sum = 0.0
        true_count = 0

        false_overall_sum = 0.0
        false_average_sum = 0.0
        false_f1_sum = 0.0
        false_mcc_sum = 0.0
        false_count = 0

        for entry in results:
            if option in entry[0]:
                true_overall_sum += entry[1]
                true_average_sum += entry[2]
                true_f1_sum += entry[3]
                true_mcc_sum += entry[4]
                true_count += 1
            else:
                false_overall_sum += entry[1]
                false_average_sum += entry[2]
                false_f1_sum += entry[3]
                false_mcc_sum += entry[4]
                false_count += 1

        if true_count != 0 and false_count != 0:
            true_overall_mean = true_overall_sum / float(true_count)
            true_average_mean = true_average_sum / float(true_count)
            true_f1_mean = true_f1_sum / float(true_count)
            true_mcc_mean = true_mcc_sum / float(true_count)

            false_overall_mean = false_overall_sum / float(false_count)
            false_average_mean = false_average_sum / float(false_count)
            false_f1_mean = false_f1_sum / float(false_count)
            false_mcc_mean = false_mcc_sum / float(false_count)

            boolean_analysis[option].append([option, true_overall_mean, true_average_mean, true_f1_mean, true_mcc_mean])
            boolean_analysis[option].append(['Not ' + option, false_overall_mean, false_average_mean, false_f1_mean, false_mcc_mean])
        else:
            del boolean_analysis[option]
    return boolean_analysis


def get_iterable_analysis(results):
    iterable_analysis = {}
    iterable_options = get_iterable_options()
    for option_set in iterable_options:
        iterable_analysis[option_set] = []
        for option in iterable_options[option_set]:
            
            overall_sum = 0.0
            average_sum = 0.0
            f1_sum = 0.0
            mcc_sum = 0.0
            count = 0

            for entry in results:
                if option in entry[0]:
                    overall_sum += entry[1]
                    average_sum += entry[2]
                    f1_sum += entry[3]
                    mcc_sum += entry[4]
                    count += 1
                    
            if count != 0:
                overall_mean = overall_sum / float(count)
                average_mean = average_sum / float(count)
                f1_mean = f1_sum / float(count)
                mcc_mean = mcc_sum / float(count)

                iterable_analysis[option_set].append([option, overall_mean, average_mean, f1_mean, mcc_mean])

    return iterable_analysis


def main(filename, silent, wt, wc, title, directory):
    analysis = {}

    results = load_csv(filename)

    analysis.update(get_boolean_analysis(results))
    analysis.update(get_iterable_analysis(results))

    if not silent:
        print_analysis(analysis, title)
    if wt:
        write_summary(analysis, title, directory)
    if wc:
        write_csv(analysis, title, directory)

    return analysis


if __name__ == '__main__':
    filename = ''
    silent = False
    wt = False
    wc = False
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
                filename = sys.argv[i]
            else:
                unrecognized.append('-lc: Missing Specifier')
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
        elif sys.argv[i] == '-wc':
            wc = True
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
                unrecognized.append(sys.argv[i])
        else:
            unrecognized.append(sys.argv[i])
        i += 1
    
    if filename == '':
        unrecognized.append('Missing input file: Please specify with -lt filename')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(filename, silent, wt, wc, title, directory)
