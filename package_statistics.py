import requests
import sys
import gzip
import shutil
import os
import re
from heapq import nlargest

# List of supported architectures
ALLOWED = ["all", "amd64", "arm64", "armel", "armhf", "i386", "mips64el", "mipsel", "ppc64el", "s390x"]

# Collect package architecture to scan
package = ""
if len(sys.argv) > 1: package = sys.argv[1]
else: package = input("Input contents architecture: ")

# Verify package is on allowlist - won't bother trying to download nonexistent files
if package in ALLOWED: pass
else: exit("Unknown architecture: " + package)

# Assemble URL and file names from input
url = "https://ftp.uk.debian.org/debian/dists/stable/main/Contents-" + package + ".gz"
file = "./contents/" + package + ".gz"
file_out = "./contents/" + package

# Get file from internet and save to disk
if not os.path.exists('./contents'): os.makedirs('./contents')
with open(file, 'wb') as f:
    resp = requests.get(url, verify=False)
    f.write (resp.content)

# Unzip archive
with gzip.open(file, "rb") as f_in:
    with open(file_out, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

# Get threads for multithreading support
#threadcount = len(os.sched_getaffinity(0))

# Read contents file into list
lines = []
with open(file_out, "rb") as f_in:
    for line in f_in:
        lines.append(line)

#print(f'Contents file length: {len(lines)} lines')

# Key: package name, Value: number of files associated with package
packages = {}

# Add packages to dictionary defined above
for line in lines:
    line = re.sub('\A\S+\s+', '', str(line)) # Regex to clear file name and spaces to the left of packages
    line = line.rstrip('\\n\'') # Somehow the newline gets stringified. This removes the \n'
    if ',' in line:
        line = line.split(',')
        for string in line:
            name = string.split('/')[-1]
            if name in packages.keys(): packages.update({name : packages.get(name) + 1})
            else: packages.update({name : 1})
    else:
        name = line.split('/')[-1]
        if name in packages.keys(): packages.update({name : packages.get(name) + 1})
        else: packages.update({name : 1})

# Get ten largest packages from dictionary and print list
largest = nlargest(10, packages, key = packages.get)
for i in range(len(largest)):
    print(f'{i+1}. {largest[i]} {packages.get(largest[i])}')

# Delete files created during execution
#input('Execution complete. Hit enter to clear downloaded files...')
os.remove(file)
os.remove(file_out)