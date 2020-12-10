import ants
import h5py
import setup_raw as sr


WRITE_FILE_NAME = "denoised_raw.h5"
READ_FILE_NAME = 'raw.h5'
IMAGES_KEY_NAME = 'raw'


raw_file = h5py.File(READ_FILE_NAME, 'r')
images_r = raw_file[IMAGES_KEY_NAME]
denoised_file = h5py.File(WRITE_FILE_NAME, 'w')
images_w = denoised_file[IMAGES_KEY_NAME]

for i in range(len(images_r)):
	#converting numpy array to ANTsImage and denoising it then converting it back to a numpy array and storing it in images_w[i]
	images_w[i] = ants.denoise_image(ants.from_numpy(images_r[i])).numpy()

#update h5 file
denoised_file.close()
sr.store(WRITE_FILE_NAME, raw_file, IMAGES_KEY_NAME, images_w)

raw_file.close()