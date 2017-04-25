import threading
from time import sleep
from pprint import pprint as pp

def worker():
    t_name = threading.currentThread().getName()
    t_id = threading.currentThread().ident
    print "Inside worker"
    sleep(10)

    print ">> {} : THREAD : {} <<".format(t_name, t_id)

def main():
    for item in range(1,6):
        t = threading.Thread(target=worker)
        t.start()

    list1 = threading.enumerate() ; print "LIST ALL RUNNING THREADS", list1 ## this will list all running threads
    list2 = threading.currentThread() ; print "CURRENT" , list2 ## this will list the current thread which is main thread

    for t in threading.enumerate():# This is for all threads
        if t is not threading.currentThread():
            print "t is %s" %t
            t.join()

    print "main thread terminates"


    print "MAIN THREAD TERMINATES"

if __name__ == '__main__':
    main()