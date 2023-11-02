import threading


class THBThread(threading.Thread):
    def __init__(self, thread_id, name, delay):
        super().__init__()
        self.thread_id = thread_id
        self.name = name
        self.delay = delay

    def run(self) -> None:
        pass


"""
g_thread_lock = threading.Lock()
threads = []
thread1 = THBThread(1, 't1', 1)
thread2 = THBThread(2, 't2', 2)

#Strat new Threads
thread1.start()
thread2.start()

threads.append(thread1)
threads.append(thread2)

#Wait for all threads to complete
for t in threads:
    t.join()
"""
