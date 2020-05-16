#!/usr/bin/env python3

from vars.main import *
from templates.main import *
import subprocess as sp
import os

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

with open("/etc/named.conf", "w") as i:
    i.write(namedconf.strip())

sp.run(["chown", "root.named", "/etc/named.conf"])
sp.run(["chmod", "640", "/etc/named.conf"])

with open(f"{zimbra_zone_path}", "w") as i:
    i.write(example_com_zone.strip())

sp.run(["chown", "root.named", zimbra_zone_path])
sp.run(["chmod", "640", zimbra_zone_path])

with open(f"{zimbra_revzone_path}", "w") as i:
    i.write(example_com_revzone.strip())

sp.run(["chown", "root.named", zimbra_revzone_path])
sp.run(["chmod", "640", zimbra_revzone_path])

sp.run(["systemctl", "--now", "enable", "named"])

sp.run(["nmcli", "con", "mod", zimbra_network_name, "ipv4.dns", "127.0.0.1"])
sp.run(["nmcli", "con", "reload"])
sp.run(["nmcli", "con", "up", zimbra_network_name])

sp.run(["yum", "install", "-y", "perl", "net-tools"])

sp.run(["wget", "-P", "./files", zimbra_installer_url])
sp.run(["tar", "-xvf", zimbra_installer_path, "-C", "./files"])
os.chdir(zimbra_installer_dir)

with open("../zimbra_answers.txt", "w") as i:
    i.write(zimbra_answers_txt.strip())

input_answers = open("../zimbra_answers.txt")
sp.run(["./install.sh", "-s"], stdin=input_answers)

with open("../zimbra_config.txt", "w") as i:
    i.write(zimbra_config_txt.strip())

sp.run(["/opt/zimbra/libexec/zmsetup.pl", "-c", "../zimbra_config.txt"])
