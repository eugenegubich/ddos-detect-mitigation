import os
import sys
import dotenv
import re
import subprocess
import requests
import json
import time
import socket

def get_tg_api_ip():
    ip_address = socket.gethostbyname("api.telegram.org")
    return ip_address

def tg_send_alert(message, token, chat_id, tg_api_ip):
    time.sleep(20)
    try:
        attempts = 0
        while attempts < 200:
            response = requests.get(f"https://{tg_api_ip}/bot{token}/sendMessage?chat_id={chat_id}&text={message}", headers={"Host": "api.telegram.org"}, verify=False)
            if response.status_code == 200:
                break
            attempts += 1
            time.sleep(1)
    except Exception as e:
        print(f"Error sending alert: {e}")

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

def check_dport(line, port):
    if re.search(r"dport=(\d+)", line).group(1) == port:
        return True

def connect_ip_parse(subnet, port):
    connected_ips = []
    with open("/proc/net/nf_conntrack", "r") as f:
        conntrack_table = f.read()
    for line in conntrack_table.split("\n"):
        if 'tcp' in line and check_dport(line, port):
            ip_re = re.search(r"dst=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
            if ip_re:
                ip = ip_re.group(1)
                if ip in subnet_to_ips(subnet):
                    connected_ips.append(ip)
    return connected_ips

def most_connected_ip(connected_ips):
    ip_count = {}
    for ip in connected_ips:
        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1
    max_ip = max(ip_count, key=ip_count.get)
    result = [max_ip, ip_count[max_ip]]
    return result
                
def netplan_disable_ip(conf_path, address):
    with open(conf_path, 'r') as file:
            lines = file.readlines()
    with open(conf_path, 'w') as file:
        for line in lines:
            if address in line:
                file.write('# ' + line)
            else:
                file.write(line)
    os.system("netplan apply")


if __name__ == "__main__":
    dotenv.load_dotenv(dotenv.find_dotenv())
    if get_conntrack_usage_percent() > int(os.getenv("THRESHOLD")):
        tg_api_ip = get_tg_api_ip()
        most_connected_ip = most_connected_ip(connect_ip_parse(os.getenv("LOCAL_IPS_SUBNET"), os.getenv("LOCAL_PORT")))
        netplan_disable_ip(os.getenv("NETPLAN_CONFIG_PATH"), most_connected_ip[0])
        hostname = socket.gethostname()
        message = f"Disabled {most_connected_ip[0]} with {most_connected_ip[1]} connections, host {hostname}, conntrack usage {get_conntrack_usage_percent()}%"
        tg_send_alert(message, os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"), tg_api_ip)
