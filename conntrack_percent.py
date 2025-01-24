
def get_conntrack_usage_percent():
    with open("/proc/sys/net/netfilter/nf_conntrack_max", "r") as f:
        max_conntrack = int(f.read())
    with open("/proc/sys/net/netfilter/nf_conntrack_count", "r") as f:
        current_conntrack = int(f.read())
    percentage = (current_conntrack / max_conntrack) * 100
    return percentage

def most_connected_ip(connected_ips):
    ip_count = {}
    for ip in connected_ips:
        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1
    return max(ip_count, key=ip_count.get)

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
    with open("/proc/net/nf_conntrack", "r") as f:
        conntrack_table = f.read()
    for line in conntrack_table.split("\n"):
        if 'tcp' in line and check_dport(port):
            ip = re.search(r"dst=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line).group(1)
            if ip in subnet_to_ips(subnet):
                connected_ips.append(ip)
    return connected_ips

print(get_conntrack_usage_percent())

most_connected_ip = most_connected_ip(connect_ip_parse("138.199.240.0/24", "443"))
print(most_connected_ip)