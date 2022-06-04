import os
import shutil


def clear_directory(path: str):
    remove_directory(path, ignore_errors=True)
    create_directory(path, ignore_errors=True)


def create_directory(path: str, ignore_errors: bool = False):
    try:
        cmd = f'mkdir {path}'
        os.system(cmd)
    except Exception as e:
        if not ignore_errors:
            raise e


def remove_directory(path: str, ignore_errors: bool = False):
    try:
        cmd = f'rm -r {path}'
        os.system(cmd)
    except Exception as e:
        if not ignore_errors:
            raise e


def get_extension(filepath: str):
    return os.path.splitext(filepath)[1]


def remove_extension(filepath: str):
    return os.path.splitext(filepath)[0]


def copy_file(src: str, dst: str):
    return shutil.copyfile(src, dst)


def delete_file(filepath: str):
    return os.remove(filepath)


def get_filename(filepath: str, clear_extension: bool = False):
    filename = os.path.basename(filepath)
    if clear_extension:
        filename = remove_extension(filename)
    return filename


def append_suffix_to_filename(filepath: str, suffix: str):
    filepath_no_ext = remove_extension(filepath)
    ext = get_extension(filepath)
    filepath = f'{filepath_no_ext}{suffix}{ext}'
    return filepath


def is_image(filepath: str):
    try:
        from PIL import Image
        img = Image.open(filepath)
        return img.format.lower() in ['jpeg', 'jpg', 'png', 'tiff', 'gif']
    except:
        return False


def is_video(filepath: str):
    ext = get_extension(filepath)
    return ext.lower() in ['jpeg', 'jpg', 'png', 'tiff', 'gif']
