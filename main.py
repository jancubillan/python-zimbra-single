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

namedconf = """
options {
	listen-on port 53 { any; };
	directory 	"/var/named";
	dump-file 	"/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	memstatistics-file "/var/named/data/named_mem_stats.txt";
	recursing-file  "/var/named/data/named.recursing";
	secroots-file   "/var/named/data/named.secroots";
	allow-query     { any; };

	recursion yes;

	forward only;
	forwarders { 8.8.8.8; 8.8.4.4; };

	dnssec-enable yes;
	dnssec-validation no;

	bindkeys-file "/etc/named.root.key";

	managed-keys-directory "/var/named/dynamic";

	pid-file "/run/named/named.pid";
	session-keyfile "/run/named/session.key";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
	type hint;
	file "named.ca";
};

zone "example.com" IN {
	type master;
	file "example.com.zone";
	allow-update { none; };
};

zone "122.168.192.in-addr.arpa" IN {
	type master;
	file "example.com.revzone";
	allow-update { none; };
};

include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
"""

with open("/etc/named.conf", "w") as i:
    i.write(namedconf.strip())

sp.run("chown", "root.named", "/etc/named.conf")
sp.run("chmod", "640", "/etc/named.conf")

examplecomzone = """
$TTL 1D
@	IN SOA	example.com. (
					; serial
					1D	; refresh
					1H	; retry
					1W	; expire
					3H )	; minimum
	NS	@
	A	${zimbra_ip}
	MX	1	${zimbra_fqdn}.
${zimbra_shortname}	A	${zimbra_ip}
"""

with open("/var/named/example.com/zone", "w") as i:
    i.write

