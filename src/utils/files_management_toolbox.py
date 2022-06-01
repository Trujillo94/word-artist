import os
import shutil


def clear_directory(path):
	try:
		cmd1 = f'rm -r {path}'
		os.system(cmd1)
	except:
		pass
	try:
		cmd2 = f'mkdir {path}'
		os.system(cmd2)
	except:
		pass


def get_extension(filepath):
	return os.path.splitext(filepath)[1]


def remove_extension(filepath):
	return os.path.splitext(filepath)[0]


def copy_file(src, dst):
	return shutil.copyfile(src, dst)


def delete_file(filepath):
	return os.remove(filepath)


def get_filename(filepath, clear_extension=False):
	filename = os.path.basename(filepath)
	if clear_extension:
		filename = remove_extension(filename)
	return filename


def append_suffix_to_filename(filepath, suffix):
	filepath_no_ext = remove_extension(filepath)
	ext = get_extension(filepath)
	filepath = f'{filepath_no_ext}{suffix}{ext}'
	return filepath


def is_image(filepath):
	try:
		from PIL import Image
		img = Image.open(filepath)
		return img.format.lower() in ['jpeg', 'jpg', 'png', 'tiff', 'gif']
	except:
		return False

def is_video(filepath):
	ext = get_extension(filepath)
	return ext.lower() in ['jpeg', 'jpg', 'png', 'tiff', 'gif']
