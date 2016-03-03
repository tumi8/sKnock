#!/bin/bash
service ntp stop
for i in {1..20}
do
    ntpdate ntp.informatik.tu-muenchen.de
done
service ntp start