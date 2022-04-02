#!/bin/sh
# gwcgi - CGI web interface for Greasweazle
# Copyright 2022 Seth Price, all rights reserved.

# Location of images directory & filename template
dir='./images'
filename="$dir/gwcgi_`date +%s`.scp"

# Get parameters for gw invocation through standard input
read -r args

gw --time read $args --no-clobber $filename 2>&1

# Greaseweazle doesn’t change exit codes, so assume success if file is found
if [ -f "$filename" ]; then
	echo "[DOWNLOAD]$filename"
fi
