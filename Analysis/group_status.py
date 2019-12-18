import sys
import os
import csv
import itertools
sys.path.append('../Naive-Bayes')
import evaluation


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -n number_of_groups     Specifies to number of groups into which to divide all classes
    -m min_words            Specifies the minimum words (this sources from s_VOAP_Results,
                                so must be in [100, 250, 500, 1000, 1500, 2000, 2500]
    -d                      Discontiguous: Create groupings from non-adjacent classes as well
    -g [ovl/avg/f1/mcc]     Greedy: Uses greedy approach with the given metric at each stage of grouping
'''.format(sys.argv[0]))


def get_string(results_list):
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)
    lines = []
    lines.append('{:^80}\n'.format('Overall Accuracy:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in overall_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item[:-1]))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Accuracy:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in average_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item[:-1]))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average F1 Score:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in f1_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item[:-1]))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Matthews Correlation Coefficient:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in mcc_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item[:-1]))
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
        title = (title + '_').lstrip('_')
    filename = directory + 'grouping_results_' + title + 'sorted.txt'
    results_string = get_string(results_list)
    with open(filename, 'w') as text_out:
        print(results_string, file=text_out)


def write_csv(sorted_results, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = (title + '_').lstrip('_')
    filename = directory + 'grouping_results_' + title + 'sorted.csv'
    with open(filename, 'w', newline = '') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['name', 'overall', 'average', 'f1', 'mcc'])
        for line in sorted_results:
            writer.writerow(line[:-1])


def choose_best_grouping(master_matrix, groupings_list, ovl_avg_f1_mcc='ovl', directory=''):
    results_list = []
    for grouping in groupings_list:
        print(grouping)
        name = '-'.join([''.join(group) for group in grouping])
        grouped_matrix = evaluation.ConfusionMatrix(master_matrix.get_grouped_by(grouping))
        if directory:
            grouped_matrix.write_text(name, directory + '/' + name, True)
            grouped_matrix.write_csv(name, directory + '/' + name)
            grouped_matrix.write_json(name, directory + '/' + name)
        ovl_acc = grouped_matrix.get_overall_accuracy()
        avg_acc = grouped_matrix.get_average_accuracy()
        avg_f1 = grouped_matrix.get_f1()
        avg_mcc = grouped_matrix.get_mcc()
        results_list.append([name, ovl_acc, avg_acc, avg_f1, avg_mcc, grouping])

    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)
    returns = [overall_sorted[0][-1], average_sorted[0][-1], f1_sorted[0][-1], mcc_sorted[0][-1]]

    if directory:
        write_text(results_list, directory=directory)
        write_csv(overall_sorted, 'overall', directory)
        write_csv(average_sorted, 'average', directory)
        write_csv(f1_sorted, 'f1', directory)
        write_csv(mcc_sorted, 'mcc', directory)

    return returns[['ovl', 'avg', 'f1', 'mcc'].index(ovl_avg_f1_mcc)]


def merge_groups(groupings, *indices):
    indices = sorted(indices)
    if len(indices) < 2:
        return groupings
    else:
        i, j = indices[-2], indices[-1]
        merged = tuple(sorted(groupings[i] + groupings[j]))
        new_groupings = tuple(groupings[:i] + (merged,) + groupings[i+1:j] + groupings[j+1:])
        return merge_groups(new_groupings, indices[:-1])


def generate_next_merges(groupings, contiguous=True):
    groupings = tuple(sorted(groupings, key=lambda g: g[0]))
    possibilities = []
    if contiguous:
        for i in range(len(groupings) - 1):
            possibilities.append(merge_groups(groupings, i, i+1))
    else:
        for (i, j) in itertools.combinations(range(len(groupings)), 2):
            possibilities.append(merge_groups(groupings, i, j))
    return possibilities


def build_groupings_list(classes, n, contiguous=True):
    groupings = tuple([(c,) for c in classes])
    groupings_list = [groupings]
    for i in range(len(classes) - n):
        new_groupings = set()
        for groupings in groupings_list:
            possibilities = generate_next_merges(groupings, contiguous)
            new_groupings |= set(possibilities)
        groupings_list = sorted(new_groupings)
    return groupings_list


# Begins with a tuple of single-element tuples (groups) and successively merges
#     groupes until the number of groups is equal to min_size
def greedy_optimize(results_csv, min_size, min_words, ovl_avg_f1_mcc='f1', contiguous=True):
    master = evaluation.ConfusionMatrix()
    master.load_csv(results_csv)
    classes = master.get_classes()
    stages = []
    groupings = tuple([(c,) for c in sorted(classes)])
    stages.append(groupings)
    while len(groupings) > min_size:
        possibilities = generate_next_merges(groupings)
        groupings = choose_best_grouping(master, possibilities, ovl_avg_f1_mcc, directory='s_VOAP_0-6_Group-Results/s_VOAP_0-6{0}_Group-Results/Greedy-{1}{2}/{3}-Groups{2}'.format(('' if min_words == 0 else '-min-{}'.format(min_words)), ovl_avg_f1_mcc, ('' if contiguous else '-Discontiguous'), len(groupings)))
        stages.append(groupings)

    with open('s_VOAP_0-6_Group-Results/s_VOAP_0-6{}_Group-Results/Greedy-{}{}/groupings.tsv'.format(('' if min_words == 0 else '-min-{}'.format(min_words)), ovl_avg_f1_mcc, ('' if contiguous else '-Discontiguous')), 'w') as outfile:
        for i in range(len(stages)):
            stage = stages[i]
            print('{}\t{}'.format(len(stage), stage), file=outfile)


def main(n, min_words, contiguous=True, greedy=''):
    #char_filename = 'status_Vowels-Only-All-Percentages_0-6-Only/status_Vowels-Only-All-Percentages_0-6-Only_results-dictionary.csv'
    char_filename = 's_VOAP_Results/s_VOAP_Results_excluding-a2-7-p{0}/s_VOAP_Results_excluding-a2-7-p{0}_results-dictionary.csv'.format('' if min_words == 0 else '-min-{}'.format(min_words))
    if greedy:
        greedy_optimize(char_filename, n, min_words, greedy, contiguous)
    else:
        master = evaluation.ConfusionMatrix()
        master.load_csv(char_filename)
        classes = master.get_classes()
        groupings_list = build_groupings_list(classes, n, contiguous)
        choose_best_grouping(master, groupings_list, directory='s_VOAP_0-6_Group-Results/s_VOAP_0-6{}_Group-Results/{}{}'.format(('' if min_words == 0 else '-min-{}'.format(min_words)), n, ('' if contiguous else'-Discontiguous')))


if __name__ == '__main__':
    n = -1
    min_words = 0
    contiguous = True
    greedy = ''

    i = 1
    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print_help_string()
            quit()
        elif sys.argv[i] == '-n':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                n = int(sys.argv[i])
            else:
                unrecognized.append('-n: Missing Specifier')
        elif sys.argv[i] == '-m':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                min_words = int(sys.argv[i])
            else:
                unrecognized.append('-m: Missing Specifier')
        elif sys.argv[i] == '-g':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                greedy = sys.argv[i]
            else:
                unrecognized.append('-g: Missing Specifier')
        elif sys.argv[i] == '-d':
            contiguous = False
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if n < 0:
        unrecognized.append('Missing group number: Please specify with -n')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print_help_string()

    else:
        main(n, min_words, contiguous, greedy)
