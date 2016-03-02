#!/bin/bash

ip netns add A
ip netns add B
ip netns add fwd

ip link add name vethA type veth peer name vethAF
ip link add name vethB type veth peer name vethBF
ip link add name br0 type bridge
ip link set dev vethAF master br0
ip link set dev vethBF master br0

ip link set vethA netns A
ip link set vethB netns B
ip link set vethAF netns fwd
ip link set vethBF netns fwd

ip netns exec A brctl addbr br0


