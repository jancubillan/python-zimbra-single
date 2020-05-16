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
