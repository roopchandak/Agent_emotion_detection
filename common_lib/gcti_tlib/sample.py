import sys

#this sample can be run right from inside gcti_tlib
sys.path.append('..')
import gcti_tlib
from gcti_tlib.ptlib import CreateTserverClient


def main():
    host = '10.10.15.134'
    port = '5001'
    
    dn = "100000"
    queue = "1004"
    
    ts = CreateTserverClient(host, port)
    ts.RegisterAddress(dn)
    e = ts.WaitEvent(timeout=5)
    print e
    
    ts.AgentLogin(queue, dn, dn)
    e = ts.WaitEvent(timeout=5)
    print e
    
    ts.AgentSetReady(queue, dn)
    e = ts.WaitEvent(timeout=5)
    print e
    

if __name__ == '__main__':
    main()
