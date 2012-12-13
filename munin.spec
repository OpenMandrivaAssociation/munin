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
Requires(post):  rpm-helper >= 0.24.8-1
Requires(preun): rpm-helper >= 0.24.8-1
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
Requires(post):  rpm-helper >= 0.24.8-1
Requires(preun): rpm-helper >= 0.24.8-1

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
%attr(-,munin,apache) %{_localstatedir}/lib/munin/data/cgi-tmp
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
%doc %{_docdir}/%{name}
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


%changelog

* Sat Dec 08 2012 guillomovitch <guillomovitch> 2.0.9-1.mga3
+ Revision: 328131
- new version

* Thu Nov 29 2012 guillomovitch <guillomovitch> 2.0.8-1.mga3
+ Revision: 323102
- new version

* Thu Nov 22 2012 guillomovitch <guillomovitch> 2.0.7-5.mga3
+ Revision: 321117
- run systemd-tmpfiles during %%post

* Sun Oct 07 2012 barjac <barjac> 2.0.7-4.mga3
+ Revision: 303236
- Fix problem with fcgi unit files

* Sat Oct 06 2012 guillomovitch <guillomovitch> 2.0.7-3.mga3
+ Revision: 303070
- split asynchronous client in a distinct subpackage
- do not ship duplicated dejavu fonts
- add additional configuration directory to avoid wanings
- move munin-asyncd to %%{_sbindir} for FHS compliance
- ship same default plugin configuration as fedora
- hardcode rundir path as default

* Fri Oct 05 2012 barjac <barjac> 2.0.7-2.mga3
+ Revision: 302945
- Fix log directory

* Fri Oct 05 2012 guillomovitch <guillomovitch> 2.0.7-1.mga3
+ Revision: 302870
- fix master dependencies (#7697)
- new version
- no need to add user when installing node, it's already handled by base package

* Mon Sep 03 2012 guillomovitch <guillomovitch> 2.0.6-1.mga3
+ Revision: 287789
- new version
- use consistent syntax

* Thu Aug 23 2012 guillomovitch <guillomovitch> 2.0.5-2.mga3
+ Revision: 283349
- ship java plugins in a distinct subpackage
- use /run/munin instead of /var/run/munin
- convert /run/munin to tmpfs
- ship additional fedora systemd services
- make webapp configuration file compliant with apache 2.4

* Wed Aug 15 2012 guillomovitch <guillomovitch> 2.0.5-1.mga3
+ Revision: 281425
- new version

* Tue Aug 07 2012 guillomovitch <guillomovitch> 2.0.4-1.mga3
+ Revision: 279658
- new version

* Mon Jul 30 2012 guillomovitch <guillomovitch> 2.0.3-1.mga3
+ Revision: 275991
- new version

* Wed Jul 18 2012 guillomovitch <guillomovitch> 2.0.2-1.mga3
+ Revision: 272240
- new version

* Fri Jun 29 2012 guillomovitch <guillomovitch> 2.0.1-2.mga3
+ Revision: 264962
- fix perms of images generation directory

* Tue Jun 26 2012 guillomovitch <guillomovitch> 2.0.1-1.mga3
+ Revision: 263839
- new version

* Mon Jun 04 2012 guillomovitch <guillomovitch> 2.0.0-1.mga3
+ Revision: 254377
- 2.0.0 final
- drop sysinit support

* Mon May 07 2012 guillomovitch <guillomovitch> 2.0-0.rc5.2.mga2
+ Revision: 234858
- new release candidate

* Sat Apr 28 2012 tmb <tmb> 2.0-0.rc4.2.mga2
+ Revision: 233802
- Require rpm-helper >= 0.24.8-1 for systemd support

* Sat Apr 07 2012 guillomovitch <guillomovitch> 2.0-0.rc4.1.mga2
+ Revision: 229574
- new pre-release

* Wed Apr 04 2012 luigiwalser <luigiwalser> 2.0-0.rc2.2.mga2
+ Revision: 228527
- httpd restart is handled by filetriggers now

* Mon Mar 12 2012 guillomovitch <guillomovitch> 2.0-0.rc2.1.mga2
+ Revision: 222910
- new pre-release snapshot
- systemd support

* Mon Aug 29 2011 guillomovitch <guillomovitch> 2.0-0.beta4.1.mga2
+ Revision: 136248
- suggests perl(CGI::Fast)
- add missing LSB headers
- new version
- spec cleanup
- drop obsolete upgrade %%post scriptlet

* Thu Jul 14 2011 kharec <kharec> 1.4.6-1.mga2
+ Revision: 124035
- bugfix release

* Sun Feb 20 2011 dmorgan <dmorgan> 1.4.5-1.mga1
+ Revision: 54636
- imported package munin


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

  + Olivier Blin <oblin@mandriva.com>
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


* Fri Jan 26 2007 Michael Scherer <misc@mandriva.org> 1.2.5-5mdv2007.0
+ Revision: 113693
- add a forked version of the initscript, easier to add lsb init information etc

* Mon Jan 22 2007 Michael Scherer <misc@mandriva.org> 1.2.5-4mdv2007.1
+ Revision: 112109
- munin user requires a real directory for the shell, as cron check this
- restrict ( and in fact autorize ) connection from localhost on web interface
- it seems there is no service munin, so no need to call the macro

* Sun Jan 21 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5-3mdv2007.1
+ Revision: 111202
- fix path in config file (thanks misc)

* Sun Jan 21 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5-2mdv2007.1
+ Revision: 111200
- fix %%post: remove not need call

* Sat Jan 20 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5-1mdv2007.1
+ Revision: 111096
- build all doc
- fix www path
- import from RH/fedora rpm
- Create munin

