%define octave_api api-v50+
%define _disable_rebuild_configure 1
%define _disable_lto 1

Name:		octave
Version:	4.0.1
Release:	1
Summary:	High-level language for numerical computations
License:	GPLv3+
Group:		Sciences/Mathematics
Url:		http://www.octave.org/
Source0:	ftp://ftp.gnu.org/gnu/octave/%{name}-%{version}.tar.xz
Source99:       %{name}.macros
Source100:	octave.rpmlintrc

# This patch is required when installing all sagemath dependencies,
# otherwise it will fail with a message like:
#
#	$ octave
#	$ fatal: lo_ieee_init: floating point format is not IEEE!  Maybe DLAMCH is miscompiled, or you are using some strange system without IEEE floating point math?
#
# and, while the reason is clear (using x87 and 80 bits doubles) the
# proper library/dependency causing it was not detected.
# This is not an issue in x86_64 that uses sse2+
Patch3:		octave-3.6.3-detect-i586-as-little-endian-ieee754.patch
BuildRequires:	bison
BuildRequires:	dejagnu
BuildRequires:	desktop-file-utils
BuildRequires:	emacs-nox
BuildRequires:	flex
BuildRequires:	gcc-gfortran
BuildRequires:	gnuplot
# (Abel) not strictly needed, but play safe
BuildRequires:	gperf
BuildRequires:	texinfo
#BuildRequires:	texlive
BuildRequires:	blas-devel
BuildRequires:	glpk-devel
BuildRequires:	hdf5-devel
BuildRequires:	lapack-devel
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(fftw3)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(ncurses)
# (Lev) needed to support sparse matrix functionality
BuildRequires:	amd-devel
BuildRequires:	suitesparse-devel
BuildRequires:	ccolamd-devel
BuildRequires:	cholmod-devel
BuildRequires:	colamd-devel
BuildRequires:	cxsparse-devel
BuildRequires:	umfpack-devel
# (Lev) other useful libraries
BuildRequires:	qhull-devel
BuildRequires:	qrupdate-devel
# (Lev) for new experimental plotting
BuildRequires:	fltk-devel
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
# to make imread more functional
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(GraphicsMagick)
BuildRequires:	pkgconfig(pixman-1)
# gui
BuildRequires:  pkgconfig(QtCore)
BuildRequires:  pkgconfig(QtGui)
BuildRequires:  pkgconfig(QtNetwork)
BuildRequires:  pkgconfig(QtOpenGL)
BuildRequires:  qscintilla-qt4-devel

%rename	octave3
Provides:	octave(api) = %{octave_api}
Requires:	gnuplot

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
Summary:	Development headers and files for Octave
Group:		Development/C
Requires:	%{name} = %{EVRD}
Requires:	gcc-c++
Requires:	gcc-gfortran
%rename	octave3-devel

%description devel
The octave-devel package contains files needed for developing
applications which use GNU Octave.

%package doc
Summary:	Documentation for Octave, a numerical computational language
Group:		Sciences/Mathematics

%description doc
GNU Octave is a high-level language, primarily intended for numerical
computations. It provides a convenient command line interface for
solving linear and nonlinear problems numerically, and for performing
other numerical experiments using a language that is mostly compatible
with Matlab. It may also be used as a batch-oriented language.

This package contains documentation of Octave in various formats.

%prep
%setup -q

%ifarch %{ix86}
%patch3 -p0
%endif

%build
export CC=gcc
export CXX=g++

%define enable64 no
export CPPFLAGS="%{optflags} -DH5_USE_16_API"
%configure2_5x \
	--enable-dl \
	--enable-shared \
	--disable-static \
	--enable-lite-kernel \
	--enable-picky-flags \
	--enable-64=%{enable64} \
        --with-amd="-lamd -lsuitesparseconfig" \
        --with-camd="-lcamd -lsuitesparseconfig" \
        --with-colamd="-lcolamd -lsuitesparseconfig" \
        --with-ccolamd="-lccolamd -lsuitesparseconfig"

make OCTAVE_RELEASE="%{distribution} %{version}-%{release}"

# emacs mode

%install
%makeinstall_std

# Make library links
mkdir -p %{buildroot}/etc/ld.so.conf.d
/bin/echo "%{_libdir}/octave-%{version}" > %{buildroot}/etc/ld.so.conf.d/octave-%{_arch}.conf

# Remove RPM_BUILD_ROOT from ls-R files
perl -pi -e "s,%{buildroot},," %{buildroot}%{_libexecdir}/octave/ls-R
perl -pi -e "s,%{buildroot},," %{buildroot}%{_datadir}/octave/ls-R

%{_bindir}/find %{buildroot} -name "*.oct" -print0 | %{_bindir}/xargs -t -0 -r strip --strip-unneeded

# prepare documentation
%__rm -rf package-doc
mkdir -p package-doc

# Create desktop file
mv %{buildroot}%{_datadir}/applications/www.octave.org-octave.desktop \
        %{buildroot}%{_datadir}/applications/octave.desktop
%{_bindir}/desktop-file-install --add-category Education --remove-category Development \
        --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/octave.desktop

mkdir -p %{buildroot}%{_datadir}/octave/packages
/bin/touch %{buildroot}%{_datadir}/octave/octave_packages

%multiarch_includes %{buildroot}%{_includedir}/octave-%{version}/octave/*.h

mkdir -p %{buildroot}%{_sysconfdir}/rpm/macros.d/
cp -p %{SOURCE99} %{buildroot}%{_sysconfdir}/rpm/macros.d/

%files
%defattr(0644,root,root,0755)
%doc NEWS* AUTHORS BUGS README
%doc examples INSTALL.OCTAVE
%defattr(-,root,root,0755)
%{_bindir}/octave*
%config(noreplace) /etc/ld.so.conf.d/*
%{_libdir}/octave*
%{_datadir}/octave
%{_datadir}/appdata/www.octave.org-octave.appdata.xml
%{_datadir}/icons/*/*/apps/octave.png
%{_datadir}/icons/*/*/apps/octave.svg
%if "%{_libdir}" != "%{_libexecdir}"
%{_libexecdir}/octave
%endif
%{_mandir}/man*/octave*
%{_infodir}/octave.info*
%{_datadir}/applications/*

%files devel
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/mkoctfile*
%{_includedir}/octave-%{version}
%{multiarch_includedir}/octave-%{version}
%{_mandir}/man1/mkoctfile.1*
%{_sysconfdir}/rpm/macros.d/%{name}.macros

%files doc
%defattr(0644,root,root,0755)
%doc doc/refcard/refcard-a4.pdf
%{_infodir}/liboctave.*

