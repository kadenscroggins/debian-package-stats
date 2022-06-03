'''
Takes a processor architecture input, downloads the associated Contents archive,
extracts it and counts the number of files associated with each package,
and prints the top 10 packages with the most files to the screen
'''

import heapq
import sys
import gzip
import os
import shutil
import re
import requests

# List of supported architectures
ALLOWED = ['all', 'amd64', 'arm64', 'armel', 'armhf',\
    'i386', 'mips64el', 'mipsel', 'ppc64el', 's390x']

# Collect package architecture to scan
if len(sys.argv) > 1:
    architecture = sys.argv[1]
else:
    architecture = input("Input contents architecture: ")
if architecture in ALLOWED:
    pass
else:
    sys.exit("Unknown architecture: " + architecture)

# Assemble URL and file names from input
url = "https://ftp.uk.debian.org/debian/dists/stable/main/Contents-" + architecture + ".gz"
file_compressed = "./contents/" + architecture + ".gz"
file_decompressed = "./contents/" + architecture

# Get file from internet, save to disk, extract
if not os.path.exists('./contents'):
    os.makedirs('./contents')
with open(file_compressed, 'wb') as f:
    resp = requests.get(url, verify=False)
    f.write (resp.content)
with gzip.open(file_compressed, "rb") as f_in:
    with open(file_decompressed, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

# Read contents file into list, remove files on disk
lines = []
with open(file_decompressed, "rb") as f_in:
    for line in f_in:
        lines.append(line)
os.remove(file_compressed)
os.remove(file_decompressed)

# Key: package name, Value: number of files associated with package
packages = {}

# Add packages to dictionary defined above
for line in lines:
    # Regex to clear file name and spaces to the left of packages
    line = re.sub('\\A\\S+\\s+', '', str(line))
    # Somehow the newline gets stringified. This removes the \n'
    line = line.rstrip('\\n\'')
    if ',' in line:
        # Some files are in multiple packages, this handles that
        line = line.split(',')
        for string in line:
            name = string.split('/')[-1]
            if name in packages.keys():
                packages.update({name : packages.get(name) + 1})
            else:
                packages.update({name : 1})
    else:
        name = line.split('/')[-1]
        if name in packages.keys():
            packages.update({name : packages.get(name) + 1})
        else:
            packages.update({name : 1})

# Get ten largest packages from dictionary and print list
largest = heapq.nlargest(10, packages, key = packages.get)
for i, package in enumerate(largest):
    print(f'{i+1}. {largest[i]} {packages.get(largest[i])}')
