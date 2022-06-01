import requests
import sys

# List of supported architectures
allowed = ["all", "amd64", "arm64", "armel", "armhf", "i386", "mips64el", "mipsel", "ppc64el", "s390x"]

package = ""
if len(sys.argv) > 1: package = sys.argv[1]
else: package = input("Input contents architecture: ")

if package in allowed: pass
else: exit("Unknown architecture: " + package)

url = "https://ftp.uk.debian.org/debian/dists/stable/main/Contents-" + package + ".gz"
file = "./contents/" + package + ".gz"

with open(file, 'wb') as f:
    resp = requests.get(url, verify=False)
    f.write (resp.content)