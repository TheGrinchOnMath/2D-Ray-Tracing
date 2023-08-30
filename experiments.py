import os

print(os.getcwd())

assets_dir = "assets\image.png" #  str(input("type path to image here"))

def path_fiddler(assets_dir):
    CWD = os.getcwd()
    newpath = os.path.join(CWD, assets_dir)

    return newpath
dir = path_fiddler(assets_dir)

newdir = ""
temp = ""
for i in dir:
    if i == "\\":
        temp = temp + i + i
    else:
        temp = temp + i
print(temp)
