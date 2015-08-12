#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from Tkinter import *
import time
import threading
#
import scan

class Application(Frame):
    '''
    mongodb scan gui
    '''
    def __print_output_msg(self,msg):
        '''
        put the message to output text
        '''
        self.text_output.insert('1.0',msg+'\n')

    def __show_output_msg(self,app):
        '''
        show all the output message
        '''
        while True:
            msg = app.get_output_msg()
            if msg == None:
                return
            else:
                self.__print_output_msg(msg)

    def __start_scan(self):
        '''
        start to scan
        '''
        ip = self.text_target.get('1.0','end')
        ip = ip.strip()
        if ip == None or ip.strip() == '':
            self.__print_output_msg(u'[-]请输入要扫描的目标地址IP，可以是单个IP或是带掩码的IP段！')
            return

        app = scan.mongodb_scan()
        app.args.target = ip
        if self.use_nmap.get() == 1:
            app.args.nmap = True
        get_target = app.generate_target_queue()
        if get_target == False:
            self.__show_output_msg(app)
            return

        msg = "[+]start run,total target:%d" % app.queue_target.qsize()
        self.__print_output_msg(msg)
        
        for i in range(app.args.threads):
            t_scan = threading.Thread(target=app.do_scan, args=())
            t_scan.setDaemon(True)
            t_scan.start()
        while True:
            app.lock_thread_num.acquire()
            thread_num = app.thread_num
            app.lock_thread_num.release()
            if thread_num <= 0:
                break
            try:
                time.sleep(0.01)
            except KeyboardInterrupt:
                app.APP_STOP = True
                app.print_result(
                    '[-]waiting for %d thread exit...' % app.thread_num)

        app.print_result("[-]finish!")
        app.APP_STOP = True

        self.__show_output_msg(app)


    def createWidgets(self):
        '''
        create gui control
        '''
        self.frame_option = Frame(height=50)
        self.frame_output = Frame(height=400)

        label_target = Label(self.frame_option,text=u'扫描目标IP:')
        label_result = Label(self.frame_output,text=u'扫描结果')
        self.text_target = Text(self.frame_option,width=20,height=1,relief=SUNKEN,bd=1)
        self.text_target.insert(INSERT,'101.251.97.144/30')
        self.use_nmap = IntVar()
        self.check_nmap = Checkbutton(self.frame_option,text=u'使用namp扫描',variable=self.use_nmap,onvalue=1,offvalue=0)

        self.button_scan = Button(self.frame_option)
        self.button_scan["text"] = u"开始扫描"
        self.button_scan['command'] = self.__start_scan
        self.button_cancel = Button(self.frame_option)
        self.button_cancel["text"] = u"取消"
        self.button_cancel["fg"]   = "red"
        self.button_cancel['command'] = self.quit

        self.text_output = Text(self.frame_output,height=20,relief=SUNKEN,bd=1)

        self.frame_option.grid(row=0,column=0,padx=5,pady=5)
        self.frame_output.grid(row=1,column=0,padx=5,pady=5)

        label_target.grid(row=0,column=0)
        self.text_target.grid(row=0,column=1)
        self.check_nmap.grid(row=0,column=2)
        self.button_scan.grid(row=0,column=3)
        self.button_cancel.grid(row=0,column=4)

        label_result.pack()
        self.text_output.pack()


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.createWidgets()

def main():
    root = Tk()
    root.title(u'mongodb未验证授权扫描器')
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()