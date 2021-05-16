#!/usr/bin/env bash
mkdir -p /var/tmp/pcap
tcpdump -i wlan0 -nltt '(port 443 and tcp and greater 128) or (port 53 and udp)' -W 100 -G 60 -w  /var/tmp/pcap/%Y%m%d%H%M%S.pcap
