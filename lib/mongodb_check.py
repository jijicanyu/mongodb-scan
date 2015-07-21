#!/usr/bin/env python
#-*- coding: utf-8 -*-
import socket
import pymongo

def check_mongodb_open(host, port,timeout=3):
    '''
    use socket to fast check the mongodb server is open
    '''
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check_target = (host, port)
    soc.settimeout(timeout)

    port_status = soc.connect_ex(check_target)
    if port_status == 0:
    	soc.close()
        return True
    else:
        return False
    
def get_mongodb_server_info(host,port,username=None,password=None,timeout=3):
    '''
    use pymongo to connect server and get server info
    '''
    server_info = None
    connection_string = ''
    if username == None or password == None or username == '' or password == '':
        connection_string = "mongodb://%s:%d" % (host,port)
    else:
        connection_string = "mongodb://%s:%s@%s:%d" % (username,password,host,port)
    #set timeout value
    connection_string += "/?socketTimeoutMS=%d&connectTimeoutMS=%d&serverSelectionTimeoutMS=%d" %(timeout*1000,timeout*1000,timeout*1000)

    try:
        client = pymongo.MongoClient(connection_string)
        server_info = client.server_info()
        client.close()
    except :
        #raise
        pass 

    return server_info

def main():
    check = check_mongodb_open('101.251.102.66',27017)
    print check
    server_info = get_mongodb_server_info('101.251.102.66',27017,'','')
    print server_info

if __name__ == '__main__':
    main()

