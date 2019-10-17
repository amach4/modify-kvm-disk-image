
Python 3 helper script to modify SUSE CaasP v3 KVM disk image using libguestfs library

- execute python script and enter KVM disk image name - example:

```tux@caasp-01:~>  python3 modify-kvm-disk-image.py```

  Please enter KVM domain disk image file name: `caasp-07-1.qcow2`

---
 
- start KVM domain and verify timestamps of new files:

```  
  caasp-07:~ # ls -al /etc/hosts
  -rw-r--r-- 1 root root 686 Oct  8 08:48 /etc/hosts
  
  caasp-07:~ # ls -al /etc/sysconfig/network/ifcfg-eth0
  -rw-r--r-- 1 root root 181 Oct  8 08:48 /etc/sysconfig/network/ifcfg-eth0

  caasp-07:~ # ls -al /etc/hostname
  -rw-r--r-- 1 root root 8 Oct  8 08:48 /etc/hostname

  caasp-07:~ # ls -al /etc/machine-id
  -rw-r--r-- 1 root root 33 Oct  8 08:48 /etc/machine-id
```
