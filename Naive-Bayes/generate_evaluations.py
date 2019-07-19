import sys
sys.path.append('../Reference')
from archive_combinations import get_class_eval_names, get_class_args, get_eval_args
import os
import queue
import threading
import time
import csv
import json


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -h              Help
    -n #_of_threads Specifies number of threads to use for computation
    -c class_id     Specifies the class (role, gender, social class, etc.) to predict
    -s              Silent
    -wt             Write text
    -wc             Write csv
    -t title        Title, used in output filename
    -d directory    Output directory
'''.format(sys.argv[0]))


class MyThread(threading.Thread):
    def __init__(self, thread_name, work_queue, queue_lock, exit_flag, results_list):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.work_queue = work_queue
        self.queue_lock = queue_lock
        self.exit_flag = exit_flag
        self.results_list = results_list

    def run(self):
        print('Starting', self.thread_name)
        classify_and_eval(self.thread_name, self.work_queue, self.queue_lock, self.exit_flag, self.results_list)
        print('Exiting', self.thread_name)


def classify_and_eval(thread_name, work_queue, queue_lock, exit_flag, results_list):
    while not exit_flag[0]:
        queue_lock.acquire()
        if not work_queue.empty():
            name, class_args, eval_args = work_queue.get()
            queue_lock.release()
            print('-->', thread_name, 'beginning', name)
            os.system('python3 classification.py {}'.format(class_args))
            os.system('python3 evaluation.py {}'.format(eval_args))
            dir_list = class_args.split(' ')
            filename = dir_list[-1] + '/confusion-matrix.json'
            with open(filename, 'r') as result_file:
                conf_dict = json.load(result_file)
            overall_accuracy = conf_dict['overall_accuracy']
            average_accuracy = conf_dict['average_accuracy']
            results_list.append([name, overall_accuracy, average_accuracy])
            print('<--', thread_name, 'finished', name)
        else:
            queue_lock.release()
            time.sleep(1)

def get_string(results_list):
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    lines = []
    lines.append('{:^80}\n'.format('Overall Accuracy:'))
    lines.append('{:>60} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average'))
    for item in overall_sorted:
        lines.append('{:>60} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('')
    lines.append('{:^80}\n'.format('Average Accuracy:'))
    lines.append('{:>60} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average'))
    for item in average_sorted:
        lines.append('{:>60} {:^10.2%} {:^10.2%}'.format(*item))
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
    results_string = get_string(results_list)
    filename = directory + 'results_' + title + 'sorted.txt'
    with open(filename, 'w') as text_out:
        print(results_string, file=text_out)

def write_csv(sorted_results, title='', directory=''):
    if directory != '':
        directory = directory.rstrip('/') + '/'
        create_directory(directory)
    if title != '':
        title = (title + '_').lstrip('_')
    filename = directory + 'results_' + title + 'sorted.csv'
    with open(filename, 'w', newline = '') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['name', 'overall', 'average'])
        for line in sorted_results:
            writer.writerow(line)


def main(thread_count, class_id, silent, wt, wc, title, directory):
    names = get_class_eval_names()
    class_args = get_class_args()
    eval_args = get_eval_args()

    new_class_args = []
    for arg in class_args:
        new_class_args.append(arg + ' -c ' + class_id)
    class_args = new_class_args

    if directory:
        directory = directory.rstrip('/')
        new_class_args = []
        new_eval_args = []
        for arg in class_args:
            new_class_args.append(arg.replace('../Results', directory))
        for arg in eval_args:
            new_eval_args.append(arg.replace('../Results', directory))
        class_args = new_class_args
        eval_args = new_eval_args

    exit_flag = [0]
    work_queue = queue.Queue(len(names))
    queue_lock = threading.Lock()
    results_list = []

    # Create threads
    threads = []
    for i in range(int(thread_count)):
        thread_name = 'Thread_{}'.format(i)
        thread = MyThread(thread_name, work_queue, queue_lock, exit_flag, results_list)
        thread.start()
        threads.append(thread)

    # Fill the queue
    queue_lock.acquire()
    for i in range(len(names)):
        work_queue.put((names[i], class_args[i], eval_args[i]))
    queue_lock.release()

    # Wait for queue to empty
    while not work_queue.empty():
        time.sleep(1)

    # Notify threads of end
    exit_flag[0] = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print('Exiting Main Thread')

    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)

    if not directory:
        directory = '../Results/'

    if wt:
        write_text(results_list, title, directory)

    if wc:
        write_csv(overall_sorted, title + '_overall', directory)
        write_csv(average_sorted, title + '_average', directory)
    
    if not silent:
        print_summary(results_list)

    return overall_sorted, average_sorted


if __name__ == '__main__':
    thread_count = 4
    class_id = ''
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
        elif sys.argv[i] == '-n':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                thread_count = int(sys.argv[i])
            else:
                unrecognized.append('-t: Missing Specifier')
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

    if not class_id:
        unrecognized.append('Missing class id: Please specify with -c')

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print()
        print_help_string()
    else:
        main(thread_count, class_id, silent, wt, wc, title, directory)
