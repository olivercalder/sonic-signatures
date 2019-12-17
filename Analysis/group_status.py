import sys
import os
import csv
import itertools
sys.path.append('../Naive-Bayes')
import evaluation


# Begins with a single list of strings (classes) and builds a list of all
#     groupings which yield 3 (subject to change) groups in total
def build_groupings_list(classes):  # Implement user-specified number of groups
    groupings_list = []
    for i in range(1, len(classes) - 1):
        for j in range(i + 1, len(classes)):
            groupings_list.append([classes[:i], classes[i:j], classes[j:]])
    return groupings_list


def merge_groups(groupings, *indices):
    indices = sorted(indices)
    if len(indices < 2):
        return groupings
    else:
        i, j = indices[-2], indices[-1]
        merged = groupings[i] + groupings[j]
        new_groupings = groupings[:i] + [merged] + groupings[i+1:j] + groupings[j+1:]
        return merge_groups(new_groupings, indices[:-1])


# Begins with a list of single-element lists (groups) and successively merges
#     groupes until the number of groups is equal to min_size
def greedy_optimize(results_csv, min_size, contiguous=False):
    master = evaluation.ConfusionMatrix()
    master.load_csv(results_csv)
    classes = master.get_classes()
    stages = []
    groupings = [[c] for c in sorted(classes)]
    stages.append(groupings)
    while len(groupings) > min_size:
        possiblities = []
        if contiguous:
            for i in range(len(groupings) - 1):
                possiblities.append(merge_groups(groupings, i, i+1))
        else:
            for (i, j) in itertools.combinations(range(len(groupings)), 2):
                possibilities.append(merge_groups(groupings, i, j))



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
            writer.writerow(line)


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


def main():
    #char_filename = 'status_Vowels-Only-All-Percentages_0-6-Only/status_Vowels-Only-All-Percentages_0-6-Only_results-dictionary.csv'
    char_filename = 's_VOAP_Results/s_VOAP_Results_excluding-a2-7-p-min-100/s_VOAP_Results_excluding-a2-7-p-min-100_results-dictionary.csv'
    master = evaluation.ConfusionMatrix()
    master.load_csv(char_filename)

    classes = ['0', '1', '2', '3', '4', '5', '6']
    groupings_list = build_groupings_list(classes)
    choose_best_grouping(master, groupings_list, directory='s_VOAP_0-6-min-100_Group-Results')


if __name__ == '__main__':
    main()
