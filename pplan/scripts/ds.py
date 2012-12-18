import sys, struct, re
import dpkt

sources = set()

infile = open('dockserver_packets', 'r')
pcap_reader = dpkt.pcap.Reader(infile)
pkt_list = []
for ts, buf in pcap_reader:
        eth = dpkt.ethernet.Ethernet(buf)
        if type(eth.data) == dpkt.ip.IP:
            ip = eth.data
            if type(ip.data) == dpkt.gre.GRE:
                gre = ip.data
                ppp = gre.data
                if type(ppp.data) == dpkt.ip.IP:
                    ip2 = ppp.data
                    tcp = ip2.data
                    pkt_list.append(('to_ds', tcp.data))
                    print [ord(c) for c in ip2.src], [ord(c) for c in ip2.dst]
                elif type(ppp.data) == str:
                    print 'got'
                    start_i = ppp.data.find(r'<?xml')
                    if start_i != -1:
                        pkt_str = ppp.data[start_i:]
                        print pkt_str
                        pkt_list.append(('from_ds', pkt_str))
                else:
                    dieeeee
            else:
                src_addr = tuple([ord(c) for c in ip.src])
                if src_addr == (128, 125, 36, 100):
                    pass
                else:
                    pass
                

    
