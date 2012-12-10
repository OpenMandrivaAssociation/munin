%define _requires_exceptions perl(\\(Munin::Master::LimitsOld\\|CGI::Fast\\))

Name:      munin
Version:   1.4.7
Release:   %mkrel 1
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPLv2
Group:     Monitoring
URL:       http://munin.projects.linpro.no/
Source0: http://download.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz
Source5: munin-node.init
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires: html2text
BuildRequires: htmldoc
BuildRequires: java-devel-openjdk
BuildRequires: perl(Module::Build)
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
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(post): rpm-helper
Requires(preun): rpm-helper
Obsoletes: munin-plugins-slapd

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
%setup -q -n %{name}-%{version}

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
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
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

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

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

%postun
%_postun_userdel %{name}


%post master
%_post_webapp

%postun master
%_postun_webapp

%pre node
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%post node
if [ $1 = 1 ]; then
    /usr/sbin/munin-node-configure --shell | sh
fi
%_post_service munin-node

%preun node
%_preun_service munin-node

%postun node
%_postun_userdel %{name}

%files
%defattr(-, root, root)
%doc %{_docdir}/%{name}
%dir %{_datadir}/munin
%dir %{_sysconfdir}/munin
%dir %{_localstatedir}/lib/munin
%attr(-,munin,munin) %{_localstatedir}/run/munin
%attr(-,munin,munin) %{_localstatedir}/log/munin
%{perl_vendorlib}/Munin
%exclude %{perl_vendorlib}/Munin/Master
%exclude %{perl_vendorlib}/Munin/Node
%exclude %{perl_vendorlib}/Munin/Plugin
%exclude %{perl_vendorlib}/Munin/Plugin.pm

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
%{_datadir}/munin/DejaVuSans.ttf
%{_datadir}/munin/DejaVuSansMono.ttf
%{perl_vendorlib}/Munin/Master
%dir %{_sysconfdir}/munin/templates
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%config(noreplace) %{_sysconfdir}/munin/templates/*
%config(noreplace) %{_sysconfdir}/cron.d/munin
%config(noreplace) %{_sysconfdir}/logrotate.d/munin
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
%{perl_vendorlib}/Munin/Node
%{perl_vendorlib}/Munin/Plugin
%{perl_vendorlib}/Munin/Plugin.pm
%{_mandir}/man1/munindoc.1*
%{_mandir}/man1/munin-run.1*
%{_mandir}/man1/munin-node.1*
%{_mandir}/man1/munin-node-configure.1*
%{_mandir}/man5/munin-node.conf.5*


%changelog
* Mon Apr 23 2012 Alexander Khrukin <akhrukin@mandriva.org> 1.4.7-1mdv2012.0
+ Revision: 792867
- version update 1.4.7

* Fri Jul 16 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.5-1mdv2011.0
+ Revision: 554269
- update to new version 1.4.5

* Wed Mar 24 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.4-2mdv2010.1
+ Revision: 527110
- transfer %%{_localstatedir}/run/munin to shared package, it is needed by the agent also

* Mon Mar 01 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.4-1mdv2010.1
+ Revision: 513036
- new version
- really fix munin-node init script

* Thu Dec 31 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.3-1mdv2010.1
+ Revision: 484536
- new version
- fix data migration from 1.3.x package
- fix init script (mdv bug #56646)

* Wed Dec 16 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.2-1mdv2010.1
+ Revision: 479561
- switch to non-sensitive apache access policy
- new version
- reload munin-node after rotating logs

* Fri Dec 04 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.1-1mdv2010.1
+ Revision: 473474
- more explicit access rules and access denied error message in apache configuration
- new version

* Mon Nov 30 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.0-5mdv2010.1
+ Revision: 472115
- restrict default access permissions to localhost only, as per new policy
- fix fw_forwarded_local plugin autoconfiguration
- fix post-installation scripts, and related dependencies
- split perl modules between master and node packages, so as to leverage deps
- drop useless explicit dependency on perl-Net-SNMP
- munin-node obsoletes munin-plugins-slapd

* Sat Nov 28 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.0-2mdv2010.1
+ Revision: 470864
- fix build dependencies
- 1.4.0 final
- new version

* Sun Nov 15 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.0-0.alpha2.2mdv2010.1
+ Revision: 466340
- new alpha release

* Mon Nov 09 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.0-0.alpha.2mdv2010.1
+ Revision: 463277
- only run data move procedure on upgrade

* Sun Nov 08 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.4.0-0.alpha.1mdv2010.1
+ Revision: 463050
- use here-in documents for logrotate configuration
- don't redefine logrotate configuration options uselessly
- drop all patches, excepted utf8 one
- only run automatic configuration on initial install, to avoid removed plugins to come back after each update
- handle data location change when upgrading
- new version
- spec cleanup
- move server components in munin-master package
- move generated HTML files in FHS-compliant /var/lib/munin/html
- move server data in /var/lib/munin/data
- move plugins data outside of server data directory
- use herein-documents for additional plugins configuration
- drop redundant dependencies

* Wed Aug 05 2009 Michael Scherer <misc@mandriva.org> 1.3.4-8mdv2010.0
+ Revision: 410245
- fix error in the patch for the utf8 fix, see bug 51502 for details
- correct the license

* Wed Jul 01 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.4-7mdv2010.0
+ Revision: 391252
- install manually missing Munin::Plugin::SNMP module
- keep bash completion in its own package

* Thu Jun 25 2009 Olivier Thauvin <nanardon@mandriva.org> 1.3.4-6mdv2010.0
+ Revision: 388903
- #51848: requires fonts-ttf-dejavu

* Mon Jun 08 2009 Olivier Thauvin <nanardon@mandriva.org> 1.3.4-5mdv2010.0
+ Revision: 384102
- fix #51502

* Fri Oct 10 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.4-4mdv2009.1
+ Revision: 291379
- backportability < 2009.0

* Wed Sep 24 2008 Olivier Thauvin <nanardon@mandriva.org> 1.3.4-3mdv2009.0
+ Revision: 287773
- munin-html: use cmp vs <=> operator for string sort

* Tue Jun 17 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.4-2mdv2009.0
+ Revision: 223662
- bash completion

  + Michael Scherer <misc@mandriva.org>
    - use lowercase for message, asked by guillomovitch
    - requires network on boot, asked by guillomovitch

* Sun Jun 08 2008 Olivier Thauvin <nanardon@mandriva.org> 1.3.4-1mdv2009.0
+ Revision: 216916
- 1.3.4

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Oct 12 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.3-4mdv2008.1
+ Revision: 97351
- various file list cleanup
- no need for %%doc tags for man pages
- make munin-node package own plugins directory, otherwise it get loosely created with various perms, breaking usage if too much restricted

  + Olivier Thauvin <nanardon@mandriva.org>
    - provide a config for fw* plugins
    - path4: fix cgi-graph lock
    - simplify specfile

* Mon May 28 2007 Olivier Thauvin <nanardon@mandriva.org> 1.3.3-3mdv2008.0
+ Revision: 32010
- one more plugins fix
- patch3: plugins fix

* Mon May 28 2007 Olivier Thauvin <nanardon@mandriva.org> 1.3.3-2mdv2008.0
+ Revision: 31972
- move Munin::Plugin into munin-node, where it is required
- munin-node require perl-Net-SNMP >= 5.2.0 for some plugins

* Mon May 28 2007 Olivier Thauvin <nanardon@mandriva.org> 1.3.3-1mdv2008.0
+ Revision: 31959
- 1.3.3

* Sat May 12 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5-6mdv2008.0
+ Revision: 26426
- fix cgi loacation

