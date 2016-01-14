%{!?scl_name_base:%global scl_name_base git}
%{!?scl_name_version:%global scl_name_version 19}
# particularly useful for mock
%{!?scl:%global scl %{scl_name_base}%{scl_name_version}}
%scl_package %scl
# do not produce empty debuginfo package (https://bugzilla.redhat.com/show_bug.cgi?id=1061439#c2)
%global debug_package %{nil}


Summary: Package that installs %scl
Name: %scl_name
# should match the RHSCL version
Version: 1.2
Release: 4%{?dist}
Group: Applications/File
Source0: README
Source1: LICENSE
License: GPLv2+
Requires: scl-utils
Requires: %{scl_prefix}git
BuildRequires: scl-utils-build, help2man

%description
This is the main package for %scl Software Collection, which install
the necessary packages to use git-1.9.4. Software collections allow
to install more versions of the same package by using an alternative
directory structure.
Install this package if you want to use git-1.9.4 on your system.

%package runtime
Summary: Package that handles %scl Software Collection.
Group: Applications/File
Requires: scl-utils
# e.g. scl-utils 20120927-8.el6_5
Requires: /usr/bin/scl_source
Requires(post): policycoreutils-python, libselinux-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: %{name}-runtime = %{version}
Requires: scl-utils-build
Group: Applications/File

%description build
Package shipping essential configuration macros to build
%scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl.
Group: Applications/File

%description scldevel
Development files for %scl (useful e.g. for hierarchical collection
building with transitive dependencies).

%prep
%setup -c -T

cat > README <<\EOF
%{expand:%(cat %{SOURCE0})}
EOF
# copy the license file so %%files section sees it
cp %{SOURCE1} .

%build
# temporary helper script used by help2man
cat > h2m_helper <<\EOF
#!/bin/sh
if [ "$1" = "--version" ]; then
  printf '%%s' "%{scl_name} %{version} Software Collection"
else
  cat README
fi
EOF
chmod a+x h2m_helper
# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# install generated man page
install -d -m 755               %{buildroot}%{_mandir}/man7
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

%scl_install

# scldevel garbage
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

%post runtime
# Simple copy of context from system root to DSC root.
# In case new version needs some additional rules or context definition,
# it needs to be solved.
semanage fcontext -a -e /var/log/mongodb /var/log/%{scl_prefix}mongodb >/dev/null 2>&1 || :
semanage fcontext -a -e /usr/libexec/git-core/git-daemon /usr/libexec/git-core/%{scl_prefix}git-daemon >/dev/null 2>&1 || :
semanage fcontext -a -e / %{_scl_root} >/dev/null 2>&1 || :
selinuxenabled && load_policy >/dev/null 2>&1 || :
restorecon -R %{_scl_root} >/dev/null 2>&1 || :

%files

%files runtime
%doc README LICENSE
%{_mandir}/man7/%{scl_name}.*
%scl_files

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Tue Aug 12 2014 Ondrej Oprala <ooprala@redhat.com> 1.2-4
- Resolves: #1128115 - safely set PATH

* Tue Aug 12 2014 Ondrej Oprala <ooprala@redhat.com> 1.2-3
- Resolves: #1128115 - set MANPATH

* Wed Jun 11 2014 Ondrej Oprala <ooprala@redhat.com> 1-2
- Bump the git version mentioned in description

* Tue May 20 2014 Ondrej Oprala <ooprala@redhat.com> 1-1
- Initial commit
