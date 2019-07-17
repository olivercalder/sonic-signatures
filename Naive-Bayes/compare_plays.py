import sys
import os
import csv
import json
import classification
import evaluation


def print_help_string():
    print('''
Usage: python3 {} Arguments

Arguments:
    -lt filename.csv    Loads classifications from given csv file
    -lj filename.json   Loads classifications from given json file
    -s                  Silent: Do not print output
    -wt                 Writes output to csv file
    -wj                 Writes output to json file
    -R                  Recursively write intermediate outputs along the way
    -t title            Title of run, used in output filenames
    -d directory        Directory in which to write output files
    -2                  Twofold classification
'''.format(sys.argv[0]))


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/').split('/')
        for i in range(len(path)):
            path_chunk = '/'.join(path[:i+1])
            if not os.path.isdir(path_chunk):
                os.mkdir(path_chunk)


def write_csv(sorted_results, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = title + '_'
    filename = directory + 'plays_results_' + title + 'sorted.csv'
    with open(filename, 'w', newline = '') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['name', 'overall', 'average'])
        for line in sorted_results:
            writer.writerow(line)


def main(in_csv='', in_json='', silent=False, wt=False, wj=False, cascade=False, title='', directory='', twofold=''):
    play_dict = classification.build_play_confusion_dictionary(in_csv, in_json, silent, wj and cascade, title, directory, twofold)
    results_list = []
    for play in play_dict:
        play_title = (title + '_' + play).lstrip('_')
        char_dict = play_dict[play]
        play_matrix = evaluation.ConfusionMatrix()
        play_matrix.build(char_dict, play_title)

        overall_accuracy = play_matrix.get_overall_accuracy()
        average_accuracy = play_matrix.get_average_accuracy()
        results_list.append([play, overall_accuracy, average_accuracy])

        if not silent:
            play_matrix.print_summary()
        if wt and cascade:
            play_matrix.write_text(play_title, directory, True)
        if wj and cascade:
            play_matrix.write_json(play_title, directory)
    
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)

    if title:
        title += '_'
    if wt:
        write_csv(overall_sorted, title + 'overall', directory)
        write_csv(average_sorted, title + 'average', directory)

    if not silent:
        print('{:^27}'.format('Overall Accuracy:'))
        print('{:^8} {:^8} {:^8}'.format('name', 'overall', 'average'))
        for item in overall_sorted:
            print('{:^8} {:^8.2%} {:^8.2%}'.format(*item))
        print()
        print('{:^27}'.format('Average Accuracy:'))
        print('{:^8} {:^8} {:^8}'.format('name', 'overall', 'average'))
        for item in average_sorted:
            print('{:^8} {:^8.2%} {:^8.2%}'.format(*item))
        print()

    return overall_sorted, average_sorted


if __name__ == '__main__':
    lt = ''
    lj = ''
    silent = False
    wt = False
    wj = False
    cascade = False
    title = ''
    directory = ''
    twofold = False

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
        elif sys.argv[i] == '-2':
            twofold = True
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
        main(lt, lj, silent, wt, wj, cascade, title, directory, twofold)
