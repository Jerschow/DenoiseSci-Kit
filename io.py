'''Notes:
-all lambdas passed to bool_fxn param of validate_until_true take a *args parameter because validate_until_true
has one and passes it to bool_fxn for fxns that actually need more parameters to test the validity of user input.
This goes for valid_shape and is_yn as well'''


import numpy as np
import os
import h5py
import denoise
from constants import H5_EXTENSION_LENGTH, H5_EXTENSION, DEFAULT_PARAMS, PARAM_TYPE

# a fxn that keeps taking user input until bool_fxn(input()) == True
# param description:
# bool_fxn (function): the function that returns true if and only if the user input is valid and false otherwise
# error_message (str): message to print if bool_fxn(input()) == False
# *args (list): additional arguments needed by bool_fxn to determine if valid
def validate_until_true(bool_fxn, error_message, *args):
    ans = input()
    while not bool_fxn(ans, args):
        print(error_message)
        ans = input()
    return ans

# checks if name is a dataset in the file at file_path. Does this by trying to access dataset name in file at file_path
# (cont.) and if an error is caught, False is returned
# param descriptions:
# name (str): name of dataset
# file_path (str or tuple): path to the file you want to check has a dataset: name. This could be a tuple bc it is passed to 
# (cont.) validate_until_true as varargs
def is_dataset(name, file_path):
    yes = True
    file = h5py.File(file_path[0] if isinstance(file_path, tuple) else file_path, 'r')
    try:
        print(str(file[name]) + " exists. Good job")
    except KeyError:
        yes = False
    finally:
        file.close()
    return yes

# checks if the shape in param: shape, is a valid tuple
# param description:
# shape (str): string to be checked if in valid tuple format
# *args (list): read first bullet point at Notes at top of this file
def valid_shape(shape, *args):
    if not shape[0] == '(' or not shape[-1] == ')':
        return False
    for char in shape[1:-1]:
        if not char.isnumeric() and not char == ',':
            return False
    return True

# checks if ans is a yes or no answer
# param descriptions:
# ans (str): user answer
# args: check Notes at top of page above
def is_yn(ans, *args):
    return ans in ['y', 'n']

# make dataset in file at file_path with name: name, and return param: name
# param descriptions:
# name (str): name of dataset to be created
# file_path (str): path to file you want to create dataset at
# rshape (tuple): shape of read dataset
def mkdataset(name, file_path, args):
    print("Do you want to use the same shape for this dataset as your read dataset? (y/n)")
    shape = None
    if validate_until_true(is_yn, "Please enter 'y' or 'n'.") == 'y':
        shape = rshape
    else:
        print("What shape do you want your dataset to have? Please enter format (int1,int2,int3,...,intn) (no spaces)")
        shape = tuple(map(int, validate_until_true(valid_shape, "Please enter shape in format specified")[1:-1].split(',')))
    to_be_written = h5py.File(file_path, 'w')
    to_be_written.create_dataset(name, shape)
    to_be_written.close()
    return name

# creates file at param: path, and returns param: path
# param descriptions:
# path (str): path of file to be created
def create_file(path):
    # create file with h5py
    f = h5py.File(path, 'w')
    f.close()
    return path

# gets path to read/write file from user
# param descriptions:
# file_name (str): file to get path name for
def get_path(file_name):
    print("Would you like to pass an environment variable for the path name of your " + file_name + " file? (y/n)")
    # check that user said yes or no
    if validate_until_true(is_yn, "Please enter 'y' or 'n'.") == 'y':
        print("Please make sure that the path stored in your environment variable " +\
            "does not try to refer to your home directory with ~")
        # make user enter existing environment variable. Test if exists with os.environ.get(ans) == None or if ~ is in it
        return validate_until_true(lambda varname, *args : not os.environ.get(varname) == None and '~'\
            not in os.environ.get(varname), "Environment variable does not exist, please try again")
    print("Enter the path of the file or the path of one you want to make (only if you are entering your write file's path). " +\
            "Please make sure that the path you enter " + "does not try to refer to your home directory with ~")
    # nothing will happen if file already exists but make sure file name has h5 extension at end and that ~ not in it
    return create_file(validate_until_true(lambda path, *args : path[-H5_EXTENSION_LENGTH:] == H5_EXTENSION and '~' not in path,\
        "Sorry, this file does not have the required " + H5_EXTENSION + " extension at the end. Please try again"))

# gets dataset name (plus shape if read file)
# param descriptions:
# file (str): this is either read or write
# file_path (str): path of h5 file you want to read/write to
# *args (list): where the read dataset name and shape are passed in case user wants to select same name and shape for write file
# (cont.) as read file. args[0] is name and args[1] is shape
def get_dataset_name(file, file_path, *args):
    print("Enter the dataset you want to " + file)
    if file == 'read':
        name = validate_until_true(is_dataset, "Please enter an existing dataset", file_path)
        f = h5py.File(file_path, 'r')
        shape = f[name].shape
        f.close()
        return [name, shape]
    print("Do you want to use the same name for your write dataset as your read? (y/n)")
    ans = None
    if validate_until_true(is_yn, "Please enter 'y' or 'n'.") == 'y':
        ans = args[0]
    else:
        print("Please enter the name of the dataset you want to write to")
        ans = input()
    return ans if is_dataset(ans, file_path) else mkdataset(ans, file_path, args[1])

# returns the length of the 1st dimension of the array in file at param: file_path and datset param: key
# param description:
# file_path (str): path of h5 file you want to read/write to
# key (str): key of dataset where images are stored
def get_1stdim(file_path, key):
    file = h5py.File(file_path, 'r')
    length = len(file[key])
    file.close()
    return length

# processes user input for giving parameters and returns value and how many times to repeat it
# param descriptions:
# string (str): string to be processed
# left_to_assign (int): amount of images left to assign a parameter to
# param (str): name of param to be passed to denoise.denoise_set
def process(string, left_to_assign, param):
    times = string[string.index('*') + 1:]
    if times == 'rest':
        times = left_to_assign
    elif int(times) > left_to_assign:
        times = left_to_assign
    value = string[:string.index('*')]
    if value == 'None':
        value = DEFAULT_PARAMS[param]
    else:
        value = PARAM_TYPE[param](value)
    return [value, int(times)]

# method that gets parameter that can be passed to denoise.denoise_set
# param descriptions:
# param (str): name of param to be passed to denoise.denoise_set
# file_path (str): path of h5 file you want to read/write to
# key (str): key of dataset where images are stored
# validate_fxn (function): function that will be used to validate user input of parameters
# error_message (str): error printed when format of parameter input is wrong
def get_param(param, file_path, key, validate_fxn, error_message):
    print(param + " is an optional parameter. Press enter if you want the default values to be used or anything else to " +\
        "provide your own values")
    length = get_1stdim(file_path, key)
    if input() == '':
        # return default values
        return np.full((length,), DEFAULT_PARAMS[param])
    params = np.empty((length,), dtype=PARAM_TYPE[param])
    print("Enter the value you want to give plus '*a' where a is a number that represents for how many of the next fields " +\
        "you want to have that value (i.e. 1.3*3 would give the next 3 elements a " + param + " of 1.3). If you want to " +\
        "simply assign a value to the rest of the images do: value*rest")
    i = 0
    while i < length:
        print("Params left to specify: " + str(length - i) + " Enter 'None' if you want to use the default " +\
        "value for this image")
        value, times = process(validate_until_true(validate_fxn, error_message), length - i, param)
        for j in range(i, i + times):
            params[j] = value
        i += times
    return params

# checks if param: string is a float
# string: string to be checked
def isfloat(string):
    for char in string:
        if not char.isnumeric() and not char == '.':
            return False
    return True

# get path names for files
read_file_path = get_path('read')
write_file_path = get_path('write')

# enter the name of the dataset you want to read from
rkey, rshape = get_dataset_name('read', read_file_path)
wkey = get_dataset_name('write', write_file_path, rkey, rshape)

# get the rest of the parameters that will be passed to denoise.denoise_set
print_estimated_stdev_for = get_param('print_estimated_stdev_for', read_file_path, rkey,\
    lambda string, *args: '*' in string and (bool(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['print_estimated_stdev_for']))
hs = get_param('hs', read_file_path, rkey,\
    lambda string, *args: '*' in string and (isfloat(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['hs']))
sigmas = get_param('sigmas', read_file_path, rkey,\
    lambda string, *args: '*' in string and (isfloat(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['sigmas']))
average_sigmas = get_param('average_sigmas', read_file_path, rkey,\
    lambda string, *args: '*' in string and (bool(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['average_sigmas']))
multichannel = get_param('multichannel', read_file_path, rkey,\
    lambda string, *args: '*' in string and (bool(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['multichannel']))
fast_mode = get_param('fast_mode', read_file_path, rkey,\
    lambda string, *args: '*' in string and (bool(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['fast_mode']))
patch_size = get_param('patch_size', read_file_path, rkey,\
    lambda string, *args: '*' in string and (string[:string.index('*')].isnumeric() or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['patch_size']))
patch_distance = get_param('patch_distance', read_file_path, rkey,\
    lambda string, *args: '*' in string and (string[:string.index('*')].isnumeric() or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['patch_distance']))
preserve_range = get_param('preserve_range', read_file_path, rkey,\
    lambda string, *args: '*' in string and (bool(string[:string.index('*')]) or string[:string.index('*')] == 'None') and\
    (string[string.index('*') + 1:] == 'rest' or string[string.index('*') + 1:].isnumeric()), "Wrong format. Please enter type "\
    + str(PARAM_TYPE['preserve_range']))

# pass to denoise.denoise_set
denoise.denoise_set(write_file_path, read_file_path, wkey, rkey, print_estimated_stdev_for, hs, sigmas, average_sigmas,
    multichannel, fast_mode, patch_size, patch_distance, preserve_range)