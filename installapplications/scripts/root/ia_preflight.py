#!/usr/bin/python
import os


def check():
    validated = True
    filetocheck = '/path/to/file/file.ext'
    if not os.path.isfile(filetocheck):
        validated = False

    return validated


def main():
    if check():
        # Our checks passed, so we can skip the bootstrap process.
        exit(0)
    else:
        # Our checks didn't pass, so we need to run the bootstrap process.
        exit(1)


if __name__ == '__main__':
    main()
