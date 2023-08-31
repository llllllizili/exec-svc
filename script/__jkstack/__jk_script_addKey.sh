#!/usr/bin/expect

set timeout 3
set username [lindex $argv 0]
set ip [lindex $argv 1]
set password [lindex $argv 2]
set port [lindex $argv 3]

spawn ssh-copy-id -i /root/.ssh/id_rsa.pub $username@$ip -p $port

expect {
    "yes/no" {send "yes\r";exp_continue}
    "*password*" {send "$password\r";exp_continue}
}

# interact