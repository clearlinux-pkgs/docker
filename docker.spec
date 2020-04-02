Name     : docker
Version  : 19.03.8
Release  : 96
URL      : https://github.com/docker/docker-ce/archive/v19.03.8.tar.gz
Source0  : https://github.com/docker/docker-ce/archive/v19.03.8.tar.gz
%global commit_libnetwork 9fd385be8302dbe1071a3ce124891893ff27f90f
Source1  : https://github.com/docker/libnetwork/archive/9fd385be8302dbe1071a3ce124891893ff27f90f.tar.gz
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
BuildRequires : libseccomp-dev
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
Patch1: 0001-Use-systemd-cgroup.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global commit_id afacb8b7f0d8d4f9d2a8e8736e9c993e672b41f3
%global docker_src_dir %{name}-ce-%{version}

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n %docker_src_dir
# docker-proxy
tar -xf %{SOURCE1}

%patch1 -p1

%build
export DOCKER_BUILDTAGS="pkcs11 seccomp"
export RUNC_BUILDTAGS="seccomp"

export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 DOCKER_BUILDTAGS='exclude_graphdriver_aufs seccomp' 
export GOPATH=$HOME/go

mkdir -p $HOME/go/src/github.com/docker/
rm -fr $HOME/go/src/github.com/docker/cli
ln -s /builddir/build/BUILD/%docker_src_dir/components/cli $HOME/go/src/github.com/docker/cli
pushd $HOME/go/src/github.com/docker/cli
make VERSION=%version GITCOMMIT=%commit_id BUILDTAGS="exclude_graphdriver_aufs  seccomp"  dynbinary manpages
popd
rm -fr $HOME/go/src/github.com/docker/engine
ln -s /builddir/build/BUILD/%docker_src_dir/components/engine $HOME/go/src/github.com/docker/engine
pushd $HOME/go/src/github.com/docker/engine

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
ln -s /usr/bin/ctr %{buildroot}/usr/bin/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/usr/bin/docker-runc

# install systemd unit files
install -m 0644 -D ./components/packaging/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service
install -m 0644 -D ./components/packaging/systemd/docker.socket %{buildroot}/usr/lib/systemd/system/docker.socket

# install bash completion file.
install -m 0644 -D ./components/cli/contrib/completion/bash/docker %{buildroot}/usr/share/bash-completion/completions/docker

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
/usr/lib/systemd/system/docker.socket
/usr/share/bash-completion/completions/docker
/usr/share/man/man*/*
