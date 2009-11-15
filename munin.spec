%define beta alpha2
%define _requires_exceptions perl(\\(Munin::Master::LimitsOld\\|CGI::Fast\\))

Name:      munin
Version:   1.4.0
Release:   %mkrel 0.%{beta}.2
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPLv2
Group:     Monitoring
URL:       http://munin.projects.linpro.no/
Source0: http://download.sourceforge.net/sourceforge/munin/%{name}_%{version}-%{beta}.tar.gz
Source5: munin-node.init
Patch6: 380-munin-graph-utf8.patch
BuildRequires: html2text
BuildRequires: htmldoc
BuildRequires: java-devel-openjdk
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}

%description
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

%package master
Group: Monitoring
Summary: Network-wide graphing framework (master)
Requires: rrdtool
Requires: %{name} = %{version}-%{release}
Obsoletes: %{name} < 1.4.0

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

%prep
%setup -q -n %{name}-%{version}-%{beta}
#%patch6 -p0 -b .utf8

%build
make \
    CONFIG=dists/redhat/Makefile.config \
    PREFIX=%{_prefix} \
    DOCDIR={_docdir}/%{name} \
    MANDIR=%{_mandir} \
    HTMLDIR=%{_localstatedir}/lib/munin/html \
    DBDIR=%{_localstatedir}/lib/munin/data \
    PLUGSTATE=%{_localstatedir}/lib/munin/plugin-state \
    CGIDIR=%{_datadir}/%{name}/cgi \
    CONFDIR=%{_sysconfdir}/munin \
    LIBDIR=%{_datadir}/munin \
    PERLLIB=%{perl_vendorlib} \
    HOSTNAME=localhost \
    build

%install
rm -rf %{buildroot}

## Node
make \
    CONFIG=dists/redhat/Makefile.config \
    CHOWN=/bin/true \
    CHGRP=/bin/true \
    DOCDIR=%{buildroot}%{_docdir}/%{name} \
    MANDIR=%{buildroot}%{_mandir} \
    HTMLDIR=%{buildroot}%{_localstatedir}/lib/munin/html \
    DBDIR=%{buildroot}%{_localstatedir}/lib/munin/data \
    PLUGSTATE=%{buildroot}%{_localstatedir}/lib/munin/plugin-state \
    CGIDIR=%{buildroot}%{_datadir}/%{name}/cgi \
    PREFIX=%{buildroot}%{_prefix} \
    LIBDIR=%{buildroot}%{_datadir}/munin \
    CONFDIR=%{buildroot}%{_sysconfdir}/munin \
    PERLLIB=%{buildroot}%{perl_vendorlib} \
    DESTDIR=%{buildroot} \
    HOSTNAME=localhost \
    install install-doc

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE5} %{buildroot}/%{_initrddir}/munin-node

# plugins configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/munin/plugin-conf.d
install -m 644 dists/tarball/plugins.conf \
    %{buildroot}%{_sysconfdir}/munin/plugin-conf.d/munin-node

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/hddtemp_smartctl <<EOF
[hddtemp_smartctl]
user root
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/sendmail <<EOF
[sendmail*]
user root
env.mspqueue %{_localstatedir}/spool/clientmqueue
EOF

cat >%{buildroot}%{_sysconfdir}/munin/plugin-conf.d/fw <<EOF
[fw*]
user root
EOF

# remove the Sybase plugin for now, as they need perl modules 
# that are not in extras. We can readd them when/if those modules are added. 
#
rm -f %{buildroot}/usr/share/munin/plugins/sybase_space

# state and log directories
install -d -m 755 %{buildroot}%{_localstatedir}/lib/munin
install -d -m 755 %{buildroot}%{_localstatedir}/log/munin

# apache configuration
rm -f %{buildroot}%{_localstatedir}/lib/munin/html/.htaccess

install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%_webappconfdir/%{name}.conf <<EOF
Alias /munin %{_localstatedir}/lib/munin/html
<Directory %{_localstatedir}/lib/munin/html>
    Order deny,allow
    Allow from all
</Directory>
EOF

# cron task
install -d -m 755 %{buildroot}%{_sysconfdir}/cron.d
install -m 644 dists/redhat/munin.cron.d %{buildroot}%{_sysconfdir}/cron.d/munin

# logrotate
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/munin-node <<EOF
/var/log/munin/munin-node.log {
}
EOF
cat > %{buildroot}%{_sysconfdir}/logrotate.d/munin <<EOF
/var/log/munin/munin-update.log /var/log/munin/munin-graph.log /var/log/munin/munin-html.log /var/log/munin/munin-limits.log {
}
EOF

# add changelog to installed documentation files
install -m 644 ChangeLog %{buildroot}%{_docdir}/%{name}/ChangeLog

%clean
rm -rf %{buildroot}

%pre master
if [ $1 = 2 ]; then
    # on upgrade, move data to new location if needed
    if [ ! -d %{_localstatedir}/lib/%{name}/data ]; then
        cd %{_localstatedir}/lib/%{name}
        mkdir data
        for i in *; do
            [ $i == plugin-state ] && continue
            [ $i == data ] && continue
            mv $i data
        done
    fi
fi

%pre node
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%postun node
%_postun_userdel %{name}

%post node
if [ $1 = 1 ]; then
    /usr/sbin/munin-node-configure --shell | sh
fi
%_post_service munin-node

%preun node
%_preun_service munin-node

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%postun
%_postun_userdel %{name}
%_postun_webapp

%post
%_post_webapp

%files
%defattr(-, root, root)
%doc %{_docdir}/%{name}
%dir %{_datadir}/munin
%dir %{_sysconfdir}/munin
%dir %{_localstatedir}/lib/munin
%dir %attr(-,munin,munin) %{_localstatedir}/log/munin
%{perl_vendorlib}/Munin

%files master
%defattr(-, root, root)
%{_bindir}/munin-cron
%{_bindir}/munin-check
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{_datadir}/munin/munin-jmx-plugins.jar
%{_datadir}/munin/cgi
%{_datadir}/munin/VeraMono.ttf
%dir %{_sysconfdir}/munin/templates
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%config(noreplace) %{_sysconfdir}/munin/templates/*
%config(noreplace) %{_sysconfdir}/cron.d/munin
%config(noreplace) %{_sysconfdir}/logrotate.d/munin
%attr(-,munin,munin) %{_localstatedir}/run/munin
%attr(-,munin,munin) %{_localstatedir}/lib/munin/data
%attr(-,munin,munin) %{_localstatedir}/lib/munin/html
%{_mandir}/man8/munin.8*
%{_mandir}/man8/munin-graph.8*
%{_mandir}/man8/munin-update.8*
%{_mandir}/man8/munin-limits.8*
%{_mandir}/man8/munin-html.8*
%{_mandir}/man8/munin-cron.8*
%{_mandir}/man8/munin-check.8*
%{_mandir}/man5/munin.conf.5*
%{_mandir}/man3/Munin::*

%files node
%doc %{_docdir}/%{name}
%dir %{_sysconfdir}/munin/plugins
%dir %{_sysconfdir}/munin/plugin-conf.d
%config(noreplace) %{_sysconfdir}/munin/munin-node.conf
%config(noreplace) %{_sysconfdir}/munin/plugin-conf.d/*
%config(noreplace) %{_sysconfdir}/logrotate.d/munin-node
%{_initrddir}/munin-node
%{_bindir}/munindoc
%{_sbindir}/munin-run
%{_sbindir}/munin-node
%{_sbindir}/munin-node-configure
%attr(-,munin,munin) %{_localstatedir}/lib/munin/plugin-state
%{_datadir}/munin/plugins
%{_mandir}/man1/munindoc.1*
%{_mandir}/man1/munin-run.1*
%{_mandir}/man1/munin-node.1*
%{_mandir}/man1/munin-node-configure.1*
%{_mandir}/man5/munin-node.conf.5*
