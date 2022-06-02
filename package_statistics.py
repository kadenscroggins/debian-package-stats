import requests
import sys
import gzip
import shutil
import os

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
with open(file, 'wb') as f:
    resp = requests.get(url, verify=False)
    f.write (resp.content)

# Unzip archive
with gzip.open(file, "rb") as f_in:
    with open(file_out, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

# Get threads for multithreading support
#threadcount = len(os.sched_getaffinity(0))

lines = 0
with open(file_out, "rb") as f_in:
    for line in f_in:
        lines += 1
print(lines)

# Delete files created during execution
input("Execution complete. Hit enter to clear downloaded files...")
os.remove(file)
os.remove(file_out)