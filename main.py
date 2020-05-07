#!/usr/bin/env python3

import subprocess as sp
import os

zimbra_timezone = "Asia/Manila"
zimbra_fqdn = "mail.example.com"
zimbra_shortname = "mail"
zimbra_ip = "192.168.122.75"
zimbra_reverse_ip = "122.168.192"
zimbra_forwarders = "8.8.8.8; 8.8.4.4;"
zimbra_domain = "example.com"


sp.run(["timedatectl", "set-timezone", zimbra_timezone])
sp.run(["timedatectl", "set-ntp", "true"])
sp.run(["systemctl", "restart", "chronyd"])

sp.run(["hostnamectl", "set-hostname", zimbra_fqdn])
with open("/etc/hosts", "a") as i:
    i.write(f"{zimbra_ip} {zimbra_fqdn} {zimbra_shortname}\n")

utilities = ["bash-completion", "tmux", "tmux", "telnet", "bind-utils", "tcpdump", "wget", "lsof", "rsync"]
for i in utilities:
    sp.run(["yum", "install", "-y", i])

sp.run(["yum", "update", "-y"])

ports = ["25/tcp", "465/tcp", "587/tcp", "110/tcp", "995/tcp", "143/tcp", "993/tcp", "80/tcp", "443/tcp", "7071/tcp"]
for i in ports:
    sp.run(["firewall-cmd", "--permanent", "--add-port", i])

sp.run(["firewall-cmd", "--reload"])

sp.run(["systemctl", "--now", "disable", "postfix"])
sp.run(["systemctl", "mask", "postfix"])

sp.run(["yum", "install", "-y", "bind"])
os.rename("/etc/named.conf", "/etc/named.conf.bak")
