import requests
import sys
import gzip
import shutil

# List of supported architectures
allowed = ["all", "amd64", "arm64", "armel", "armhf", "i386", "mips64el", "mipsel", "ppc64el", "s390x"]

package = ""
if len(sys.argv) > 1: package = sys.argv[1]
else: package = input("Input contents architecture: ")

if package in allowed: pass
else: exit("Unknown architecture: " + package)

url = "https://ftp.uk.debian.org/debian/dists/stable/main/Contents-" + package + ".gz"
file = "./contents/" + package + ".gz"
file_out = "./contents/" + package

with open(file, 'wb') as f:
    resp = requests.get(url, verify=False)
    f.write (resp.content)

with gzip.open(file, "rb") as f_in:
    with open(file_out, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)