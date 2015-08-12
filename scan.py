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
from IPy import IP
#myself lib
from lib import console_print
from lib import cmd_parse
from lib import mongodb_check

class mongodb_scan:

    '''
    scan mongodb server
    '''

    def __init__(self):
        self.APP_STOP = False
        self.queue_target = Queue.Queue()
        self.__lock_output_msg = threading.Lock()
        self.lock_thread_num = threading.Lock()
        self.thread_num = 0
        self.__target_total = 0
        self.__progress_deltal = 5
        self.__progress_num = 0
        self.__progress_last = 0
        self.__queue_output_msg = Queue.Queue()
        # get argument
        self.args = cmd_parse.get_argument()
        filename = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'.txt'
        if self.args.logfile!= None:
            filename = self.args.logfile
        logging.basicConfig(level=logging.INFO,format='%(message)s',filename=filename,filemode="a")                


    def __get_target_from_line(self):
        '''
        get target from cmd line by --u(target)
        '''
        try:
            ips = IP(self.args.target)

            self.__target_total = len(ips)
            for ip in ips:
                self.queue_target.put(str(ip))
            return True
        except Exception, ex:
            self.print_result("[-]Fail to get target:%s" % ex.message)
            return False

    def __get_target_from_file(self):
        '''
        get target from a scanned log file,the everyone target is same like ip:port,xxx(target info)
        '''
        with open(self.args.file) as f:
            for line in f:
                host_port = line.split(',')[0]
                try:
                    ip = IP(host_port.split(':')[0])
                    self.queue_target.put(str(ip))
                    self.__target_total += 1
                except:
                    continue
        return True


    def generate_target_queue(self):
        '''
        generate all the target ip
        '''
        if self.args.target != None:
            return self.__get_target_from_line()

        if self.args.file != None:
            return self.__get_target_from_file()

        return False
        
    def __get_one_target(self):
        '''
        get one target from queue, and get the progress 
        '''
        if self.queue_target.empty():
            return None
        try:
            target = self.queue_target.get(block=False)

            self.__progress_num += 1
            progress_now = 100 * self.__progress_num / self.__target_total
            if progress_now - self.__progress_last >= self.__progress_deltal:
                self.__progress_last = progress_now
                self.print_result(
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

    def print_result(self, msg):
        '''
        show result message
        '''
        self.__queue_output_msg.put(msg)
        self.__lock_output_msg.acquire()
        console_print.print_result(msg)
        self.__lock_output_msg.release()


    def get_output_msg(self):
        '''
        get one output message from queue
        '''
        if self.__queue_output_msg.empty():
            return None
        return self.__queue_output_msg.get()

    def do_scan(self):
        '''
        scan process
        '''
        # start
        self.lock_thread_num.acquire()
        self.thread_num += 1
        self.lock_thread_num.release()
        # do loop
        while True:
            if self.APP_STOP == True:
                break
            target = self.__get_one_target()
            if target == None:
                break
            # scan target
            self.__print_progress('target:%s...' % target)
            if self.args.nmap :
                target_info = self.__do_nmap_one_target(target,self.args.port)
            else:
                target_info = self.do_scan_one_target(target, self.args.port)
            # show server info:
            if len(target_info) > 0:
                for ti in target_info:
                    info = ''
                    if self.args.nmap :
                        server_info = mongodb_check.get_mongodb_server_info(ti[0],ti[1])
                        if server_info != None:
                            info = '%s:%d,%s' % (ti[0], ti[1], server_info)
                    else:
                        info = '%s:%d,%s' % (ti[0], ti[1], ti[2])

                    if info != '':
                        logging.info (info)
                        self.print_result('[+]' + info)
        # end
        self.lock_thread_num.acquire()
        self.thread_num -= 1
        self.lock_thread_num.release()

    def __do_nmap_one_target(self,target,ports):
        '''
        use nmap to scan one target
        '''
        from lib import mongodb_nmap
        target_info = mongodb_nmap.nmap_mongodb(target,ports)

        return target_info


    def do_scan_one_target(self, target, ports):
        '''
        scan one target and everyone port
        '''
        target_info = []
        ports_list = ports.split(',')

        for p in ports_list:
            port = int(p)
            # check port open:
            check_open = mongodb_check.check_mongodb_open(
                target, port, timeout=self.args.timeout)
            if check_open == False:
                continue
            # get server info
            server_info = mongodb_check.get_mongodb_server_info(
                target, port, timeout=self.args.timeout)
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
        get_target = self.generate_target_queue()
        if get_target == False:
            return
        print "[+]start run,total target:%d" % self.queue_target.qsize()
        for i in range(self.args.threads):
            t_scan = threading.Thread(target=self.do_scan, args=())
            t_scan.setDaemon(True)
            t_scan.start()
        while True:
            self.lock_thread_num.acquire()
            thread_num = self.thread_num
            self.lock_thread_num.release()
            if thread_num <= 0:
                break
            try:
                time.sleep(0.01)
            except KeyboardInterrupt:
                self.APP_STOP = True
                self.print_result(
                    '[-]waiting for %d thread exit...' % self.thread_num)

        self.print_result("[-]finish!")
        self.APP_STOP = True

def main():
    app = mongodb_scan()
    app.run()

if __name__ == '__main__':
    main()
