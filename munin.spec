%define _requires_exceptions perl(\\(Munin::Master::LimitsOld\\|CGI::Fast\\|DBD::Pg\\))

Name:      munin
Version:   2.0.9
Release:   %mkrel 1
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPLv2
Group:     Monitoring
URL:       http://munin.projects.linpro.no/
Source0:   http://download.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz
Source1:    munin-node.service
Source2:    munin-asyncd.service
Source3:    munin-fcgi-html.service
Source4:    munin-fcgi-graph.service
Source5:    munin.tmpfiles
Patch0:     munin-2.0.7-use-system-fonts.patch
Requires(post):  rpm-helper
Requires(preun): rpm-helper
BuildRequires: html2text
BuildRequires: htmldoc
BuildRequires: java-devel
BuildRequires: perl(Module::Build)
BuildArch: noarch

%description
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

%package master
Group: Monitoring
Summary: Network-wide graphing framework (master)
Requires: rrdtool
Requires: %{name} = %{version}-%{release}
Suggests:   perl(CGI::Fast)
Requires:   perl(FCGI)
Requires:   spawn-fcgi
Requires(post): rpm-helper
Requires(postun): rpm-helper

%description master
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains the grapher/gatherer. You will only need one instance of
it in your network. It will periodically poll all the nodes in your network
it's aware of for data, which it in turn will use to create graphs and HTML
pages, suitable for viewing with your graphical web browser of choice.

%package node
Group: Monitoring
Summary: Network-wide graphing framework (node)
Requires: procps >= 2.0.7
Requires: sysstat
Requires: %{name} = %{version}-%{release}
Requires(post):  rpm-helper
Requires(preun): rpm-helper

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

%package java-plugins
Group:      Monitoring
Summary:    java-plugins for munin
Requires:   %{name}-node = %{version}-%{release}
Requires:   jpackage-utils

%description java-plugins
java-plugins for munin-node.

%package async
Group:      Monitoring
Summary:    Asynchronous client tools for munin
Requires:   %{name}-node = %{version}-%{release}

%description async
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.
This package contains the tools necessary for setting up an asynchronous
client / spooling system

%prep
%setup -q
%patch0 -p 1

%build
make \
    CONFIG=Makefile.config \
    PREFIX=%{_prefix} \
    DOCDIR=%{_docdir}/%{name} \
    MANDIR=%{_mandir} \
    HTMLDIR=%{_localstatedir}/lib/munin/html \
    DBDIR=%{_localstatedir}/lib/munin/data \
    PLUGSTATE=%{_localstatedir}/lib/munin/plugin-state \
    LOGDIR=%{_localstatedir}/log/munin \
    STATEDIR=/run/munin \
    CGIDIR=%{_datadir}/%{name}/cgi \
    CONFDIR=%{_sysconfdir}/munin \
    LIBDIR=%{_datadir}/munin \
    PERLLIB=%{perl_vendorlib} \
    HOSTNAME=localhost \
    build

%install
rm -rf %{buildroot}

# ugly hack
cp common/blib/lib/Munin/Common/Defaults.pm Defaults.pm

make \
    CONFIG=Makefile.config \
    PREFIX=%{buildroot}%{_prefix} \
    DOCDIR=%{buildroot}%{_docdir}/%{name} \
    MANDIR=%{buildroot}%{_mandir} \
    HTMLDIR=%{buildroot}%{_localstatedir}/lib/munin/html \
    DBDIR=%{buildroot}%{_localstatedir}/lib/munin/data \
    PLUGSTATE=%{buildroot}%{_localstatedir}/lib/munin/plugin-state \
    CGIDIR=%{buildroot}%{_datadir}/%{name}/cgi \
    LOGDIR=%{buildroot}%{_localstatedir}/log/munin \
    STATEDIR=%{buildroot}/run/munin \
    LIBDIR=%{buildroot}%{_datadir}/munin \
    CONFDIR=%{buildroot}%{_sysconfdir}/munin \
    PERLLIB=%{buildroot}%{perl_vendorlib} \
    DESTDIR=%{buildroot} \
    HOSTNAME=localhost \
    CHOWN=/bin/true \
    CHGRP=/bin/true \
    CHMOD=/bin/true \
    CHECKUSER=true \
    CHECKGROUP=true \
    install install-doc

cp -f Defaults.pm %{buildroot}%{perl_vendorlib}/Munin/Common/Defaults.pm

# move template and static files in data
mv %{buildroot}%{_sysconfdir}/munin/templates %{buildroot}%{_datadir}/%{name}
mv %{buildroot}%{_sysconfdir}/munin/static %{buildroot}%{_datadir}/%{name}

# configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/munin/munin-conf.d
perl -pi \
    -e 's|^# ?tmpldir.*|tmpldir %{_datadir}/%{name}/templates|;' \
    -e 's|^# ?staticdir.*|staticdir %{_datadir}/%{name}/static|;' \
    -e 's|^# ?cgiurl_graph.*|cgiurl_graph /munin/cgi/munin-cgi-graph|;' \
   %{buildroot}%{_sysconfdir}/munin/munin.conf

# systemd service
install -d -m 755 %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/munin-node.service
install -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/munin-asyncd.service
install -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/munin-fcgi-html.service
install -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/munin-fcgi-graph.service

install -D -m 644 %{SOURCE5} %{buildroot}%{_prefix}/lib/tmpfiles.d/%{name}.conf

# plugins configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/munin/plugin-conf.d
cat > %{buildroot}%{_sysconfdir}/munin/plugin-conf.d/munin-node <<EOF
[diskstats]
user munin

[iostat_ios]
user munin
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/hddtemp_smartctl <<EOF
[hddtemp_smartctl]
user root
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/sendmail <<EOF
[sendmail*]
user root
env.mspqueue %{_localstatedir}/spool/clientmqueue
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/postfix <<EOF
[postfix*]
user root
env.logfile info.log
env.logdir /var/log/mail
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/df <<EOF
[df*]
env.exclude none unknown iso9660 squashfs udf romfs ramfs debugfs binfmt_misc rpc_pipefs fuse.gvfs-fuse-daemon
EOF

# remove the Sybase plugin for now, as it requires unavailable perl modules
rm -f %{buildroot}/usr/share/munin/plugins/sybase_space

# move munin-asyncd to /usr/sbin/ (FHS)
mv %{buildroot}/%{_datadir}/munin/munin-asyncd \
    %{buildroot}/%{_sbindir}/munin-asyncd

# remove duplicated fonts
rm %{buildroot}/usr/share/munin/DejaVuSans*.ttf

# additional configuration directory
install -d -m 755 %{buildroot}%{_sysconfdir}/munin/munin-conf.d

# state and log directories
install -d -m 755 %{buildroot}%{_localstatedir}/lib/munin
install -d -m 775 %{buildroot}%{_localstatedir}/lib/munin/data/cgi-tmp
install -d -m 775 %{buildroot}%{_localstatedir}/log/munin

# apache configuration
rm -f %{buildroot}%{_localstatedir}/lib/munin/html/.htaccess

install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
ScriptAlias /munin/cgi    %{_datadir}/munin/cgi
Alias       /munin/static %{_datadir}/munin/static
Alias       /munin        %{_localstatedir}/lib/munin/html

<Directory %{_datadir}/munin/cgi>
    Options ExecCGI
    Require all granted
</Directory>

<Directory %{_datadir}/munin/static>
    Require all granted
</Directory>

<Directory %{_localstatedir}/lib/munin/html>
    Require all granted
</Directory>
EOF

# cron task
install -d -m 755 %{buildroot}%{_sysconfdir}/cron.d
cat > %{buildroot}%{_sysconfdir}/cron.d/munin <<EOF
*/5 * * * *     munin /usr/bin/munin-cron
EOF

# logrotate
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/munin-node <<EOF
/var/log/munin/munin-node.log {
    postrotate
        service munin-node reload
    endscript

}
EOF
cat > %{buildroot}%{_sysconfdir}/logrotate.d/munin <<EOF
/var/log/munin/munin-update.log /var/log/munin/munin-graph.log /var/log/munin/munin-html.log /var/log/munin/munin-limits.log {
}
EOF

# add changelog to installed documentation files
install -m 644 ChangeLog %{buildroot}%{_docdir}/%{name}/ChangeLog

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%post
systemd-tmpfiles --create %{name}.conf

%postun
%_postun_userdel %{name}

%post node
if [ $1 = 1 ]; then
    /usr/sbin/munin-node-configure --shell | sh
fi
%_post_service munin-node

%preun node
%_preun_service munin-node

%files
%doc %{_docdir}/%{name}
%dir %{_datadir}/munin
%dir %{_sysconfdir}/munin
%dir %{_localstatedir}/lib/munin
%attr(-,munin,apache) %{_localstatedir}/log/munin
%{_prefix}/lib/tmpfiles.d/munin.conf
%{perl_vendorlib}/Munin
%exclude %{perl_vendorlib}/Munin/Master
%exclude %{perl_vendorlib}/Munin/Node
%exclude %{perl_vendorlib}/Munin/Plugin
%exclude %{perl_vendorlib}/Munin/Plugin.pm

%files master
%{_bindir}/munin-cron
%{_bindir}/munin-check
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{_datadir}/munin/munin-datafile2storable
%{_datadir}/munin/munin-storable2datafile
%{_datadir}/munin/cgi
%{perl_vendorlib}/Munin/Master
%{_datadir}/munin/static
%{_datadir}/munin/templates
%{_datadir}/munin/munin-graph
%{_unitdir}/munin-fcgi-graph.service
%{_unitdir}/munin-fcgi-html.service
%dir %{_sysconfdir}/munin/munin-conf.d
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%config(noreplace) %{_sysconfdir}/cron.d/munin
%config(noreplace) %{_sysconfdir}/logrotate.d/munin
%attr(-,munin,munin) %{_localstatedir}/lib/munin/data
%attr(-,munin,munin) %{_localstatedir}/lib/munin/html
%{_mandir}/man8/munin.8*
%{_mandir}/man8/munin-update.8*
%{_mandir}/man8/munin-limits.8*
%{_mandir}/man8/munin-html.8*
%{_mandir}/man8/munin-cron.8*
%{_mandir}/man8/munin-check.8*
%{_mandir}/man8/munin-graph.8*
%{_mandir}/man5/munin.conf.5*
%{_mandir}/man3/Munin::*

%files node
#% doc %{_docdir}/%{name}
%dir %{_sysconfdir}/munin/plugins
%dir %{_sysconfdir}/munin/plugin-conf.d
%config(noreplace) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %{_sysconfdir}/munin/plugin-conf.d/*
%config(noreplace) %{_sysconfdir}/logrotate.d/munin-node
%{_unitdir}/munin-node.service
%{_bindir}/munindoc
%{_sbindir}/munin-run
%{_sbindir}/munin-node
%{_sbindir}/munin-node-configure
%{_sbindir}/munin-sched
%attr(-,munin,munin) %{_localstatedir}/lib/munin/plugin-state
%{_datadir}/munin/plugins
%exclude %{_datadir}/munin/plugins/jmx_
%{perl_vendorlib}/Munin/Node
%{perl_vendorlib}/Munin/Plugin
%{perl_vendorlib}/Munin/Plugin.pm
%{_mandir}/man1/munindoc.1*
%{_mandir}/man1/munin-run.1*
%{_mandir}/man1/munin-node.1*
%{_mandir}/man1/munin-node-configure.1*
%{_mandir}/man1/munin-sched.1*
%{_mandir}/man5/munin-node.conf.5*

%files java-plugins
%{_datadir}/munin/munin-jmx-plugins.jar
%{_datadir}/munin/plugins/jmx_

%files async
%{_unitdir}/munin-asyncd.service
%{_datadir}/munin/munin-async
%{_sbindir}/munin-asyncd
