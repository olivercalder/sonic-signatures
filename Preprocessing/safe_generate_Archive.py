import sys
import queue
import threading
import counts
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
            print(thread_name, 'beginning', name)
            counts.build_phoneme_counts(**args_dict)  # Way to unpack args_dict and assign to appropriate optional parameters
            print(thread_name, 'finished', name)
        else:
            queue_lock.release()
            time.sleep(1)

def main(thread_count):
    combinations = [
        ('Emphasis-All', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-All/', 'cascade':True, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-All', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-All/', 'cascade':True, 'vowels_only':True, 'preserve_emphasis':True}),
        ('All', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/All/', 'cascade':True}),
        ('Vowels-Only-All', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-All/', 'cascade':True, 'vowels_only':True}),
        ('Emphasis-Min-100', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Min-100/', 'cascade':True, 'min_words':100, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-Min-100', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-Min-100/', 'cascade':True, 'min_words':100, 'vowels_only':True, 'preserve_emphasis':True}),
        ('Min-100', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Min-100/', 'cascade':True, 'min_words':100}),
        ('Vowels-Only-Min-100', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-Min-100/', 'cascade':True, 'min_words':100, 'vowels_only':True}),
        ('Emphasis-Min-250', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Min-250/', 'cascade':True, 'min_words':250, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-Min-250', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-Min-250/', 'cascade':True, 'min_words':250, 'vowels_only':True, 'preserve_emphasis':True}),
        ('Min-250', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Min-250/', 'cascade':True, 'min_words':250}),
        ('Vowels-Only-Min-250', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-Min-250/', 'cascade':True, 'min_words':250, 'vowels_only':True}),
        ('Emphasis-Min-500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Min-500/', 'cascade':True, 'min_words':500, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-Min-500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-Min-500/', 'cascade':True, 'min_words':500, 'vowels_only':True, 'preserve_emphasis':True}),
        ('Min-500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Min-500/', 'cascade':True, 'min_words':500}),
        ('Vowels-Only-Min-500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-Min-500/', 'cascade':True, 'min_words':500, 'vowels_only':True}),
        ('Emphasis-Min-1000', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Min-1000/', 'cascade':True, 'min_words':1000, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-Min-1000', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-Min-1000/', 'cascade':True, 'min_words':1000, 'vowels_only':True, 'preserve_emphasis':True}),
        ('Min-1000', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Min-1000/', 'cascade':True, 'min_words':1000}),
        ('Vowels-Only-Min-1000', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-Min-1000/', 'cascade':True, 'min_words':1000, 'vowels_only':True}),
        ('Emphasis-Min-2500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Min-2500/', 'cascade':True, 'min_words':2500, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-Min-2500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-Min-2500/', 'cascade':True, 'min_words':2500, 'vowels_only':True, 'preserve_emphasis':True}),
        ('Min-2500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Min-2500/', 'cascade':True, 'min_words':2500}),
        ('Vowels-Only-Min-2500', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-Min-2500/', 'cascade':True, 'min_words':2500, 'vowels_only':True}),
        ('Emphasis-No-Others', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-No-Others/', 'cascade':True, 'eo':True, 'preserve_emphasis':True}),
        ('Emphasis-Vowels-Only-No-Others', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Emphasis-Vowels-Only-No-Others/', 'cascade':True, 'eo':True, 'vowels_only':True, 'preserve_emphasis':True}),
        ('No-Others', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/No-Others/', 'cascade':True, 'eo':True}),
        ('Vowels-Only-No-Others', {'silent':True, 'wt':True, 'wj':True, 'directory':'../Archive/Vowels-Only-No-Others/', 'cascade':True, 'eo':True, 'vowels_only':True})
        ]
    
    exit_flag = [0]
    work_queue = queue.Queue(len(combinations))
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
    for item in combinations:
        work_queue.put(item)
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
