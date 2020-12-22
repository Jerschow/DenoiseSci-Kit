import h5py
import numpy as np
from skimage.restoration import denoise_nl_means, estimate_sigma

# retrieve sigma based on whether it should be estimated or it is already given
# used exclusively by denoise
# param description:
# img: image to find the standard deviation of
# print_estimated_stdev_for (bool): tells whether to print the estimated standard deviation
# sigma (float): check description of denoise_nl_means
# multichannel (bool): check description of np.mean
# total_img_number (int): total number of images in dataset
def retrieve_sigma(img, print_estimated_stdev_for, sigma, mc, i, total_img_number):
	if sigma == None:
			# estimate the noise standard deviation from the noisy image
			sigma = np.mean(estimate_sigma(img, multichannel=mc))
			print("Estimated noise standard deviation for image at index " + str(i) + "=: " + str(sigma))\
				if print_estimated_stdev_for else print("Currently processing image at index " + str(i) +\
					". " + str(total_img_number - i) + " images left to denoise")
			return sigma
	return sigma

# retrieve sigma based on whether it should be estimated or it is already given
# used exclusively by denoise_set
# param description:
# img: image to find the standard deviation of
# print_estimated_stdev_for (bool): tells whether to print the estimated standard deviation
# sigma_sub_i (float): check description of denoise_nl_means
# avg_sigma (bool): check average_sigmas parameter in denoise_nl_means
# multichannel (bool): check description of np.mean
# fm (bool): check fast_mode parameter in denoise_nl_means called in denoise_set
# ps (array of ints): check patch_size parameter in denoise_nl_means
# pd (array of ints): check patch_distance parameter in denoise_nl_means
# pr (array of bools): check preserve_range parameter in denoise_nl_means
# i (int): img index in array
# total_img_number (int): total number of images in dataset
def denoise(img, print_estimated_stdev_for, h_sub_i, sigma_sub_i, avg_sigma, mc, fm, ps, pd, pr, i, total_img_number):
	sigma_retrieved = retrieve_sigma(img, print_estimated_stdev_for, sigma_sub_i, mc, i, total_img_number)
	patch_kw = dict(patch_size=ps,      # 5x5 patches
		patch_distance=pd,  # 13x13 search area
		multichannel=mc)
	return denoise_nl_means(img, h=h_sub_i * sigma_retrieved, sigma=sigma_retrieved, fast_mode=fm, preserve_range=pr,
		**patch_kw)

# returns data from read array and array of shape as the one in write file's param: wkey dataset. Also returns read_file so it
# can be closed and so that it can still be read from in denoise_set
# param descriptions:
# write_file_path (str): path to file where shape of dataset needs to be returned from
# read_file_path (str): path to file where data needs to be returned from
# wkey (str): dataset name where shape of dataset needs to be returned from
# rkey (str): dataset name where data needs to be returned from
def extract_data(write_file_path, read_file_path, wkey, rkey):
	write_file = h5py.File(write_file_path, 'r')
	read_file = h5py.File(read_file_path, 'r')
	write_array = np.full(write_file[wkey].shape, None)
	read_array = read_file[rkey]
	write_file.close()
	return [write_array, read_array, read_file]

def write_to(write_array, write_file_path, wkey):
	write_file = h5py.File(write_file_path, 'w')
	write_file[wkey] = write_array.astype('uint8')
	write_file.close()

# denoise images from read file's dataset whose name is provided by the parameter: key
# param description:
# write_file_path (str): name of h5 file to write denoised images to
# read_file_path (str): name of h5 file to read images yet to be denoised from
# wkey (str): name of dataset where images should be stored in write file
# rkey (str): name of dataset where images to be denoised are in read file
# print_estimated_stdev_for ( of bools): print the estimated standard deviation for all images at the indexes of True
# (cont.) if not passed then set to array of Falses
# hs (array of floats): define multiple of sigma used for h for corresponding image index
# sigmas (array of floats): define sigma for corresponding image index, an index can be None in which case the best guess will
# (cont.) be used
# average_sigmas (array of bools): define average_sigmas for corresponding image index, default is False if not passed
# multichannel (array of bools): define multichannel for corresponding image index, default is False if not passed
# fm (array of bools): check fast_mode parameter in denoise_nl_means
# ps (array of ints): check patch_size parameter in denoise_nl_means
# pd (array of ints): check patch_distance parameter in denoise_nl_means
# pr (array of bools): check preserve_range parameter in denoise_nl_means
def denoise_set(write_file_path, read_file_path, wkey, rkey, print_estimated_stdev_for, hs, sigmas,	average_sigmas, mc, fm,
	ps, pd, pr):
	# opening files and extracting arrays of images
	write_array, read_array, read_file = extract_data(write_file_path, read_file_path, wkey, rkey)
	
	# denoising
	for i in range(len(read_array)):
		# in case length of read_array is longer than write_array if user accidentally gave datasets of different sizes
		try:
			write_array[i] = denoise(read_array[i], print_estimated_stdev_for[i], hs[i], sigmas[i], average_sigmas[i],
				mc[i], fm[i], ps[i], pd[i], pr[i], i, len(write_array))
		except IndexError:
			break
	
	# save changes
	write_to(write_array, write_file_path, wkey)

	# close read file
	read_file.close()