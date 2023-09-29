import os, json, sys, pathlib

def read(path):
    with open(path, "r") as file_temp:
        try:
            # add code here that reads the file contents differently if it is an image or a json
            # add call to opencv function, or add the code into this function
            file = file_temp
            return file
        except FileNotFoundError:
            print("Error: File Not Found.")


def write(data, path):
    with data as write_file:
        try:
            if os.path.exists(path):
                overwrite = str(input("file exists, overwrite? \n\n WARNING, THIS WILL DELETE THE FILE"))
                if overwrite == "yes" or "y" or "Y":
                    pass
            else:
                with open(path, "w") as file:
                    file.write(write_file, path)
        except:
            pass

def path_fiddler(dirs):
    CWD = os.getcwd()
    for dir in dirs try:
        if type(dir) != "string":
            raise TypeError("not a string")
        

# find out how to make the code not be able to write outside of the main folder