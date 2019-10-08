#!/usr/bin/python3

# To see the Python docs, do: help (guestfs)
# To see the general docs http://libguestfs.org/guestfs.3.html
# For FAQ see http://libguestfs.org/FAQ.html

import guestfs
import libvirt
import subprocess
import os


# All new Python code should pass python_return_dict=True
# to the constructor.  It indicates that your program wants
# to receive Python dicts for methods in the API that return
# hashtables.
g = guestfs.GuestFS(python_return_dict=True)

# Set the trace flag so that we can see each libguestfs call.
g.set_trace(1)

print()
dom_image = input("  Please enter KVM domain disk image file name: ")
domimage = dom_image

# check if KVM disk image file exists
diskimage = "./" + dom_image
if os.path.isfile(diskimage) and os.access(diskimage, os.R_OK):
  print()
  print("  KVM disk image exists and is readable")
  print()
else:
  print()
  print("  KVM disk image file is missing or not readable")
  print()
  exit(1)

# get KVM domain hostname
domname = domimage[0:8]

# get KVM domain IP address
domip = domimage[7:8]

# check if KVM domain is running
conn = libvirt.open("qemu:///system")
if conn == None:
  print()
  print("  Failed to open connection to qemu:///system", file=sys.stderr)
  print()
  exit(1)

dom = conn.lookupByName(domname)
if dom == None:
  print()
  print("  Failed to find the domain "+domname, file=sys.stderr)
  print()
  exit(1)

flag = dom.isActive()
if flag == True:
  print()
  print("  KVM domain is active stop it!!!")
  print()
  exit(1)
#else:
#  print("  KVM domain is not active.')
conn.close()

# Attach the disk image to libguestfs.
g.add_drive_opts(domimage, format="qcow2")

# Run the libguestfs back-end.
g.launch()

# Get the list of partitions.
#g.list_partitions()
#print()

# Get the list of filesystems.
#g.list_filesystems()
#g.inspect_get_mountpoints(root)

# get root block device
roots = g.inspect_os ()
root = roots[0]
print("root block device (g.inspect_os): " + root )
print()

# get btrfs subvolume list
subvoli_int = g.btrfs_subvolume_list(root)
subvoli = str(subvoli_int)
print("subvolume list (g.btrfs_subvolume_list) :" + subvoli )
print()

# get default subvolume ID
subvoid_int = g.btrfs_subvolume_get_default(root)
subvoid = str(subvoid_int)
print("default subvolume ID (g.btrfs_subvolume_get_default): " + subvoid )
print()

# mount default subvolume
g.mount_options("rw,relatime,space_cache,subvolid=" + subvoid, root, "/")  
g.btrfs_subvolume_show("/")
print()

# verify and set btrfs subvolume readonly flag to "false"
g.sh("btrfs property get -ts /")
g.sh("btrfs property set -ts / ro false")
print()


# 1- create /etc/hosts file inside the KVM domain image
f = open('/tmp/hosts', 'w')
f.write('# \n') 
f.write('# hosts         This file describes a number of hostname-to-address \n') 
f.write('#               mappings for the TCP/IP subsystem.  It is mostly \n') 
f.write('#               used at boot time, when no name servers are running. \n') 
f.write('#               On small systems, this file can be used instead of a \n') 
f.write('#               "named" name server. \n') 
f.write('# Syntax: \n') 
f.write('#     \n') 
f.write('# IP-Address  Full-Qualified-Hostname  Short-Hostname \n') 
f.write('# \n') 
f.write(' \n') 
f.write('127.0.0.1	localhost \n') 
f.write(' \n') 
f.write('# special IPv6 addresses \n') 
f.write('::1             localhost ipv6-localhost ipv6-loopback \n') 
f.write(' \n') 
f.write('fe00::0         ipv6-localnet \n') 
f.write(' \n') 
f.write('ff00::0         ipv6-mcastprefix \n') 
f.write('ff02::1         ipv6-allnodes \n') 
f.write('ff02::2         ipv6-allrouters \n') 
f.write('ff02::3         ipv6-allhosts \n') 
f.write('192.168.10.3' + domip + ' caasp-0' + domip + '\n')
f.close()

g.rename("/etc/hosts", "/etc/hosts.orig")
g.upload("/tmp/hosts", "/etc/hosts")
os.remove("/tmp/hosts")
print('File "/tmp/hosts" uploaded!')
print()

###

# 2- create /etc/sysconfig/network/ifcfg-eth0 file inside the KVM domain image
f = open('/tmp/ifcfg-eth0', 'w')
f.write('BOOTPROTO=\'static\' \n')
f.write('BROADCAST=\'\' \n')
f.write('ETHTOOL_OPTIONS=\'\' \n')
f.write('IPADDR=\'192.168.10.3' + domip + '/24\' \n')
f.write('MTU=\'\' \n')
f.write('NAME=\'82540EM Gigabit Ethernet Controller\' \n')
f.write('NETWORK=\'\' \n')
f.write('REMOTE_IPADDR=\'\' \n')
f.write('STARTMODE=\'auto\' \n')
f.close()

g.rename("/etc/sysconfig/network/ifcfg-eth0", "/etc/sysconfig/network/ifcfg-eth0.orig")
g.upload("/tmp/ifcfg-eth0", "/etc/sysconfig/network/ifcfg-eth0")
os.remove("/tmp/ifcfg-eth0")
print('File "/tmp/ifcfg-eth0" uploaded!')
print()

# 3- re-create empty /etc/machine-id used in /etc/salt/minion.d/minion_id.conf
g.rm("/etc/machine-id")
g.touch("/etc/machine-id")

# set btrfs subvolume readonly flag back to "true"
g.btrfs_subvolume_show("/")
g.sh("btrfs property set -ts / ro true")
g.sh("btrfs property get -ts /")
print()
g.btrfs_subvolume_show("/")
print()

g.sync ()
g.umount_all ()

###

# 4- !! different subvolume !! - create /etc/hostname file inside the KVM domain image
g.mount_options("rw,relatime,space_cache,subvol=/@/var/lib/overlay", root, "/")
g.write("/etc/hostname", domname)
print('File "/etc/hostname" created!')
print()

###

g.sync ()
g.umount_all ()

