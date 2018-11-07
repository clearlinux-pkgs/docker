Name     : docker
Version  : 18.06.1
Release  : 80
URL      : https://github.com/docker/docker-ce/archive/v18.06.1-ce.tar.gz
Source0  : https://github.com/docker/docker-ce/archive/v18.06.1-ce.tar.gz
%global commit_libnetwork d00ceed44cc447c77f25cdf5d59e83163bdcb4c9
Source1  : https://github.com/docker/libnetwork/archive/d00ceed44cc447c77f25cdf5d59e83163bdcb4c9.tar.gz
Source2  : docker-set-default-runtime
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

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global commit_id e68fc7a215d7133c34aa18e3b72b4a21fd0c6136
%global docker_src_dir %{name}-ce-%{version}-ce

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n %docker_src_dir
# docker-proxy
tar -xf %{SOURCE1}

%build
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 DOCKER_BUILDTAGS='exclude_graphdriver_aufs'
export GOPATH=/go

mkdir -p /go/src/github.com/docker/
rm -fr /go/src/github.com/docker/cli
ln -s /builddir/build/BUILD/%docker_src_dir/components/cli /go/src/github.com/docker/cli
pushd /go/src/github.com/docker/cli
make VERSION=%version GITCOMMIT=%commit_id dynbinary manpages
popd
rm -fr /go/src/github.com/docker/engine
ln -s /builddir/build/BUILD/%docker_src_dir/components/engine /go/src/github.com/docker/engine
pushd /go/src/github.com/docker/engine

#./hack/dockerfile/install-binaries.sh runc-dynamic containerd-dynamic proxy-dynamic tini
VERSION=%version ./hack/make.sh dynbinary
popd
# generate man pages
#PATH="$PATH:$(pwd)" ./man/md2man-all.sh

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
install -p -m 755 components/cli/build/docker-linux-amd64 %{buildroot}/usr/bin/docker
install -p -m 755 components/engine/bundles/dynbinary-daemon/dockerd-%{version} %{buildroot}/usr/bin/dockerd
#install docker-proxy
install -p -m 755 libnetwork-%{commit_libnetwork}/docker-proxy  %{buildroot}/usr/bin/docker-proxy
install -m 0755 -D %{SOURCE2} %{buildroot}/usr/bin/

# install containerd
ln -s /usr/bin/containerd %{buildroot}/usr/bin/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/usr/bin/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/usr/bin/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/usr/bin/docker-runc

# install systemd unit files
install -m 0644 -D ./components/packaging/rpm/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service

# install man pages
install -d %{buildroot}/usr/share/man/man1 %{buildroot}/usr/share/man/man5 %{buildroot}/usr/share/man/man8
install ./components/cli/man/man1/* %{buildroot}/usr/share/man/man1
install ./components/cli/man/man5/* %{buildroot}/usr/share/man/man5
install ./components/cli/man/man8/* %{buildroot}/usr/share/man/man8
chmod -x %{buildroot}/usr/share/man/man*/*

%files
%defattr(-,root,root,-)
/usr/bin/docker
/usr/bin/docker-containerd
/usr/bin/docker-containerd-ctr
/usr/bin/docker-containerd-shim
/usr/bin/docker-proxy
/usr/bin/docker-runc
/usr/bin/docker-set-default-runtime
/usr/bin/dockerd
/usr/lib/systemd/system/docker.service
/usr/share/man/man*/*
