#!/usr/bin/env python
#-*- coding:utf-8 -*-
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import time

def __do_scan(targets, options):
    '''
    do scan a target by nmap
    '''
    parsed = None
    nmproc = NmapProcess(targets=targets, options=options)
    nmproc.run()
    
    try:
        parsed = NmapParser.parse(nmproc.stdout)
    except NmapParserException as e:
        print("Exception raised while parsing scan: {0}".format(e.msg))

    return parsed

def __parse_scan(nmap_report):
    '''
    parser a nmap scan stdout,and return report by host's open port
    '''
    reports=[]
    for host in nmap_report.hosts:
        for serv in host.services:
            if serv.state == 'open':
                srv = serv.service 
                if len(serv.banner):
                	srv += serv.banner
                reports.append((host.address,serv.port,srv))

    return reports

def __print_scan(nmap_report):
    '''
    print a scan report
    '''
    print("Starting Nmap {0} ( http://nmap.org ) at {1}".format(
        nmap_report.version,
        nmap_report.started))

    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        print("Nmap scan report for {0} ({1})".format(
            tmp_host,
            host.address))
        print("Host is {0}.".format(host.status))
        print("  PORT     STATE         SERVICE")

        for serv in host.services:
            pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(
                    str(serv.port),
                    serv.protocol,
                    serv.state,
                    serv.service)
            if len(serv.banner):
                pserv += " ({0})".format(serv.banner)
            print(pserv)
    print(nmap_report.summary)

def nmap_mongodb(host,port):
    '''
    do a mongodb scan  by namp
    '''
    options = '-sV -Pn -p%s' % port
    report = __do_scan(host,options)
    r = []
    if report:
        r = __parse_scan(report)
        #print r
    return r

def main():
    r = nmap_mongodb('101.251.112.125','27017')
    print r


if __name__ == '__main__':
    main()