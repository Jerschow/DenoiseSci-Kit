import ants
import h5py
import os
import setup_raw as sr


WRITE_FILE_NAME = "denoised_image_extened.h5"
READ_FILE_NAME = 'image_extened.h5'
IMAGES_KEY_NAME = 'main'


read_file = h5py.File(READ_FILE_NAME, 'r')
images_r = read_file[IMAGES_KEY_NAME]
denoised_file = h5py.File(WRITE_FILE_NAME, 'w')
images_w = denoised_file[IMAGES_KEY_NAME]

for i in range(len(images_r)):
	#converting numpy array to ANTsImage and denoising it then converting it back to a numpy array and storing it in images_w[i]
	images_w[i] = ants.denoise_image(ants.from_numpy(images_r[i])).numpy()

#update h5 file
denoised_file.close()
sr.store(WRITE_FILE_NAME, read_file, IMAGES_KEY_NAME, images_w)

read_file.close()