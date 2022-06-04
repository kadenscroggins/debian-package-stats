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

def get_architecture():
    '''
    Checks command line input for package architecture,
    gets it from user input if no command line argument is passed,
    and checks input architecture against list of supported architectures
    defined in the ALLOWED list.
    '''
    if len(sys.argv) > 1:
        architecture = sys.argv[1]
    else:
        architecture = input("Input contents architecture: ")
    if architecture in ALLOWED:
        pass
    else:
        sys.exit("Unknown architecture: " + architecture)

    return architecture

def get_contents_list(architecture):
    '''
    Takes string of contents architecture (ex: amd64) and downloads
    the associated contents file from the debian package repository.
    '''
    # Assemble URL and file names from input
    url = "https://ftp.uk.debian.org/debian/dists/stable/main/Contents-" + architecture + ".gz"
    file_compressed = "./contents/" + architecture + ".gz"
    file_decompressed = "./contents/" + architecture

    # Get file from internet, save to disk, extract
    if not os.path.exists('./contents'):
        os.makedirs('./contents')
    with open(file_compressed, 'wb') as file:
        resp = requests.get(url, verify=False)
        file.write (resp.content)
    with gzip.open(file_compressed, "rb") as file_in:
        with open(file_decompressed, "wb") as file_out:
            shutil.copyfileobj(file_in, file_out)

    # Read contents file into list, remove files on disk
    lines_list = []
    with open(file_decompressed, "rb") as f_in:
        for line in f_in:
            lines_list.append(line)
    os.remove(file_compressed)
    os.remove(file_decompressed)

    return lines_list

def list_to_dict(lines_list):
    '''
    Takes a list containing every line from a Contents file,
    and returns a dictionary that counts the number of files associated
    with each package in the Contents file.

    Dictionary Key: package name
    Dictionary Val: number of files associated with the package
    '''
    packages_dict = {}
    for line in lines_list:
        # Regex to clear file name and spaces to the left of packages
        line = re.sub('\\A\\S+\\s+', '', str(line))
        # Somehow the newline gets stringified. This removes the \n'
        line = line.rstrip('\\n\'')
        if ',' in line:
            # Some files are in multiple packages, this handles that
            line = line.split(',')
            for string in line:
                name = string.split('/')[-1]
                if name in packages_dict:
                    packages_dict.update({name : packages_dict.get(name) + 1})
                else:
                    packages_dict.update({name : 1})
        else:
            name = line.split('/')[-1]
            if name in packages_dict:
                packages_dict.update({name : packages_dict.get(name) + 1})
            else:
                packages_dict.update({name : 1})

    return packages_dict

def print_largest(packages_dict):
    '''
    Takes dictionary with package names as keys and number of files associated
    with package as value, and prints top ten packages with the most associated files
    '''
    largest = heapq.nlargest(10, packages_dict, key = packages_dict.get)
    for i, package in enumerate(largest):
        print(f'{i+1}. {package} {packages_dict.get(package)}')

arch = get_architecture()           # Get desired architecture (ex: amd64)
lines = get_contents_list(arch)     # Get list of lines from contents file
packages = list_to_dict(lines)      # Count number of files assoc. with each package
print_largest(packages)             # Print top 10 packages with most files
