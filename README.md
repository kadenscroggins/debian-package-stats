# Debian Package Statistics

I coded this as part of a take-home assessment in an interview process.

Usage: `./package_statistics.py <architecture>`

This is a command line utility that outputs the top 10 packages with the most files associated with them from the debian package repository. It takes an architecture for input (`all`, `amd64`, etc) and outputs a list with the following format:

```
1. <package name 1> <number of files>
2. <package name 2> <number of files>
  
......
  
10. <package name 10> <number of files>
```

There is an allowlist of architectures stored in the `ALLOWED` list near the top of the code. The repo it draws from is the [UK debian stable mirror](http://ftp.uk.debian.org/debian/dists/stable/main/)
