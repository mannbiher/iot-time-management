import os
from datetime import datetime
import re
from socket import gethostbyaddr
import json
import time

import tldextract
from cachetools import LRUCache

from scapy.all import PcapReader, IP, TCP, DNS
from scapy.error import Scapy_Exception
from mqtt_client import MQTTClient


# Original Author of below function https://github.com/je-clark/ScapyDNSDissection
def extract_ips_from_packet(packet):
    packet_dict = {}
    query_name = packet[DNS].qd.qname

    # A qtype of 1 refers to an A record request
    if packet[DNS].qd.qtype == 1:
        for x in range(packet[DNS].ancount):
            # If rdata doesn't contain an IP address, it's just chaining to another record
            # and I don't care about it.
            if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(packet[DNS].an[x].rdata)) == None:
                continue
            # temp is a dictionary with the key being the IP address
            # and the value being a list including the record name and query name
            temp = {packet[DNS].an[x].rdata: [
                packet[DNS].an[x].rrname,
                query_name
            ]}
            packet_dict.update(temp)
        for x in range(packet[DNS].arcount):
            if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(packet[DNS].ar[x].rdata)) == None:
                continue
            temp = {packet[DNS].ar[x].rdata: [
                packet[DNS].ar[x].rrname,
                query_name
            ]}
            packet_dict.update(temp)

    # A qtype of 33 refers to a SRV request
    if packet[DNS].qd.qtype == 33:
        for x in range(packet[DNS].arcount):
            if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(packet[DNS].ar[x].rdata)) == None:
                continue
            temp = {packet[DNS].ar[x].rdata: [
                packet[DNS].ar[x].rrname,
                query_name
            ]}
            packet_dict.update(temp)
    return packet_dict


"""
{
"hostname": "",
"domain": "",
"src": "",
"dest": "",
"start": "",
"end": "",
"src_port": "",
"dest_port": ""
"size": ""
}
"""
# which ds to use for this


def get_domain(hostname):
    cloudflare_cdn = 'cdn.cloudflare.net.'
    if hostname.endswith(cloudflare_cdn):
        hostname = hostname[:-len(cloudflare_cdn)]
    return tldextract.extract(hostname)[1]


def get_hostname(pkt, dns_dict):
    """Reverse lookup on DNS Dictionary"""
    hostname = pkt['IP'].src
    if hostname in dns_dict:
        hostname = dns_dict[hostname][0].decode('utf-8')
    else:
        try:
            hostname = gethostbyaddr(hostname)[0]
        except:
            print('Reverse DNS Lookup Failed for ', hostname)
    return hostname


def create_record(pkt, dns_dict):
    """Create IoT record from packet."""
    hostname = get_hostname(pkt, dns_dict)
    domain = get_domain(hostname)
    end_time = datetime.utcfromtimestamp(
        float(pkt.time)).strftime('%Y-%m-%d %H:%M:%S.%f')
    src = pkt['IP'].src
    size = pkt['IP'].len
    dest = pkt['IP'].dst
    src_port = pkt['TCP'].sport
    dest_port = pkt['TCP'].dport
    return {
        "hostname": hostname,
        "domain": domain,
        "src": src,
        "dest": dest,
        "start": end_time,
        "end": end_time,
        "src_port": src_port,
        "dest_port": dest_port,
        "size": size
    }


def get_key(record):
    return (record['src'], record['dest'], record['src_port'], record['dest_port'])


def parse_pcap(filename, dns_dict):
    records = []
    count = 0
    with PcapReader(filename) as f:

        for pkt in f:
            if (DNS in pkt) and (pkt[DNS].qr == 1):
                dns_dict.update(extract_ips_from_packet(pkt))
            if IP in pkt and TCP in pkt:
                if pkt['IP'].src.startswith('192.168.'):
                    continue
                count += 1
                record = create_record(pkt, dns_dict)
                if records and get_key(records[-1]) == get_key(record):
                    records[-1]['end'] = record['end']
                    records[-1]['size'] += record['size']
                else:
                    records.append(record)
    print('raw count', count)
    return records


def get_files_by_mdate(path, suffix=''):
    all_files = (
        os.path.join(basedir, filename)
        for basedir, dirs, files in os.walk(path)
        for filename in files
        if filename.endswith(suffix))
    sorted_files = sorted(all_files, key=os.path.getmtime)
    return sorted_files


def main(path, topic):
    dns_dict = LRUCache(10000)
    max_usage = 0
    max_domain = ''
    client = MQTTClient(
        'a2wcug9wfns56q-ats.iot.us-east-2.amazonaws.com',
        'certificates/d6ccf7c6bd-certificate.pem.crt',
        'certificates/d6ccf7c6bd-private.pem.key',
        'certificates/AmazonRootCA1.pem')
    client.connect()
    while True:
        files = get_files_by_mdate(path, suffix='.pcap')
        for file in files:
            try:
                records = parse_pcap(file, dns_dict)
            except Scapy_Exception as err:
                if str(err) == "No data could be read!":
                    print('empty file', file, 'possibly being written by tcpdump')
                    break
                raise
            if not records: continue
            print('summarized count', len(json.dumps(records))/1000, 'KB')
            max_domain_usage = max(records, key=lambda x: x['size'])
            if max_domain_usage['size'] > max_usage:
                max_domain = max_domain_usage['domain']
                max_usage = max_domain_usage['size']
            while records:
                message = json.dumps(records[:500])
                client.publish(topic, message)
                records = records[500:]
            print('deleting file', file)
            os.remove(file)
        print('all files processed. sleeping for 1 minute.')
        print('domain', max_domain, 'usage', max_usage)
        time.sleep(60)


if __name__ == '__main__':
    # parse_pcap('data/trace-05-12-14-46-26-1620845186')
    path = '/var/tmp/pcap'
    topic = 'cs498/time/usage'
    main(path, topic)
