# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:40:35 2014

@author: legitz3
"""

import thread, threading, time

def child(tid):
    print ('hello from child thread '+ str(tid)+'\n')

def parent():
    i=0
    while True:
        i+=1
        print i
        thread.start_new_thread(child, (i,))
        
        inp=str(raw_input('press q to quit\n')) 
        if inp=='q': break
        else: print (inp + ' != q')  
            
def counter(myId, count, mutex):                        # function run in threads
    for i in range(count):
        time.sleep(1)                            # simulate real work
        mutex.acquire()
        print('[%s] => %s' % (myId, i))          # print isn't interrupted now
        mutex.release()

def tgen():
    mutex = thread.allocate_lock()                   # make a global lock object
    for i in range(5):                               # spawn 5 threads
        thread.start_new_thread(counter, (i, 5, mutex))     # each thread loops 5 times
    
    time.sleep(6)
    print('Main thread exiting.')                    # don't exit too early


tgen()
            
            
#parent()