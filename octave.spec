%define octave_api api-v32

Name:           octave
Version:        3.0.2
Release:        %mkrel 2
Epoch:          0
Summary:        High-level language for numerical computations
License:        GPLv3+
Group:          Sciences/Mathematics
Source0:        ftp://ftp.octave.org/pub/octave/%{name}-%{version}.tar.bz2
Source4:        octave-2.1.36-emac.lisp
Patch1:         octave-2.1.63-insecure-tempfile.patch
URL:            http://www.octave.org/
Obsoletes:      octave3 < %{epoch}:%{version}-%{release}
Provides:       octave3 = %{epoch}:%{version}-%{release}
Provides:       octave(api) = %{octave_api}
Requires:       gnuplot
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires(post): rpm-helper
Requires(post): info-install
Requires(preun): info-install
BuildRequires:  bison
# (Abel) If you want atlas support, install atlas noarch RPM, then
# go to /usr/src/ATLAS and build the library. After that, rebuild
# this RPM and you are done. Feel like using Gentoo?
BuildRequires:  blas-devel
BuildRequires:  dejagnu
BuildRequires:  desktop-file-utils
BuildRequires:  emacs
BuildRequires:  emacs-bin
BuildRequires:  fftw-devel >= 0:3.0.1
BuildRequires:  flex
BuildRequires:  gcc-gfortran
BuildRequires:	glpk-devel
BuildRequires:  gnuplot
# (Abel) not strictly needed, but play safe
BuildRequires:  gperf
BuildRequires:  hdf5-devel
BuildRequires:  lapack-devel
BuildRequires:  ncurses-devel
BuildRequires:  readline-devel
BuildRequires:  texinfo
BuildRequires:  tetex-dvips
BuildRequires:  tetex-latex
BuildRequires: 	pcre-devel
BuildRequires:	curl-devel
# (Lev) needed to support sparse matrix functionality
BuildRequires:  amd-devel
BuildRequires:  camd-devel
BuildRequires:  ccolamd-devel
BuildRequires:  cholmod-devel
BuildRequires:  colamd-devel
BuildRequires:  cxsparse-devel
BuildRequires:  umfpack-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
GNU Octave is a high-level language, primarily intended for numerical
computations. It provides a convenient command line interface for
solving linear and nonlinear problems numerically, and for performing
other numerical experiments using a language that is mostly compatible
with Matlab. It may also be used as a batch-oriented language.

Octave has extensive tools for solving common numerical linear algebra
problems, finding the roots of nonlinear equations, integrating
ordinary functions, manipulating polynomials, and integrating ordinary
differential and differential-algebraic equations. It is easily
extensible and customizable via user-defined functions written in
Octave's own language, or using dynamically loaded modules written in
C++, C, Fortran, or other languages.

%package devel
Summary:        Development headers and files for Octave
Group:          Development/C
Obsoletes:      octave3-devel < %{epoch}:%{version}-%{release}
Provides:       octave3-devel = %{epoch}:%{version}-%{release}
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       blas-devel
Requires:       fftw-devel
Requires:       gcc-c++
Requires:       gcc-gfortran
Requires:       hdf5-devel
Requires:       lapack-devel
Requires:       readline-devel
Requires:       zlib-devel

%description devel
The octave-devel package contains files needed for developing
applications which use GNU Octave.

%package doc
Summary:        Documentation for Octave, a numerical computational language
Group:          Sciences/Mathematics
Requires(post): info-install
Requires(preun): info-install

%description doc
GNU Octave is a high-level language, primarily intended for numerical
computations. It provides a convenient command line interface for
solving linear and nonlinear problems numerically, and for performing
other numerical experiments using a language that is mostly compatible
with Matlab. It may also be used as a batch-oriented language.

This package contains documentation of Octave in various formats.

%prep
%setup -q
OCTAVE_API=`%{__sed} -nr 's/^#define OCTAVE_API_VERSION "(api-v[[:digit:]]+)"$/\1/p' src/version.h`
test "x${OCTAVE_API}" = x%{octave_api} || exit 1
%patch1 -p1 -b .tempfile
%{__cp} -a %{SOURCE4} octave.el

%build
%define enable64 no
export CPPFLAGS="%{optflags} -DH5_USE_16_API"
%{configure2_5x} --enable-dl --enable-shared --disable-static --enable-lite-kernel --enable-picky-flags --enable-64=%{enable64} --with-f77=gfortran
%{make} OCTAVE_RELEASE="%{distribution} %{version}-%{release}"

# emacs mode
%{_bindir}/emacs -batch -q -no-site-file -f batch-byte-compile %{name}.el

%check
# (Abel) for some unknown reason linalg test took infinite time
%{make} check

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

# Make library links
%{__mkdir_p} %{buildroot}/etc/ld.so.conf.d
/bin/echo "%{_libdir}/octave-%{version}" > %{buildroot}/etc/ld.so.conf.d/octave-%{_arch}.conf

# Remove RPM_BUILD_ROOT from ls-R files
%{__perl} -pi -e "s,%{buildroot},," %{buildroot}%{_libexecdir}/octave/ls-R
%{__perl} -pi -e "s,%{buildroot},," %{buildroot}%{_datadir}/octave/ls-R

%{_bindir}/find %{buildroot} -name "*.oct" -print0 | %{_bindir}/xargs -t -0 -r strip --strip-unneeded

%{__mkdir_p} %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__cp} -a %{name}.elc %{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.elc
%{__cp} -a %{name}.el %{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el

# prepare documentation
%{__rm} -rf package-doc
%{__mkdir_p} package-doc

%{__mkdir_p} package-doc/interpreter
/bin/ln doc/interpreter/HTML/*.html package-doc/interpreter/

%{__mkdir_p} package-doc/liboctave
/bin/ln doc/liboctave/HTML/*.html package-doc/liboctave/

%{__mkdir_p} package-doc/faq
/bin/ln doc/faq/*.html package-doc/faq/

%{__mkdir_p} package-doc/examples
/bin/ln examples/[[:lower:]]* package-doc/examples/

%{__cp} -a doc/liboctave/liboctave.info %{buildroot}%{_infodir}/
%{__cp} -a doc/faq/Octave-FAQ.info %{buildroot}%{_infodir}/

# Create desktop file
%{__rm} %{buildroot}%{_datadir}/applications/www.octave.org-octave.desktop
%{_bindir}/desktop-file-install --add-category Education --remove-category Development \
        --dir %{buildroot}%{_datadir}/applications examples/octave.desktop

# Create directories for add-on packages
HOST_TYPE=`%{buildroot}%{_bindir}/octave-config -p CANONICAL_HOST_TYPE`
%{__mkdir_p} %{buildroot}%{_libexecdir}/octave/site/oct/%{octave_api}/$HOST_TYPE
%{__mkdir_p} %{buildroot}%{_libexecdir}/octave/site/oct/$HOST_TYPE
%{__mkdir_p} %{buildroot}%{_datadir}/octave/packages
/bin/touch %{buildroot}%{_datadir}/octave/octave_packages

%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/config.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/Array.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/defaults.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/dim-vector.h
#%%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/lo-sstream.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/lo-error.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/lo-utils.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/oct-cmplx.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/oct-conf.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/oct-dlldefs.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/oct-types.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/pathsearch.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/str-vec.h
%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/syswait.h

%clean
%{__rm} -rf %{buildroot}

%post
%if %mdkversion < 200900
/sbin/ldconfig
%endif
%_install_info octave.info
%create_ghostfile %{_datadir}/octave/octave_packages root root 0664

%preun
%_remove_install_info octave.info

%if %mdkversion < 200900
%postun -p /sbin/ldconfig
%endif

%post doc
%_install_info liboctave.info
%_install_info Octave-FAQ.info

%preun doc
%_remove_install_info liboctave.info
%_remove_install_info Octave-FAQ.info

%files
%defattr(0644,root,root,0755)
%doc NEWS* PROJECTS README README.Linux README.kpathsea ROADMAP
%doc SENDING-PATCHES THANKS emacs examples
#%%doc doc/interpreter/octave.p*
#%%doc doc/faq doc/interpreter/HTML doc/refcard
%defattr(-,root,root,0755)
%{_bindir}/octave*
%config(noreplace) /etc/ld.so.conf.d/*
%{_libdir}/octave*
%{_datadir}/octave
%exclude %{_datadir}/octave/octave_packages
%ghost %{_datadir}/octave/octave_packages
%if "%{_libdir}" != "%{_libexecdir}"
%{_libexecdir}/octave
%endif
%{_mandir}/man*/octave*
%{_infodir}/octave.info*
%{_datadir}/applications/*
%config(noreplace) %_sysconfdir/emacs/site-start.d/octave.el*

%files devel
%defattr(0644,root,root,0755)
#%%doc doc/liboctave
%defattr(-,root,root)
%{_bindir}/mkoctfile*
%{_includedir}/octave-%{version}
%dir %{multiarch_includedir}/octave-*
%multiarch %{multiarch_includedir}/octave-*/octave/config.h
%multiarch %{multiarch_includedir}/octave-*/octave/Array.h
%multiarch %{multiarch_includedir}/octave-*/octave/defaults.h
%multiarch %{multiarch_includedir}/octave-*/octave/dim-vector.h
#multiarch %{multiarch_includedir}/octave-*/octave/lo-sstream.h
%multiarch %{multiarch_includedir}/octave-*/octave/lo-error.h
%multiarch %{multiarch_includedir}/octave-*/octave/lo-utils.h
%multiarch %{multiarch_includedir}/octave-*/octave/oct-cmplx.h
%multiarch %{multiarch_includedir}/octave-*/octave/oct-conf.h
%multiarch %{multiarch_includedir}/octave-*/octave/oct-dlldefs.h
%multiarch %{multiarch_includedir}/octave-*/octave/oct-types.h
%multiarch %{multiarch_includedir}/octave-*/octave/pathsearch.h
%multiarch %{multiarch_includedir}/octave-*/octave/str-vec.h
%multiarch %{multiarch_includedir}/octave-*/octave/syswait.h
%{_mandir}/man*/mkoctfile*

%files doc
%defattr(0644,root,root,0755)
%doc doc/refcard/refcard-a4.pdf
%doc package-doc/*
%{_infodir}/liboctave.*
%{_infodir}/Octave-FAQ.*
