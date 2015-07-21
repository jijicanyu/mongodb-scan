# mongodb-scan

A simple mongodb sever scanner use libnmap!

usage:
python scan.py --help

optional arguments:
  
  -h, --help            show this help message and exit
  
  -u TARGET, --target TARGET scan target ip,for example: 192.168.1.1 or 192.168.1.0/24
  
  -p PORT, --port PORT  mongodb server port,for example:27017,28017,default is 27017
  
  -t THREADS, --threads THREADS thread numbers,default is 1
  
  -o TIMEOUT, --timeout TIMEOUT timeout second,default is 10
  
  -f FILE, --file FILE  read target from a logfile of scanned log file,the target is like ip:port,xxx(targetinfo)
  
  -l LOGFILE, --logfile LOGFILE output the result to logfile,default logfile name is by datetime
  
  --nmap  use libnamp do scan (install nmap first,and maybe the ctrl+c has problem)

You must set the target(-u) or file (-f) to run !

for example:python scan.py -u 192.168.1.1 --nmap

1、python lib

pip install pymongo IPy python-libnmap

2、install nmap

oxs:brew install nmap
linux:apt-get install nmap
windows:download nmap setup package

3、use

There are two way to scan, one is use --nmap,and the other don't use nmap.

Use nmap scan fast and accurate, when the namp find the mongodb server, then check the empty authentication.But you can't stop it by ctrl+c when it's running,because libnmap use Process to do nmap,if press ctrl+c,the Process won't stop normally,if you have more solvtions,thank you for correct this.

Don't use nmap way is use socket to connect the mongodb server,check the mongodb wheather open and check the empty authentication。
