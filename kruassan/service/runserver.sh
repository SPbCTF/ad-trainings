#!/bin/bash


socat -d TCP4-LISTEN:3758,reuseaddr,fork,keepalive exec:./run.sh,pty
