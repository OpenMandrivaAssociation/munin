Name:      munin
Version:   1.3.3
Release:   %mkrel 4
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPL
Group:     Monitoring
URL:       http://munin.projects.linpro.no/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Source0: http://download.sourceforge.net/sourceforge/munin/%{name}_%{version}.tar.gz
Source1: munin-1.2.4-sendmail-config
Source2: munin-1.2.5-hddtemp_smartctl-config
Source3: munin-node.logrotate
Source4: munin.logrotate
Source5: munin-node.init
Patch1: munin-1.2.4-conf.patch
Patch2: munin-nocheck-user.patch
Patch3: munin-plugins-variousfix.patch
Patch4: munin-cgi-graph-fix-lock.patch
BuildArch: noarch
Requires: rrdtool
Requires: logrotate
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires: html2text htmldoc

%description
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains the grapher/gatherer. You will only need one instance of
it in your network. It will periodically poll all the nodes in your network
it's aware of for data, which it in turn will use to create graphs and HTML
pages, suitable for viewing with your graphical web browser of choice.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool. 

%package node
Group: Monitoring
Summary: Network-wide graphing framework (node)
Requires: procps >= 2.0.7
Requires: sysstat
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires: perl-Net-SNMP >= 5.2.0

%description node
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains node software. You should install it on all the nodes
in your network. It will know how to extract all sorts of data from the
node it runs on, and will wait for the gatherer to request this data for
further processing.

It includes a range of plugins capable of extracting common values such as
cpu usage, network usage, load average, and so on. Creating your own plugins
which are capable of extracting other system-specific values is very easy,
and is often done in a matter of minutes. You can also create plugins which
relay information from other devices in your network that can't run Munin,
such as a switch or a server running another operating system, by using
SNMP or similar technology.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool. 

%prep
%setup -q
%patch1 -p1
%patch2 -p0 -b .nochown
%patch3 -p0 -b .pluginsfix
%patch4 -p0 -b .cgi-lock

%build

%make \
	DOCDIR={_docdir}/%{name}-%{version} \
	MANDIR=%{_mandir} \
    HTMLDIR=%_var/www/%name \
    CGIDIR=%_var/www/cgi-bin \
    PREFIX=%_prefix \
    CONFDIR=%_sysconfdir/munin \
    DBDIR=%_localstatedir/lib/munin \
    LIBDIR=%_datadir/munin \
    PERLLIB=%perl_vendorlib \
	CONFIG=dists/redhat/Makefile.config build 

%install

## Node
make 	CONFIG=dists/redhat/Makefile.config \
    CHOWN=/bin/true \
    CHGRP=/bin/true \
	DOCDIR=%{buildroot}%{_docdir}/%{name}-%{version} \
	MANDIR=%{buildroot}%{_mandir} \
    HTMLDIR=%{buildroot}/%_var/www/%name \
    CGIDIR=%{buildroot}/%_var/www/cgi-bin \
    PREFIX=%{buildroot}%_prefix \
    LIBDIR=%{buildroot}%_datadir/munin \
    CONFDIR=%{buildroot}%_sysconfdir/munin \
    DBDIR=%{buildroot}%_localstatedir/lib/munin \
    PERLLIB=%{buildroot}%perl_vendorlib \
	DESTDIR=%{buildroot} \
    	install-main install-node install-node-plugins install-doc install-man

mkdir -p %{buildroot}/%_initrddir
mkdir -p %{buildroot}/etc/munin/plugins
mkdir -p %{buildroot}/etc/munin/plugin-conf.d
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}/var/lib/munin
mkdir -p %{buildroot}/var/log/munin

# 
# don't enable munin-node by default. 
#
cp %{SOURCE5}  %{buildroot}/%_initrddir/%{name}-node
#chmod 755 %{buildroot}/etc/rc.d/init.d/munin-node

install -m0644 dists/tarball/plugins.conf %{buildroot}/etc/munin/
install -m0644 dists/tarball/plugins.conf %{buildroot}/etc/munin/plugin-conf.d/munin-node

# 
# remove the Sybase plugin for now, as they need perl modules 
# that are not in extras. We can readd them when/if those modules are added. 
#
rm -f %{buildroot}/usr/share/munin/plugins/sybase_space

## Server
make 	CONFIG=dists/redhat/Makefile.config \
    CHOWN=/bin/true \
    CHGRP=/bin/true \
    HTMLDIR=%{buildroot}/%_var/www/%name \
    CGIDIR=%{buildroot}/%_var/www/cgi-bin \
	DESTDIR=%{buildroot} \
    PREFIX=%{buildroot}%_prefix \
    LIBDIR=%{buildroot}%_datadir/munin \
    CONFDIR=%{buildroot}%_sysconfdir/munin \
    DBDIR=%{buildroot}%_localstatedir/lib/munin \
    PERLLIB=%{buildroot}%perl_vendorlib \
	install-main

mkdir -p %{buildroot}/var/www/munin
mkdir -p %{buildroot}/var/log/munin
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}%_webappconfdir

cat > %{buildroot}%_webappconfdir/%name.conf <<EOF
Alias /munin /var/www/munin
<Directory /var/www/munin>
    Order deny,allow
    Allow from 127.0.0.1
</Directory>

EOF

install -m 0644 dists/redhat/munin.cron.d %{buildroot}/etc/cron.d/munin
install -m 0644 server/style.css %{buildroot}/var/www/munin
install -m 0644 ChangeLog %{buildroot}%{_docdir}/%{name}-%{version}/ChangeLog
# install config for sendmail under fedora
install -m 0644 %{SOURCE1} %{buildroot}/etc/munin/plugin-conf.d/sendmail
# install config for hddtemp_smartctl
install -m 0644 %{SOURCE2} %{buildroot}/etc/munin/plugin-conf.d/hddtemp_smartctl
# install logrotate scripts
install -m 0644 %{SOURCE3} %{buildroot}/etc/logrotate.d/munin-node
install -m 0644 %{SOURCE4} %{buildroot}/etc/logrotate.d/munin

cat >%{buildroot}/etc/munin/plugin-conf.d/fw <<EOF
[fw*]
    user root
EOF

%clean
chmod u+rX -R $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT

%pre node
%_pre_useradd %name /var/lib/%name /bin/false

%postun node
%_postun_userdel %name

%post node
/usr/sbin/munin-node-configure --shell | sh
%_post_service %name-node

%preun node
%_preun_service %name-node

%pre
%_pre_useradd %name /var/lib/%name /bin/false

%postun
%_postun_userdel %name
%_postun_webapp

%post
%_post_webapp

%preun
 
%files
%defattr(-, root, root)
%doc %_docdir/*
%{_bindir}/munin-cron
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{_datadir}/munin/VeraMono.ttf
%{perl_vendorlib}/Munin.pm
%dir %{_sysconfdir}/munin
%dir %{_sysconfdir}/munin/templates
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/munin/templates/*
%config(noreplace) %{_sysconfdir}/cron.d/munin
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/munin
/var/www/cgi-bin/munin-cgi-graph
%attr(-, munin, munin) /var/www/munin
%attr(-, munin, munin) %dir /var/lib/munin
%attr(-, munin, munin) %dir /var/run/munin
%attr(-, munin, munin) %dir /var/log/munin
%{_mandir}/man8/munin-graph*
%{_mandir}/man8/munin-update*
%{_mandir}/man8/munin-limits*
%{_mandir}/man8/munin-html*
%{_mandir}/man8/munin-cron*
%{_mandir}/man5/munin.conf*

%files node
%defattr(-, root, root)
%doc %_docdir/*
%dir %{_sysconfdir}/munin
%dir %{_sysconfdir}/munin/plugins
%config(noreplace) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %{_sysconfdir}/munin/plugin-conf.d
%config(noreplace) %{_sysconfdir}/munin/plugins.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/munin-node
%_initrddir/%name-node
%{_sbindir}/munin-run
%{_sbindir}/munin-node
%{_sbindir}/munin-node-configure
%{_sbindir}/munin-node-configure-snmp
%{perl_vendorlib}/Munin
%attr(-,munin,munin) %dir /var/log/munin
%attr(-,munin,munin) %dir /var/lib/munin
%dir %attr(-,munin,munin) /var/lib/munin/plugin-state
%dir %{_datadir}/munin
%{_datadir}/munin/plugins
%{_mandir}/man8/munin-run*
%{_mandir}/man8/munin-node*
%{_mandir}/man5/munin-node*
