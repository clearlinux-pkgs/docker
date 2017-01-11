Name     : docker
Version  : 1.12.6
Release  : 51
URL      : https://github.com/docker/docker/archive/v1.12.6.tar.gz
Source0  : https://github.com/docker/docker/archive/v1.12.6.tar.gz
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0
BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
BuildRequires : gzip
BuildRequires : golang-github-cpuguy83-go-md2man
BuildRequires : golang-github-russross-blackfriday
BuildRequires : golang-github-shurcooL-sanitized_anchor_name
Requires : gzip
Requires : containerd
Requires : cc-oci-runtime
Patch1   : 0001-two-systemd-files-to-start-docker-with-proper-runtim.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global commit_id 7392c3b0ce0f9d3e918a321c66668c5d1ef4f689

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n docker-1.12.6
%patch1 -p1

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary

# generate man pages
GOPATH=/usr/lib/golang-dist go build github.com/cpuguy83/go-md2man
PATH="$PATH:$(pwd)" ./man/md2man-all.sh

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/usr/bin
install -p -m 755 bundles/latest/dynbinary-client/docker-%{version} %{buildroot}/usr/bin/docker
install -p -m 755 bundles/latest/dynbinary-daemon/dockerd-%{version} %{buildroot}/usr/bin/dockerd
install -p -m 755 bundles/latest/dynbinary-daemon/docker-proxy-%{version} %{buildroot}/usr/bin/docker-proxy

# install containerd
ln -s /usr/bin/containerd %{buildroot}/usr/bin/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/usr/bin/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/usr/bin/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/usr/bin/docker-runc

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}/usr/lib/systemd/system/docker.socket
install -m 0644 -D ./contrib/init/systemd/docker-cor.service %{buildroot}/usr/lib/systemd/system/docker-cor.service
install -m 0644 -D ./contrib/init/systemd/docker-cor.socket %{buildroot}/usr/lib/systemd/system/docker-cor.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker.socket
ln -s ../docker-cor.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker-cor.socket
#mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
#ln -s ../docker.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker.service
#ln -s ../docker-cor.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker-cor.service

# install man pages
install -d %{buildroot}/usr/share/man/man1 %{buildroot}/usr/share/man/man5 %{buildroot}/usr/share/man/man8
install ./man/man1/* %{buildroot}/usr/share/man/man1
install ./man/man5/* %{buildroot}/usr/share/man/man5
install ./man/man8/* %{buildroot}/usr/share/man/man8
chmod -x %{buildroot}/usr/share/man/man*/*

%files
%defattr(-,root,root,-)
/usr/bin/docker
/usr/bin/dockerd
/usr/bin/docker-proxy
/usr/bin/docker-containerd
/usr/bin/docker-containerd-shim
/usr/bin/docker-containerd-ctr
/usr/bin/docker-runc
/usr/lib/systemd/system/*.socket
/usr/lib/systemd/system/*.service
/usr/lib/systemd/system/*/*.socket
#/usr/lib/systemd/system/*/*.service
/usr/share/man/man*/*
