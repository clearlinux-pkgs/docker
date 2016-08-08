Name     : docker
Version  : 1.12.0
Release  : 39
URL      : https://github.com/docker/docker/archive/v1.12.0.tar.gz
Source0  : https://github.com/docker/docker/archive/v1.12.0.tar.gz
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0
BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
BuildRequires : gzip
Requires : gzip
Requires : containerd
Requires : cc-oci-runtime
Patch1   : 0001-add-cc-oci-runtime-as-default-runtime.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global gopath /usr/lib/golang
%global library_path github.com/docker/

%global commit_id 8eab29edd820017901796eb60d4bea28d760f16f

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n docker-1.12.0
%patch1 -p1

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary
# # generate man pages
# export GOPATH="$(pwd)/.gopath"
# go get github.com/spf13/cobra
# go get github.com/cpuguy83/go-md2man
# go build github.com/cpuguy83/go-md2man
# GOPATH="$(pwd)/vendor:$GOPATH" PATH="$PATH:$(pwd)" ./man/generate.sh

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/%{_bindir}
install -p -m 755 bundles/latest/dynbinary-client/docker-%{version} %{buildroot}%{_bindir}/docker
install -p -m 755 bundles/latest/dynbinary-daemon/dockerd-%{version} %{buildroot}%{_bindir}/dockerd
install -p -m 755 bundles/latest/dynbinary-daemon/docker-proxy-%{version} %{buildroot}%{_bindir}/docker-proxy

# install containerd
ln -s /usr/bin/containerd %{buildroot}/%{_bindir}/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/%{_bindir}/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/%{_bindir}/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/%{_bindir}/docker-runc

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}%{_prefix}/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}%{_prefix}/lib/systemd/system/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
ln -s ../docker.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker.service

# # install man pages
# install -d %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man5
# install ./man/man1/* %{buildroot}%{_mandir}/man1
# install ./man/man5/* %{buildroot}%{_mandir}/man5
# install ./man/man8/* %{buildroot}%{_mandir}/man8
# chmod -x %{buildroot}/%{_mandir}/man*/*

# add init scripts
install -d %{buildroot}/etc/sysconfig
install -d %{buildroot}/%{_initddir}

%files
%defattr(-,root,root,-)
%{_bindir}/docker
%{_bindir}/dockerd
%{_bindir}/docker-proxy
%{_bindir}/docker-containerd
%{_bindir}/docker-containerd-shim
%{_bindir}/docker-containerd-ctr
%{_bindir}/docker-runc
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*/*.socket
%{_prefix}/lib/systemd/system/*/*.service
# %{_mandir}/man*/*
