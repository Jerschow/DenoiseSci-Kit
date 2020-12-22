H5_EXTENSION_LENGTH = 3
H5_EXTENSION = '.h5'
DEFAULT_PARAMS = {\
    'print_estimated_stdev_for': False,\
    'hs': 0.85,\
    'sigmas': None,\
    'average_sigmas': False,\
    'multichannel': False,\
    'fast_mode': True,\
    'patch_size': 5,\
    'patch_distance': 6,\
    'preserve_range': True\
}
PARAM_TYPE = {\
    'print_estimated_stdev_for': bool,\
    'hs': float,\
    'sigmas': float,\
    'average_sigmas': bool,\
    'multichannel': bool,\
    'fast_mode': bool,\
    'patch_size': int,\
    'patch_distance': int,\
    'preserve_range': bool\
}