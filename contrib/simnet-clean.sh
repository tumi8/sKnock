#!/bin/bash



ip link del br0
ip link del vethA
ip link del vethB

ip netns del fwd
ip netns del A
ip netns del B
