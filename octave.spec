%define version 2.1.73

Summary:	GNU Octave -- a high-level language for numerical computations
Name:		octave
Version:	%{version}
Release:	%mkrel 2
License:	GPL
Group:		Sciences/Mathematics
Source0:	ftp://ftp.octave.org/pub/octave/%{name}-%{version}.tar.bz2
Source4:	octave-2.1.36-emac.lisp.bz2
Patch1:		octave-2.1.63-insecure-tempfile.patch.bz2
URL:		http://www.octave.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
# (Abel) If you want atlas support, install atlas noarch RPM, then
# go to /usr/src/ATLAS and build the library. After that, rebuild
# this RPM and you are done. Feel like using Gentoo?
BuildRequires:	libblas-devel
BuildRequires:	liblapack-devel

BuildRequires:	dejagnu
BuildRequires:	emacs
BuildRequires:	emacs-bin
BuildRequires:	fftw-devel >= 0:3.0.1
BuildRequires:	gcc-gfortran
BuildConflicts:	gcc3.3-g77
BuildConflicts: gcc3.3-c++
BuildConflicts:	gcc3.3
BuildRequires:	gnuplot
BuildRequires:	hdf5-devel
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	texinfo
# (Abel) not strictly needed, but play safe
BuildRequires:	gperf
BuildRequires:	flex
BuildRequires:	bison

Requires:	gnuplot
%ifarch x86_64
Requires:	lib64hdf5_0
%else
Requires:	libhdf5_0
%endif

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

%package	doc
Summary:	Documentation for Octave, a numerical computational language
Group:		Sciences/Mathematics

%description	doc
GNU Octave is a high-level language, primarily intended for numerical
computations. It provides a convenient command line interface for
solving linear and nonlinear problems numerically, and for performing
other numerical experiments using a language that is mostly compatible
with Matlab. It may also be used as a batch-oriented language.

This package contains documentation of Octave in various formats.

%prep
%setup -q
%patch1 -p1 -b .tempfile

%build
export CC=gcc
export CXX=g++
export F77=gfortran
CFLAGS="$RPM_OPT_FLAGS -fno-fast-math" \
CXXFLAGS="$RPM_OPT_FLAGS -fno-fast-math" \
FFLAGS="$RPM_OPT_FLAGS -fno-fast-math" \
%configure2_5x \
	--enable-dl \
	--enable-shared \
	--enable-lite-kernel \
	--enable-picky-flags
%make
# (Abel) for some unknown reason linalg test took infinite time
#make check

# emacs mode
bzcat %SOURCE4 > octave.el
emacs -batch -q -no-site-file -f batch-byte-compile %name.el

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std
find $RPM_BUILD_ROOT -name "*.oct" -print0 | xargs -0 -r strip --strip-unneeded

mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/emacs/site-start.d/
install -m 644 %name.elc $RPM_BUILD_ROOT/%_sysconfdir/emacs/site-start.d/%name.elc
install -m 644 %name.el  $RPM_BUILD_ROOT/%_sysconfdir/emacs/site-start.d/

# prepare documentation
rm -rf package-doc
mkdir package-doc

mkdir package-doc/interpreter
ln doc/interpreter/*.html package-doc/interpreter/

mkdir package-doc/liboctave
ln doc/liboctave/*.html package-doc/liboctave/

mkdir package-doc/faq
ln doc/faq/*.html package-doc/faq/

mkdir package-doc/examples
ln examples/[[:lower:]]* package-doc/examples/

install -m 644 doc/liboctave/liboctave.info $RPM_BUILD_ROOT%{_infodir}/
install -m 644 doc/faq/Octave-FAQ.info $RPM_BUILD_ROOT%{_infodir}/

%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/config.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/Array.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/defaults.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/dim-vector.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/lo-sstream.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/lo-utils.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/oct-cmplx.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/pathsearch.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/octave-%{version}/octave/str-vec.h


%clean
rm -rf $RPM_BUILD_ROOT

%post
%_install_info octave.info

%preun
%_remove_install_info octave.info

%post doc
%_install_info liboctave.info
%_install_info Octave-FAQ.info

%preun doc
%_remove_install_info liboctave.info
%_remove_install_info Octave-FAQ.info

%files
%defattr(-,root,root)
%doc BUGS COPYING NEWS* PROJECTS README README.Linux ChangeLog ROADMAP SENDING-PATCHES THANKS

%{_bindir}/*
%{_libdir}/octave/
%{_includedir}/%name-%version
%{_datadir}/octave
%{_libexecdir}/%name-%version
%{_mandir}/man?/*
%{_infodir}/octave.*
%config(noreplace) %_sysconfdir/emacs/site-start.d/octave.el*

%multiarch %{multiarch_includedir}/octave-*/octave/config.h
%multiarch %{multiarch_includedir}/octave-*/octave/Array.h
%multiarch %{multiarch_includedir}/octave-*/octave/defaults.h
%multiarch %{multiarch_includedir}/octave-*/octave/dim-vector.h
%multiarch %{multiarch_includedir}/octave-*/octave/lo-sstream.h
%multiarch %{multiarch_includedir}/octave-*/octave/lo-utils.h
%multiarch %{multiarch_includedir}/octave-*/octave/oct-cmplx.h
%multiarch %{multiarch_includedir}/octave-*/octave/pathsearch.h
%multiarch %{multiarch_includedir}/octave-*/octave/str-vec.h


%files doc
%defattr(-,root,root)
%doc doc/refcard/refcard-a4.pdf
%doc package-doc/*
%{_infodir}/liboctave.*
%{_infodir}/Octave-FAQ.*

