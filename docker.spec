Name     : docker
Version  : 20.10.5
Release  : 112
URL      : https://github.com/moby/moby/archive/v20.10.5.tar.gz
Source0  : https://github.com/moby/moby/archive/v20.10.5.tar.gz
%global commit_libnetwork fa125a3512ee0f6187721c88582bf8c4378bd4d7
Source1  : https://github.com/docker/libnetwork/archive/fa125a3512ee0f6187721c88582bf8c4378bd4d7.tar.gz
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
Requires : docker-cli = %{version}
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

# Commit ID of the version release
%global commit_id 363e9a88a11be517d9e8c65c998ff56f774eb4dc
%global docker_src_dir moby-%{version}

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
rm -fr $HOME/go/src/github.com/docker/engine
ln -s /builddir/build/BUILD/%docker_src_dir $HOME/go/src/github.com/docker/engine
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
go build -ldflags="-linkmode=external" -buildmode=pie -o docker-proxy github.com/docker/libnetwork/cmd/proxy
popd

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/usr/bin
install -p -m 755 bundles/dynbinary-daemon/dockerd-%{version} %{buildroot}/usr/bin/dockerd
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
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}/usr/lib/systemd/system/docker.socket

%files
%defattr(-,root,root,-)
/usr/bin/docker-containerd
/usr/bin/docker-containerd-ctr
/usr/bin/docker-containerd-shim
/usr/bin/docker-proxy
/usr/bin/docker-runc
/usr/bin/docker-set-default-runtime
/usr/bin/dockerd
/usr/lib/systemd/system/docker.service
/usr/lib/systemd/system/docker.socket
