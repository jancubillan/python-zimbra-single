#!/usr/bin/env python3

import subprocess as sp
import os
import requests

zimbra_timezone = "Asia/Manila"
zimbra_fqdn = "mail.example.com"
zimbra_shortname = "mail"
zimbra_ip = "192.168.122.75"
zimbra_ptr = "75"
zimbra_subnet = "192.168.122.0/24"
zimbra_reverse_ip = "122.168.192"
zimbra_forwarders = "8.8.8.8; 8.8.4.4;"
zimbra_domain = "example.com"
zimbra_zone_path = f"/var/named/{zimbra_domain}.zone"
zimbra_revzone_path = f"/var/named/{zimbra_domain}.revzone"
zimbra_serial = "2020051601"
zimbra_network_name = "eth0"
zimbra_installer_url = "https://files.zimbra.com/downloads/8.8.15_GA/zcs-8.8.15_GA_3869.RHEL7_64.20190918004220.tgz"
zimbra_installer_path = "./files/zcs-8.8.15_GA_3869.RHEL7_64.20190918004220.tgz"
zimbra_installer_dir = "./files/zcs-8.8.15_GA_3869.RHEL7_64.20190918004220"
zimbra_admin_password = "python@zimbra2020"
zimbra_system_password = "zimbra@python2020"
zimbra_random_chars = "2020051601xyz"

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
	forwarders { %s };

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

zone "%s" IN {
	type master;
	file "%s.zone";
	allow-update { none; };
};

zone "%s.in-addr.arpa" IN {
	type master;
	file "%s.revzone";
	allow-update { none; };
};

include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
""" % (zimbra_forwarders, zimbra_domain, zimbra_domain, zimbra_reverse_ip, zimbra_domain)

with open("/etc/named.conf", "w") as i:
    i.write(namedconf.strip())

sp.run(["chown", "root.named", "/etc/named.conf"])
sp.run(["chmod", "640", "/etc/named.conf"])

example_com_zone = f"""
$TTL 1D
@       IN SOA  @ {zimbra_domain}. (
                                {zimbra_serial}      ; serial
                                        1D      ; refresh
                                        1H      ; retry
                                        1W      ; expire
                                        3H )    ; minimum
        NS      @
        A       {zimbra_ip}
        MX      1       {zimbra_fqdn}.
{zimbra_shortname}    A       {zimbra_ip}
"""

with open(f"{zimbra_zone_path}", "w") as i:
    i.write(example_com_zone.strip())

sp.run(["chown", "root.named", zimbra_zone_path])
sp.run(["chmod", "640", zimbra_zone_path])

example_com_revzone = f"""
$TTL 1D
@	IN SOA	@ {zimbra_domain}. (
				{zimbra_serial}	; serial
					1D	; refresh
					1H	; retry
					1W	; expire
					3H )	; minimum
	NS	{zimbra_domain}.
{zimbra_ptr}	PTR	{zimbra_fqdn}.
"""

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

zimbra_answers_txt = """
y
y
y
y
y
n
y
y
y
y
y
y
n
n
n
y
"""

with open("../zimbra_answers.txt", "w") as i:
    i.write(zimbra_answers_txt.strip())

sp.run(["./install.sh", "-s", "<", "../zimbra_answers.txt"])

zimbra_config_txt = f"""
AVDOMAIN="{zimbra_domain}"
AVUSER="admin@{zimbra_domain}"
CREATEADMIN="admin@{zimbra_domain}"
CREATEADMINPASS="{zimbra_admin_password}"
CREATEDOMAIN="{zimbra_domain}"
DOCREATEADMIN="yes"
DOCREATEDOMAIN="yes"
DOTRAINSA="yes"
EXPANDMENU="no"
HOSTNAME="{zimbra_fqdn}"
HTTPPORT="8080"
HTTPPROXY="TRUE"
HTTPPROXYPORT="80"
HTTPSPORT="8443"
HTTPSPROXYPORT="443"
IMAPPORT="7143"
IMAPPROXYPORT="143"
IMAPSSLPORT="7993"
IMAPSSLPROXYPORT="993"
INSTALL_WEBAPPS="service zimlet zimbra zimbraAdmin"
JAVAHOME="/opt/zimbra/common/lib/jvm/java"
LDAPBESSEARCHSET="set"
LDAPHOST="{zimbra_fqdn}"
LDAPPORT="389"
LDAPREPLICATIONTYPE="master"
LDAPSERVERID="2"
MAILBOXDMEMORY="1945"
MAILPROXY="TRUE"
MODE="https"
MYSQLMEMORYPERCENT="30"
POPPORT="7110"
POPPROXYPORT="110"
POPSSLPORT="7995"
POPSSLPROXYPORT="995"
PROXYMODE="https"
REMOVE="no"
RUNARCHIVING="no"
RUNAV="yes"
RUNCBPOLICYD="no"
RUNDKIM="yes"
RUNSA="yes"
RUNVMHA="no"
SERVICEWEBAPP="yes"
SMTPDEST="admin@{zimbra_domain}"
SMTPHOST="{zimbra_fqdn}"
SMTPNOTIFY="yes"
SMTPSOURCE="admin@{zimbra_domain}"
SNMPNOTIFY="yes"
SNMPTRAPHOST="{zimbra_fqdn}"
SPELLURL="http://{zimbra_fqdn}:7780/aspell.php"
STARTSERVERS="yes"
STRICTSERVERNAMEENABLED="TRUE"
SYSTEMMEMORY="7.6"
TRAINSAHAM="ham.{zimbra_random_chars}@{zimbra_domain}"
TRAINSASPAM="spam.{zimbra_random_chars}@{zimbra_domain}"
UIWEBAPPS="yes"
UPGRADE="yes"
USEEPHEMERALSTORE="no"
USESPELL="yes"
VERSIONUPDATECHECKS="TRUE"
VIRUSQUARANTINE="virus-quarantine.{zimbra_random_chars}@{zimbra_domain}"
ZIMBRA_REQ_SECURITY="yes"
ldap_bes_searcher_password="{zimbra_system_password}"
ldap_dit_base_dn_config="cn=zimbra"
LDAPROOTPASS="{zimbra_system_password}"
LDAPADMINPASS="{zimbra_system_password}"
LDAPPOSTPASS="{zimbra_system_password}"
LDAPREPPASS="{zimbra_system_password}"
LDAPAMAVISPASS="{zimbra_system_password}"
ldap_nginx_password="{zimbra_system_password}"
mailboxd_directory="/opt/zimbra/mailboxd"
mailboxd_keystore="/opt/zimbra/mailboxd/etc/keystore"
mailboxd_keystore_password="{zimbra_system_password}"
mailboxd_server="jetty"
mailboxd_truststore="/opt/zimbra/common/lib/jvm/java/lib/security/cacerts"
mailboxd_truststore_password="changeit"
postfix_mail_owner="postfix"
postfix_setgid_group="postdrop"
ssl_default_digest="sha256"
zimbraFeatureBriefcasesEnabled="Enabled"
zimbraFeatureTasksEnabled="Enabled"
zimbraIPMode="ipv4"
zimbraMailProxy="TRUE"
zimbraMtaMyNetworks="127.0.0.0/8 [::1]/128 {zimbra_subnet}"
zimbraPrefTimeZoneId="Asia/Singapore"
zimbraReverseProxyLookupTarget="TRUE"
zimbraVersionCheckNotificationEmail="admin@{zimbra_domain}"
zimbraVersionCheckNotificationEmailFrom="admin@{zimbra_domain}"
zimbraVersionCheckSendNotifications="TRUE"
zimbraWebProxy="TRUE"
zimbra_ldap_userdn="uid=zimbra,cn=admins,cn=zimbra"
zimbra_require_interprocess_security="1"
INSTALL_PACKAGES="zimbra-core zimbra-ldap zimbra-logger zimbra-mta zimbra-snmp zimbra-store zimbra-apache zimbra-spell zimbra-memcached zimbra-proxy "
"""

sp.run(["/opt/zimbra/libexec/zmsetup.pl", "-c", "../zimbra_config.txt"])
