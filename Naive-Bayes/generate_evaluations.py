import sys
sys.path.append('../Information')
from archive_combinations import *
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

def main(thread_count):
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

    print('Overall Accuracy:')
    for item in overall_sorted:
        print('{:>40} {:^10.2%} {:^10.2%}'.format(*item))

    print('Average Accuracy:')
    for item in average_sorted:
        print('{:>40} {:^10.2%} {:^10.2%}'.format(*item))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 {} #_of_threads'.format(sys.argv[0]))
        quit()
    else:
        thread_count = sys.argv[1]
        main(thread_count)
