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
    -h              Prints help string
    -n #_of_threads Specifies number of threads to use for computation
    -c class_id     Specifies the class (role, gender, genre, social class) to predict
    -s              Silent: Do not print output
    -wt             Write output to text file
    -wc             Write output to csv file
    -R              Recursively preserve write preferences for intermediate scripts
    -t title        Title of run, used in output filename
    -d directory    Directory in which to write output files
    -2 class        Performs twofold classification, with specified class as cutoff
                        First: Predict "[class]" or non-"[class]"
                        Second: Of the non-"[class]"s, predict from remaining classes
'''.format(sys.argv[0]))


class MyThread(threading.Thread):
    def __init__(self, thread_name, work_queue, queue_lock, exit_flag, results_list, keep_intermediate, title):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.work_queue = work_queue
        self.queue_lock = queue_lock
        self.exit_flag = exit_flag
        self.results_list = results_list
        self.keep_intermediate = keep_intermediate
        self.title = title

    def run(self):
        print('Starting', self.thread_name)
        classify_and_eval(self.thread_name, self.work_queue, self.queue_lock, self.exit_flag, self.results_list, self.keep_intermediate, self.title)
        print('Exiting', self.thread_name)


def classify_and_eval(thread_name, work_queue, queue_lock, exit_flag, results_list, keep_intermediate, title):
    if title:
        title = title + '_'
    while not exit_flag[0]:
        queue_lock.acquire()
        if not work_queue.empty():
            name, class_args, eval_args = work_queue.get()
            queue_lock.release()
            print('-->', thread_name, 'beginning', title + name)
            os.system('python3 classification.py {}'.format(class_args))
            os.system('python3 evaluation.py {}'.format(eval_args))
            arg_list = eval_args.split(' ')
            index = arg_list.index('-d')
            directory = arg_list[index + 1]
            filename = '{}/{}confusion-matrix.json'.format(directory, title)
            with open(filename, 'r') as result_file:
                conf_dict = json.load(result_file)
            overall_accuracy = conf_dict['overall_accuracy']
            average_accuracy = conf_dict['average_accuracy']
            f1 = conf_dict['f1']
            mcc = conf_dict['mcc']
            results_list.append([name, overall_accuracy, average_accuracy, f1, mcc])
            if not keep_intermediate:
                os.system('rm -r {}*'.format(directory))
            print('<--', thread_name, 'finished', title + name)
        else:
            queue_lock.release()
            time.sleep(1)

def get_string(results_list):
    overall_sorted = sorted(results_list, key=lambda result: result[1], reverse=True)
    average_sorted = sorted(results_list, key=lambda result: result[2], reverse=True)
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)
    lines = []
    lines.append('{:^80}\n'.format('Overall Accuracy:'))
    lines.append('{:>50} {:^10} {:^10} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in overall_sorted:
        lines.append('{:>50} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Accuracy:'))
    lines.append('{:>50} {:^10} {:^10} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in average_sorted:
        lines.append('{:>50} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average F1 Score:'))
    lines.append('{:>50} {:^10} {:^10} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in f1_sorted:
        lines.append('{:>50} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
    lines.append('\n')
    lines.append('{:^80}\n'.format('Average Matthews Correlation Coefficient:'))
    lines.append('{:>50} {:^10} {:^10} {:^10} {:^10}'.format('Option Combination', 'Overall', 'Average', 'F1 Score', 'MCC'))
    for item in mcc_sorted:
        lines.append('{:>50} {:^10.2%} {:^10.2%} {:^10.2%} {:^10.2%}'.format(*item))
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
    filename = directory + 'results_' + title + 'sorted.txt'
    results_string = get_string(results_list)
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
        writer.writerow(['name', 'overall', 'average', 'f1', 'mcc'])
        for line in sorted_results:
            writer.writerow(line)


def main(thread_count, class_id, twofold='', silent=False, wt=False, wc=False, cascade=False, title='', directory=''):
    names = get_class_eval_names(twofold)
    class_args = get_class_args(twofold)
    eval_args = get_eval_args(twofold)

    new_class_args = []
    for arg in class_args:
        new_class_args.append(arg + ' -c ' + class_id)
    class_args = new_class_args

    if silent:
        new_class_args = []
        new_eval_args = []
        for arg in class_args:
            new_class_args.append(arg + ' -s')
        for arg in eval_args:
            new_eval_args.append(arg + ' -s')
        class_args = new_class_args
        eval_args = new_eval_args

    if title:
        new_class_args = []
        new_eval_args = []
        for arg in class_args:
            arg = arg + ' -t {}'.format(title)
            arg = arg.replace('../Results/', '../Results/{}_'.format(title))
            new_class_args.append(arg)
        for arg in eval_args:
            arg = arg + ' -t {}'.format(title)
            arg = arg.replace('../Results/', '../Results/{}_'.format(title))
            arg = arg.replace('results-dictionary', title + '_results-dictionary')
            new_eval_args.append(arg)
        class_args = new_class_args
        eval_args = new_eval_args

    if directory and cascade:
        directory = directory.rstrip('/')
        new_class_args = []
        new_eval_args = []
        for arg in class_args:
            new_class_args.append(arg.replace('../Results', directory))
        for arg in eval_args:
            new_eval_args.append(arg.replace('../Results', directory))
        class_args = new_class_args
        eval_args = new_eval_args
    elif (not directory and not cascade) or (directory and not cascade):
        new_class_args = []
        new_eval_args = []
        for arg in class_args:
            new_class_args.append(arg.replace('../Results', 'tmp'))
        for arg in eval_args:
            new_eval_args.append(arg.replace('../Results', 'tmp'))
        class_args = new_class_args
        eval_args = new_eval_args


    keep_intermediate = False
    if cascade and (wt or wc):
        keep_intermediate = True


    exit_flag = [0]
    work_queue = queue.Queue(len(names))
    queue_lock = threading.Lock()
    results_list = []

    # Create threads
    threads = []
    for i in range(int(thread_count)):
        thread_name = 'Thread_{}'.format(i)
        thread = MyThread(thread_name, work_queue, queue_lock, exit_flag, results_list, keep_intermediate, title)
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
    f1_sorted = sorted(results_list, key=lambda result: result[3], reverse=True)
    mcc_sorted = sorted(results_list, key=lambda result: result[4], reverse=True)

    if not keep_intermediate:
        try:
            os.system('rmdir {}'.format('tmp'))
        except:
            pass  # In case multiple non-cascading scripts are running recursively,
                  #     and thus 'tmp' is non-empty

    if not directory:
        directory = '../Results/'

    if wt:
        write_text(results_list, title, directory)

    if wc:
        write_csv(overall_sorted, title + '_overall', directory)
        write_csv(average_sorted, title + '_average', directory)
        write_csv(f1_sorted, title + '_f1', directory)
        write_csv(mcc_sorted, title + '_mcc', directory)
    
    if not silent:
        print_summary(results_list)

    return overall_sorted, average_sorted, f1_sorted, mcc_sorted


if __name__ == '__main__':
    thread_count = 4
    class_id = ''
    twofold = ''
    silent = False
    wt = False
    wc = False
    cascade = False
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
        main(thread_count, class_id, twofold, silent, wt, wc, cascade, title, directory)
