import sys
sys.path.append('../Reference')
from archive_combinations import get_class_eval_names, get_class_args, get_eval_args
import os
import queue
import threading
import time
import csv
import json


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


def create_directory(directory):
    if not os.path.isdir(directory):
        path = directory.rstrip('/') + '/'
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
    filename = directory + 'results_' + title + 'sorted.csv'
    with open(filename, 'w', newline = '') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['name', 'overall', 'average'])
        for line in sorted_results:
            writer.writerow(line)


def main(thread_count, silent, wt, title, directory):
    names = get_class_eval_names()
    class_args = get_class_args()
    eval_args = get_eval_args()

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

    if title:
        title += '_'

    if not directory:
        directory = '../Results/'

    if wt:
        write_csv(overall_sorted, title + 'overall', directory)
        write_csv(average_sorted, title + 'average', directory)
    
    if not silent:
        print('Overall Accuracy:')
        for item in overall_sorted:
            print('{:>60} {:^10.2%} {:^10.2%}'.format(*item))
        print('')
        print('Average Accuracy:')
        for item in average_sorted:
            print('{:>60} {:^10.2%} {:^10.2%}'.format(*item))

    return overall_sorted, average_sorted


if __name__ == '__main__':
    thread_count = 4
    silent = False
    wt = False
    title = ''
    directory = ''

    i = 1
    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print('''
Arguments:
    -h              Help
    -c #_of_threads
    -s              Silent
    -wt             Write csv
    -t title
    -d directory    Output directory
            ''')
            quit()
        elif sys.argv[i] == '-c':
            if i+1 < len(sys.argv) and sys.argv[i+1][0] != '-':
                i += 1
                thread_count = int(sys.argv[i])
            else:
                unrecognized.append('-t: Missing Specifier')
        elif sys.argv[i] == '-s':
            silent = True
        elif sys.argv[i] == '-wt':
            wt = True
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

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print()
        print('''
Arguments:
    -h              Help
    -c #_of_threads
    -s              Silent
    -wt             Write csv
    -t title
    -d directory    Output directory
        ''')
    else:
        main(thread_count, silent, wt, title, directory)
