# vim:syntax=apparmor
# AppArmor policy for xfuzz
# ###AUTHOR###
# ###COPYRIGHT###
# ###COMMENT###

#include <tunables/global>


profile xfuzz flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow network access
  network,

  /dev/tty rw,
  /dev/pts/* rw,
  /etc/{*,**} r,
  owner /tmp/** rw,

  # Python
  /usr/local/lib/{,**} rix,
  /var/cache/pycache/{,**} rwix,

  # xfuzz code. Writing to this directory is permitted except to configuration
  # and testing files.
  /opt/xfuzz/{,**} rix,
  /opt/xfuzz/** wlk,
  deny /opt/xfuzz/tox.ini wl,
  deny /opt/xfuzz/MANIFEST.in wl,
  deny /opt/xfuzz/pyproject.toml wl,
  deny /opt/xfuzz/setup.py wl,
  deny /opt/xfuzz/test/{,**} wl,

  # Inherit profile during execution
  /bin/{*,**} rix,
  /usr/bin/{*,**} rix,
  /usr/local/bin/{*,**} rix,

  # Host (privileged) processes may send signals to container processes.
  signal (receive) peer=unconfined,
  # dockerd may send signals to container processes (for "docker kill").
  signal (receive) peer=dockerd-default,

  # Container processes may send signals amongst themselves.
  signal (send,receive) peer=xfuzz,

  @{PROC}/*/fd/{,*} r,

  # suppress ptrace denials when using 'docker ps' or using 'ps' inside a container
  ptrace (trace,read,tracedby,readby) peer=xfuzz,
}
