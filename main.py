import os
import sys
import dotenv
import re
import subprocess
import requests
import json

def tg_send_alert(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)

def get_conntrack_usage_percent():
    with open("/proc/sys/net/netfilter/nf_conntrack_max", "r") as f:
        max_conntrack = int(f.read())
    with open("/proc/sys/net/netfilter/nf_conntrack_count", "r") as f:
        current_conntrack = int(f.read())
    percentage = (current_conntrack / max_conntrack) * 100
    return percentage

def subnet_to_ips(subnet):
    ips = []
    ip, mask = subnet.split("/")
    ip = ip.split(".")
    mask = int(mask)
    for i in range(2**(32-mask)):
        ip[3] = str(i)
        ips.append(".".join(ip))
    return ips

def check_dport(port):
    if re.search(r"dport=(\d+)", line).group(1) == port:
        return True

def connect_ip_parse(subnet, port):
    connected_ips = []
    with open("/proc/net/nf_conntrack", r) as f:
        conntrack_table = f.read()
    for line in conntrack_table.split("\n"):
        if 'tcp' in line and check_dport(port):
            ip = re.search(r"dst=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line).group(1)
            if ip in subnet_to_ips(subnet):
                connected_ips.append(ip)
    return connected_ips
                
def netplan_disable_ip():
    pass


if __name__ == "__main__":
    dotenv.load_dotenv()
