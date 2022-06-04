'''
Takes a processor architecture input, downloads the associated Contents archive,
extracts it and counts the number of files associated with each package,
and prints the top 10 packages with the most files to the screen
'''

from time import process_time
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

def test_functions():
    '''
    Test get_architecture, get_contents_list, list_to_dict
    Test internal functionality contained within print_largest
    '''
    time_elapsed = 0.0

    # Test get_architecture
    sys.argv[1] = 'all'
    assert get_architecture() in ALLOWED
    time_elapsed = process_time() - time_elapsed
    print(f'get_architecture test passed. Time elapsed: {time_elapsed:.2f} seconds')

    # Test get_contents_list
    # Assumes ash will not be deleted from packages archive
    test_line = 'bin/ash                                                 shells/ash'
    test_list = get_contents_list('all')
    assert test_line in str(test_list[0])
    time_elapsed = process_time() - time_elapsed
    print(f'get_contents_list test passed. Time elapsed: {time_elapsed:.2f} seconds')

    # Test list_to_dict
    # Assumes sumo-dock will not be deleted from packages archive
    test_dict = list_to_dict(test_list)
    assert 'sumo-doc' in test_dict
    time_elapsed = process_time() - time_elapsed
    print(f'list_to_dict test passed. Time elapsed: {time_elapsed:.2f} seconds')

    # Test internal functionality of print_largest
    # Assumes fonts-cns11643 will stay in the top 10 packages
    largest = heapq.nlargest(10, test_dict, key = test_dict.get)
    assert 'fonts-cns11643-pixmaps' in largest
    time_elapsed = process_time() - time_elapsed
    print(f'print_largest test passed. Time elapsed: {time_elapsed:.2f} seconds')

    sys.exit(f'All tests passed. Total time elapsed: {process_time():.2f} seconds')

# Ignore SSL warnings
requests.packages.urllib3.disable_warnings()

if len(sys.argv) > 1 and sys.argv[1] == "test":
    test_functions()

arch = get_architecture()           # Get desired architecture (ex: amd64)
lines = get_contents_list(arch)     # Get list of lines from contents file
packages = list_to_dict(lines)      # Count number of files assoc. with each package
print_largest(packages)             # Print top 10 packages with most files
