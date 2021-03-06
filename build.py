#!/usr/bin/python
"""
Run this on your main program to build it. Built files go in the .build folder.
"""

import subprocess
import sys
import os

gccArgs = [
    'gcc',
    '-Wall',
    '-o .build/a.out'
]

def prepareBuildFolder ():
    hasBuildFolder = ".build" in os.listdir(".")
    if not hasBuildFolder:
        os.mkdir(".build")

def findFile (filename):
    for d in os.walk('.'):
        for f in d[2]:
            if f == filename:
                return d[0] + '/' + filename

    raise OSError("Could not find file " + filename)

def getTargets (filename):
    targets = []

    def getCFiles (filename, targets):
        f = open(filename)
        for line in f.readlines():
            if line.startswith("#include"):
                headerFile = line.split(' ')[1].split('/')[-1].strip("\"<>\n")
                if headerFile not in os.listdir("/usr/include"):
                    try:
                        path = findFile(headerFile.replace(".h", ".c"))
                        if path not in targets:
                            targets.append(path)
                            getCFiles(path, targets)
                    except OSError:
                        pass

    getCFiles(filename, targets)

    return targets

def generateMakefile (filename):
    f = open(".build/makefile", 'w')

    target_all = "\t" + ' '.join(gccArgs)
    target_all += " " + ' '.join(getTargets(filename))
    target_all += " " + filename
    target_all += '\n'

    f.writelines(["all:\n", target_all])

    target_clean = "\tcd .build && rm -f *.o *.so *.out"
    f.writelines(["clean:\n", target_clean])

    f.close()

def build (args):
    make =  True
    run = False
    clean = False
    filename = ""

    for arg in args:
        if arg == "-r":
            run = True
        elif arg == "-m":
            make = False
        elif arg == "-c":
            clean = True
        else:
            filename = arg

    prepareBuildFolder()

    generateMakefile(filename)

    if make:
        try:
            subprocess.check_call(['make', '-f', '.build/makefile'])
        except subprocess.CalledProcessError:
            return

    if run:
        subprocess.check_call(['.build/a.out'])

    if clean:
        subprocess.check_call(['make', '-f', '.build/makefile', 'clean'])

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0 or "--help" in args:
        print """
            -r: run after building
            -m: only generate makefiles, don't build (after doing this you can run make with make -f .build/makefile)

            This script builds your files to a hidden folder called .build
            Just run .build/a.out
            """
    else:
        build(args)
