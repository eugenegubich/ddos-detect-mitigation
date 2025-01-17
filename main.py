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

def connect_ip_parse():
    # get conntrack 

def netplan_disable_ip():

if __name__ == "__main__":
    dotenv.load_dotenv()