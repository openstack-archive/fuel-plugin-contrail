#!/bin/bash

# Script to create NAT service image from ubuntu image

guestfish << _EOF_
add $IMAGE
run
mount /dev/sda1 /
download /etc/sysctl.conf /tmp/sysctl.conf
! echo "net.ipv4.ip_forward = 1" >> /tmp/sysctl.conf
upload /tmp/sysctl.conf /etc/sysctl.conf
! echo "dhclient" > /tmp/rc.local
! echo "/sbin/iptables -t nat -A POSTROUTING -o eth2 -j MASQUERADE" >> /tmp/rc.local
! echo "/sbin/iptables -A FORWARD -i eth2 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT" >> /tmp/rc.local
! echo "/sbin/iptables -A FORWARD -i eth1 -o eth2 -j ACCEPT" >> /tmp/rc.local
! echo "exit 0" >> /tmp/rc.local
upload /tmp/rc.local /etc/rc.local
echo "Set root password to 'password'"
download /etc/shadow /tmp/shadow
! sed -i 's/^root:[^:]\+:/root:$1$h2thgSpv$lAm04bPzOoldW8H0EVwVA0:/' /tmp/shadow
upload /tmp/shadow /etc/shadow
echo "Permit root login"
download /etc/ssh/sshd_config /tmp/sshd_config
! sed -i 's/^PasswordAuthentication.*$/PasswordAuthentication yes/' /tmp/sshd_config
! sed -i 's/^PermitRootLogin.*$/PermitRootLogin yes/' /tmp/sshd_config
upload /tmp/sshd_config /etc/ssh/sshd_config
_EOF_
