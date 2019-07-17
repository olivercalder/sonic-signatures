import sys
sys.path.append('../Reference')
from archive_combinations import get_names, get_param_dict
import queue
import threading
import percentages
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
            name, args_dict = work_queue.get()
            queue_lock.release()
            print('-->', thread_name, 'beginning', name)
            percentages.build_percentages(**args_dict)  # Way to unpack args_dict and assign to appropriate optional parameters
            print('<--', thread_name, 'finished', name)
        else:
            queue_lock.release()
            time.sleep(1)

def main(thread_count):
    names = get_names()
    param_dicts = get_param_dicts()
    
    exit_flag = [0]
    work_queue = queue.Queue(len(param_dicts))
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
        work_queue.put((names[i], param_dicts[i]))
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
