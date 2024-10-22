import sys
import os
import csv
import json
sys.path.append('../Naive-Bayes')
import classification
import evaluation
sys.path.append('../Reference')
from archive_combinations import get_names


def print_help_string():
    print('''
Usage: python3 {} Arguments

Arguments:
    -lt filename.csv    Loads vectors from given csv file
    -lj filename.json   Loads vectors from given json file
    -a                  Loads vectors from all combinations of options in
                            Archive and averages results
    -c class_id         Specifies the class (role, gender, genre, status) to predict
    -s                  Silent: Do not print output
    -wt                 Writes output to text file
    -wc                 Writes output to csv file
    -R                  Recursively write intermediate outputs along the way
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
    -2 class            Performs twofold classification, with specified class as cutoff
                            First: Predict "[class]" or non-"[class]"
                            Second: Of the non-"[class]"s, predict from remaining classes
'''.format(sys.argv[0]))


def get_string(results_list):
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)
    lines = []
    lines.append('{:^44}\n'.format('Overall Accuracy:'))
    lines.append('{:^8} {:^8} {:^8} {:^8} {:^8}'.format('Play', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in overall_sorted:
        lines.append('{:^8} {:^8.2%} {:^8.2%} {:^8.2%} {:^8.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^44}\n'.format('Average Accuracy:'))
    lines.append('{:^8} {:^8} {:^8} {:^8} {:^8}'.format('Play', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in average_sorted:
        lines.append('{:^8} {:^8.2%} {:^8.2%} {:^8.2%} {:^8.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^44}\n'.format('Average F1 Score'))
    lines.append('{:^8} {:^8} {:^8} {:^8} {:^8}'.format('Play', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in f1_sorted:
        lines.append('{:^8} {:^8.2%} {:^8.2%} {:^8.2%} {:^8.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^44}\n'.format('Average Matthews Correlation Coefficient'))
    lines.append('{:^8} {:^8} {:^8} {:^8} {:^8}'.format('Play', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in mcc_sorted:
        lines.append('{:^8} {:^8.2%} {:^8.2%} {:^8.2%} {:^8.2%}'.format(*item))
    string = '\n'.join(lines)
    return string

def print_summary(results_list):
    print(get_string(results_list))


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def write_text(results_list, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = (title.rstrip('_') + '_').lstrip('_')
    filename = directory + 'play_results_' + title + 'sorted.txt'
    results_string = get_string(results_list)
    with open(filename, 'w') as text_out:
        print(results_string, file=text_out)


def write_csv(sorted_results, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = (title.rstrip('_') + '_').lstrip('_')
    filename = directory + 'play_results_' + title + 'sorted.csv'
    with open(filename, 'w', newline = '') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['name', 'overall', 'average'])
        for line in sorted_results:
            writer.writerow(line)


def main(in_csv='', in_json='', all_combos=False, class_id='', twofold='', silent=False, wt=False, wc=False, cascade=False, title='', directory=''):
    if title:
        title = title + '_'
    if all_combos:
        play_dict = {}
        dir_names = get_names()
        for name in dir_names:
            for infile in [('counts.csv', 'Counts'), ('percentages.csv', 'Percentages')]:
                twofold_classes = ['']
                if twofold:
                    twofold_classes.append(twofold)
                for twofold_class in twofold_classes:
                    filename = '../Archive/' + name + '/' + infile[0]
                    class_name = name + '-' + infile[1]
                    if twofold_class:
                        class_name += '-Twofold'
                    tmp_dict = classification.build_play_confusion_dictionary(filename, '', class_id, twofold_class, silent, (wt or wc) and cascade, (wt or wc) and cascade, title + class_name, directory)
                    for play in tmp_dict:
                        if play not in play_dict:
                            play_dict[play] = {}
                        for char in tmp_dict[play]:
                            new_char = char + '-' + class_name
                            play_dict[play][new_char] = tmp_dict[play][char]
    else:
        play_dict = classification.build_play_confusion_dictionary(in_csv, in_json, class_id, twofold, silent, (wt or wc) and cascade, (wt or wc) and cascade, title, directory)
    results_list = []
    for play in play_dict:
        play_title = (title + 'All-Combos_' + play).lstrip('_')
        char_dict = play_dict[play]
        play_matrix = evaluation.ConfusionMatrix()
        play_matrix.build(char_dict, play_title)

        overall_accuracy = play_matrix.get_overall_accuracy()
        average_accuracy = play_matrix.get_average_accuracy()
        average_f1 = play_matrix.get_f1()
        average_mcc = play_matrix.get_mcc()
        results_list.append([play, overall_accuracy, average_accuracy, average_f1, average_mcc])

        if not silent:
            play_matrix.print_summary()
        if (wt or wc) and cascade:
            play_matrix.write_text(play_title, directory, True)
        if (wt or wc) and cascade:
            play_matrix.write_json(play_title, directory)

    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)

    if wt:
       write_text(results_list, title, directory) 

    if wc:
        write_csv(overall_sorted, title + 'overall', directory)
        write_csv(average_sorted, title + 'average', directory)
        write_csv(f1_sorted, title + 'f1', directory)
        write_csv(mcc_sorted, title + 'mcc', directory)

    if not silent:
        print_summary(results_list)

    return overall_sorted, average_sorted, f1_sorted, mcc_sorted


if __name__ == '__main__':
    lt = ''
    lj = ''
    all_combos = False
    class_id = ''
    twofold = ''
    silent = False
    wt = False
    wc = False
    cascade = False
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
        elif sys.argv[i] == '-a':
            all_combos = True
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
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
        elif sys.argv[i] == '-wc':
            wc = True
        elif sys.argv[i] == '-R':
            cascade = True
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

    if lt == '' and lj == '' and not all_combos:
        unrecognized.append('Missing input file: Please specify with -lt,-lj, or -a')

    elif (lt != '' and lj != '') or ((lt != '' or lj != '') and all_combos):
        unrecognized.append('Conflicting input files: Please include only one of -lt, -lj, or -a')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(lt, lj, all_combos, class_id, twofold, silent, wt, wc, cascade, title, directory)
