import sys
sys.path.append('../Information')
from archive_combinations import get_names, get_arg_strings
import os
import queue
import threading
import time


class MyThread(threading.Thread):
    def __init__(self, thread_name, work_queue, queue_lock, exit_flag):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.work_queue = work_queue
        self.queue_lock = queue_lock
        self.exit_flag = exit_flag

    def run(self):
        print('Starting', self.thread_name)
        build_directory(self.thread_name, self.work_queue, self.queue_lock, self.exit_flag)
        print('Exiting', self.thread_name)


def build_directory(thread_name, work_queue, queue_lock, exit_flag):
    while not exit_flag[0]:
        queue_lock.acquire()
        if not work_queue.empty():
            name, args = work_queue.get()
            queue_lock.release()
            print('-->', thread_name, 'beginning', name)
            os.system('python3 percentages.py {}'.format(args))
            print('<--', thread_name, 'finished', name)
        else:
            queue_lock.release()
            time.sleep(1)

def main(thread_count):
    names = get_names()
    arg_strings = get_arg_strings()
    '''combinations = [
        ('Emphasis-All', '-s -wt -wj -d ../Archive/Emphasis-All/ -R -e'),
        ('Emphasis-Vowels-Only-All', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-All/ -R -v -e'),
        ('All', '-s -wt -wj -d ../Archive/All/ -R'),
        ('Vowels-Only-All', '-s -wt -wj -d ../Archive/Vowels-Only-All/ -R -v'),
        ('Emphasis-Min-100', '-s -wt -wj -d ../Archive/Emphasis-Min-100/ -R -m 100 -e'),
        ('Emphasis-Vowels-Only-Min-100', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-Min-100/ -R -m 100 -v -e'),
        ('Min-100', '-s -wt -wj -d ../Archive/Min-100/ -R -m 100'),
        ('Vowels-Only-Min-100', '-s -wt -wj -d ../Archive/Vowels-Only-Min-100/ -R -m 100 -v'),
        ('Emphasis-Min-250', '-s -wt -wj -d ../Archive/Emphasis-Min-250/ -R -m 250 -e'),
        ('Emphasis-Vowels-Only-Min-250', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-Min-250/ -R -m 250 -v -e'),
        ('Min-250', '-s -wt -wj -d ../Archive/Min-250/ -R -m 250'),
        ('Vowels-Only-Min-250', '-s -wt -wj -d ../Archive/Vowels-Only-Min-250/ -R -m 250 -v'),
        ('Emphasis-Min-500', '-s -wt -wj -d ../Archive/Emphasis-Min-500/ -R -m 500 -e'),
        ('Emphasis-Vowels-Only-Min-500', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-Min-500/ -R -m 500 -v -e'),
        ('Min-500', '-s -wt -wj -d ../Archive/Min-500/ -R -m 500'),
        ('Vowels-Only-Min-500', '-s -wt -wj -d ../Archive/Vowels-Only-Min-500/ -R -m 500 -v'),
        ('Emphasis-Min-1000', '-s -wt -wj -d ../Archive/Emphasis-Min-1000/ -R -m 1000 -e'),
        ('Emphasis-Vowels-Only-Min-1000', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-Min-1000/ -R -m 1000 -v -e'),
        ('Min-1000', '-s -wt -wj -d ../Archive/Min-1000/ -R -m 1000'),
        ('Vowels-Only-Min-1000', '-s -wt -wj -d ../Archive/Vowels-Only-Min-1000/ -R -m 1000 -v'),
        ('Emphasis-Min-2500', '-s -wt -wj -d ../Archive/Emphasis-Min-2500/ -R -m 2500 -e'),
        ('Emphasis-Vowels-Only-Min-2500', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-Min-2500/ -R -m 2500 -v -e'),
        ('Min-2500', '-s -wt -wj -d ../Archive/Min-2500/ -R -m 2500'),
        ('Vowels-Only-Min-2500', '-s -wt -wj -d ../Archive/Vowels-Only-Min-2500/ -R -m 2500 -v'),
        ('Emphasis-No-Others', '-s -wt -wj -d ../Archive/Emphasis-No-Others/ -R -eo -e'),
        ('Emphasis-Vowels-Only-No-Others', '-s -wt -wj -d ../Archive/Emphasis-Vowels-Only-No-Others/ -R -eo -v -e'),
        ('No-Others', '-s -wt -wj -d ../Archive/No-Others/ -R -eo'),
        ('Vowels-Only-No-Others', '-s -wt -wj -d ../Archive/Vowels-Only-No-Others/ -R -eo -v')
        ]'''
    
    exit_flag = [0]
    work_queue = queue.Queue(len(names))
    queue_lock = threading.Lock()
    
    # Create threads
    threads = []
    for i in range(int(thread_count)):
        thread_name = 'Thread_{}'.format(i)
        thread = MyThread(thread_name, work_queue, queue_lock, exit_flag)
        thread.start()
        threads.append(thread)

    # Fill the queue
    queue_lock.acquire()
    for i in range(len(names)):
        work_queue.put((names[i], arg_strings[i]))
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 {} #_of_threads'.format(sys.argv[0]))
        quit()
    else:
        thread_count = sys.argv[1]
        main(thread_count)
