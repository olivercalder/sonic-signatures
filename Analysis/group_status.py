import sys
import os
import csv
sys.path.append('../Naive-Bayes')
import evaluation


def build_groupings_list(classes):
    groupings_list = []
    for i in range(1, len(classes) - 1):
        for j in range(i + 1, len(classes)):
            groupings_list.append([classes[:i], classes[i:j], classes[j:]])
    return groupings_list


def get_string(results_list):
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)
    lines = []
    lines.append('{:^80}\n'.format('Overall Accuracy:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in overall_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Accuracy:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in average_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average F1 Score:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in f1_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Matthews Correlation Coefficient:'))
    lines.append('{:>30} {:^10} {:^10} {:^10} {:^10}'.format('Grouping', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in mcc_sorted:
        lines.append('{:>30} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
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


def main():
    char_filename = 'status_Vowels-Only-All-Percentages_0-6-Only/status_Vowels-Only-All-Percentages_0-6-Only_results-dictionary.csv'
    master = evaluation.ConfusionMatrix()
    master.load_csv(char_filename)

    classes = ['0', '1', '2', '3', '4', '5', '6']
    groupings_list = build_groupings_list(classes)

    results_list = []
    for grouping in groupings_list:
        print(grouping)
        name = '-'.join([''.join(group) for group in grouping])
        grouped_matrix = evaluation.ConfusionMatrix(master.get_grouped_by(grouping))
        master.write_text(name, 's_VOAP_0-6_Group-Results/' + name, True)
        master.write_csv(name, 's_VOAP_0-6_Group-Results/' + name)
        master.write_json(name, 's_VOAP_0-6_Group-Results/' + name)
        ovl_acc = grouped_matrix.get_overall_accuracy()
        avg_acc = grouped_matrix.get_average_accuracy()
        avg_f1 = grouped_matrix.get_f1()
        avg_mcc = grouped_matrix.get_mcc()
        results_list.append([name, ovl_acc, avg_acc, avg_f1, avg_mcc])

    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)

    write_text(results_list, directory='s_VOAP_0-6_Group-Results')
    write_csv(overall_sorted, 'overall', 's_VOAP_0-6_Group-Results')
    write_csv(average_sorted, 'average', 's_VOAP_0-6_Group-Results')
    write_csv(f1_sorted, 'f1', 's_VOAP_0-6_Group-Results')
    write_csv(mcc_sorted, 'mcc', 's_VOAP_0-6_Group-Results')


if __name__ == '__main__':
    main()
