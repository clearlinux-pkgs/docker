Name     : docker
Version  : 24.0.5
Release  : 146
URL      : https://github.com/moby/moby/archive/v24.0.5.tar.gz
Source0  : https://github.com/moby/moby/archive/v24.0.5.tar.gz
%global commit_id a61e2b4c9c5f7c241aeb37f389b4444aee26bea4
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0
BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
BuildRequires : gzip
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

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# Commit ID of the version release
%global docker_src_dir moby-%{version}

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n %docker_src_dir

%build
export DOCKER_BUILDTAGS='exclude_graphdriver_aufs seccomp'
export DOCKER_GITCOMMIT=%commit_id
unset CLEAR_DEBUG_TERSE

#./hack/dockerfile/install-binaries.sh runc-dynamic containerd-dynamic proxy-dynamic tini
GO111MODULE="auto" AUTO_GOPATH=1 VERSION=%version ./hack/make.sh dynbinary

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/usr/bin
install -p -m 755 bundles/dynbinary-daemon/dockerd %{buildroot}/usr/bin/dockerd
#install docker-proxy
install -p -m 755 bundles/dynbinary-daemon/docker-proxy  %{buildroot}/usr/bin/docker-proxy

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}/usr/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}/usr/lib/systemd/system/docker.socket
# install udev rule
install -m 0644 -D ./contrib/udev/80-docker.rules %{buildroot}/usr/lib/udev/rules.d/80-docker.rules

%files
%defattr(-,root,root,-)
/usr/bin/docker-proxy
/usr/bin/dockerd
/usr/lib/systemd/system/docker.service
/usr/lib/systemd/system/docker.socket
/usr/lib/udev/rules.d/80-docker.rules
