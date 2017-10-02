Name     : docker
Version  : 17.05.0
Release  : 67
URL      : https://github.com/moby/moby/archive/v17.05.0-ce.tar.gz
Source0  : https://github.com/moby/moby/archive/v17.05.0-ce.tar.gz
%global commit_libnetwork 0f534354b813003a754606689722fe253101bc4e
Source1  : https://github.com/docker/libnetwork/archive/0f534354b813003a754606689722fe253101bc4e.tar.gz
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
Requires : iptables
Requires : git
Requires : xz
Requires : runc
Requires : gzip
Requires : containerd
Requires : LVM2
Requires : btrfs-progs
Requires : e2fsprogs
Requires : e2fsprogs-extras
Requires : xfsprogs
Patch1   : 0001-Automatic-Clear-Containers-runtime-detection.patch
Patch2   : 0002-Use-overlay-as-default.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global commit_id 7392c3b0ce0f9d3e918a321c66668c5d1ef4f689

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n moby-17.05.0-ce
%patch1 -p1
%patch2 -p1
# docker-proxy
tar -xf %{SOURCE1}

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary

# generate man pages
PATH="$PATH:$(pwd)" ./man/md2man-all.sh

# docker-proxy
pushd libnetwork-%{commit_libnetwork}
mkdir -p src/github.com/docker/libnetwork
ln -s $(pwd)/* src/github.com/docker/libnetwork
export GOPATH=$(pwd)
go build -ldflags="-linkmode=external" -o docker-proxy github.com/docker/libnetwork/cmd/proxy
popd

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/usr/bin
install -p -m 755 bundles/latest/dynbinary-client/docker-%{version}-ce %{buildroot}/usr/bin/docker
install -p -m 755 bundles/latest/dynbinary-daemon/dockerd-%{version}-ce  %{buildroot}/usr/bin/dockerd
#install docker-proxy
install -p -m 755 libnetwork-%{commit_libnetwork}/docker-proxy  %{buildroot}/usr/bin/docker-proxy

# install containerd
ln -s /usr/bin/containerd %{buildroot}/usr/bin/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/usr/bin/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/usr/bin/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/usr/bin/docker-runc

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}/usr/lib/systemd/system/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker.socket

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
/usr/bin/docker-containerd
/usr/bin/docker-containerd-shim
/usr/bin/docker-containerd-ctr
/usr/bin/docker-runc
/usr/bin/docker-proxy
/usr/lib/systemd/system/docker.socket
/usr/lib/systemd/system/docker.service
/usr/lib/systemd/system/sockets.target.wants/docker.socket
/usr/share/man/man*/*
