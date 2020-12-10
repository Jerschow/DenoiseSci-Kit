import h5py
import setup_raw as sr
import numpy as np


WRITE_FILE_NAME = "denoised_image_extened.h5"
READ_FILE_NAME = 'image_extened.h5'
IMAGES_KEY_NAME = 'main'


raw_file = h5py.File(READ_FILE_NAME, 'r')
#data stored in dataset raw just needs to be the same shape as in the read file
#so I made an array with the same shape with all entries 0
sr.store(WRITE_FILE_NAME, raw_file, IMAGES_KEY_NAME, np.zeros(raw_file['raw'].shape))

raw_file.close()