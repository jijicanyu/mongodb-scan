#!/usr/bin/env python
#-*- coding: utf-8 -*-
# system lib
import threading
import time
import socket
import Queue
import logging
import datetime
#third lib
import pymongo
from IPy import IP
#myself lib
from lib import console_print
from lib import cmd_parse
from lib import mongodb_check
from lib import mongodb_nmap

class mongodb_scan:

    '''
    scan mongodb server
    '''

    def __init__(self):
        self.__APP_STOP = False
        self.__queue_target = Queue.Queue()
        self.__lock_output_msg = threading.Lock()
        self.__lock_thread_num = threading.Lock()
        self.__thread_num = 0
        self.__target_total = 0
        self.__progress_deltal = 5
        self.__progress_num = 0
        self.__progress_last = 0
        # get argument
        self.__args = cmd_parse.get_argument()
        filename = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'.txt'
        if self.__args.logfile!= None:
            filename = self.__args.logfile
        logging.basicConfig(level=logging.INFO,format='%(message)s',filename=filename,filemode="a")                


    def __get_target_from_line(self):
        '''
        get target from cmd line by --u(target)
        '''
        try:
            ips = IP(self.__args.target)

            self.__target_total = len(ips)
            for ip in ips:
                self.__queue_target.put(str(ip))
            return True
        except Exception, ex:
            print "[-]Fail to get target:%s" % ex.message
            return False

    def __get_target_from_file(self):
        '''
        get target from a scanned log file,the everyone target is same like ip:port,xxx(target info)
        '''
        with open(self.__args.file) as f:
            for line in f:
                host_port = line.split(',')[0]
                try:
                    ip = IP(host_port.split(':')[0])
                    self.__queue_target.put(str(ip))
                    self.__target_total += 1
                except:
                    continue
        return True


    def __generate_target_queue(self):
        '''
        generate all the target ip
        '''
        if self.__args.target != None:
            return self.__get_target_from_line()

        if self.__args.file != None:
            return self.__get_target_from_file()

        return False
        
    def __get_one_target(self):
        '''
        get one target from queue, and get the progress 
        '''
        if self.__queue_target.empty():
            return None
        try:
            target = self.__queue_target.get(block=False)

            self.__progress_num += 1
            progress_now = 100 * self.__progress_num / self.__target_total
            if progress_now - self.__progress_last >= self.__progress_deltal:
                self.__progress_last = progress_now
                self.__print_result(
                    '[-]progress: %d%%...' % self.__progress_last)

            return target

        except:
            return None

    def __print_progress(self, msg):
        '''
        show progress message
        '''
        self.__lock_output_msg.acquire()
        console_print.print_progress(msg)
        self.__lock_output_msg.release()

    def __print_result(self, msg):
        '''
        show result message
        '''
        self.__lock_output_msg.acquire()
        console_print.print_result(msg)
        self.__lock_output_msg.release()

    def __do_scan(self):
        '''
        scan process
        '''
        # start
        self.__lock_thread_num.acquire()
        self.__thread_num += 1
        self.__lock_thread_num.release()
        # do loop
        while True:
            if self.__APP_STOP == True:
                break
            target = self.__get_one_target()
            if target == None:
                break
            # scan target
            self.__print_progress('target:%s...' % target)
            if self.__args.nmap :
                target_info = self.__do_nmap_one_target(target,self.__args.port)
            else:
                target_info = self.__do_scan_one_target(target, self.__args.port)
            # show server info:
            if len(target_info) > 0:
                for ti in target_info:
                    info = ''
                    if self.__args.nmap :
                        server_info = mongodb_check.get_mongodb_server_info(ti[0],ti[1])
                        if server_info != None:
                            info = '%s:%d,%s' % (ti[0], ti[1], server_info)
                    else:
                        info = '%s:%d,%s' % (ti[0], ti[1], ti[2])

                    if info != '':
                        logging.info (info)
                        self.__print_result('[+]' + info)
        # end
        self.__lock_thread_num.acquire()
        self.__thread_num -= 1
        self.__lock_thread_num.release()

    def __do_nmap_one_target(self,target,ports):
        '''
        use nmap to scan one target
        '''
        target_info = mongodb_nmap.nmap_mongodb(target,ports)

        return target_info


    def __do_scan_one_target(self, target, ports):
        '''
        scan one target and everyone port
        '''
        target_info = []
        ports_list = ports.split(',')

        for p in ports_list:
            port = int(p)
            # check port open:
            check_open = mongodb_check.check_mongodb_open(
                target, port, timeout=self.__args.timeout)
            if check_open == False:
                continue
            # get server info
            server_info = mongodb_check.get_mongodb_server_info(
                target, port, timeout=self.__args.timeout)
            if server_info == None:
                #server_info = 'connect fail' 
                continue   
            #
            target_info.append((target, port, server_info))

        return target_info

    def run(self):
        '''
        run the scan process,and use multi-thread
        '''
        get_target = self.__generate_target_queue()
        if get_target == False:
            return
        print "[+]start run,total target:%d" % self.__queue_target.qsize()
        for i in range(self.__args.threads):
            t_scan = threading.Thread(target=self.__do_scan, args=())
            t_scan.setDaemon(True)
            t_scan.start()
        while True:
            self.__lock_thread_num.acquire()
            thread_num = self.__thread_num
            self.__lock_thread_num.release()
            if thread_num <= 0:
                break
            try:
                time.sleep(0.01)
            except KeyboardInterrupt:
                self.__APP_STOP = True
                self.__print_result(
                    '[-]waiting for %d thread exit...' % self.__thread_num)

        self.__print_result("[-]finish!")


def main():
    app = mongodb_scan()
    app.run()

if __name__ == '__main__':
    main()
