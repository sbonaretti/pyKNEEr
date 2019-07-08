import subprocess
import pkg_resources
import platform
import os


# --- parameter folder ---
parameterFile = pkg_resources.resource_filename('pykneer','parameterFiles/MR_param_rigid.txt')
if not os.path.isfile(parameterFile):
    print ("TEST: - NOT FOUND " + parameterFile)
else:
    print ("TEST: " + parameterFile)


# --- elastix ---
sys = platform.system()

# get the folder depending on the OS
if sys == "Linux":
    dirpath = pkg_resources.resource_filename('pykneer','elastix/Linux/')
elif sys == "Windows":
    dirpath = pkg_resources.resource_filename('pykneer','elastix/Windows/')
elif sys == "Darwin":
    dirpath = pkg_resources.resource_filename('pykneer','elastix/Darwin/')

# create the full path
completeElastixPath     = dirpath + "elastix"
completeTransformixPath = dirpath + "transformix"

# call elastix to see if it reponds
cmd = [completeElastixPath]
output = subprocess.call(cmd, cwd=dirpath)
print ("TEST: " + str(output))
assert output == 0

# call transformix to see if it responds
md = [completeTransformixPath]
output = subprocess.call(cmd, cwd=dirpath)
print ("TEST: " + str(output))
assert output == 0
