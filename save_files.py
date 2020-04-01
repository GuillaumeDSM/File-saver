from os import remove
from os.path import join, isdir, exists
from pathlib import Path
from shutil import copytree, copy, rmtree, move, make_archive
from time import time
from traceback import format_exc
from yaml import load, FullLoader


def get_list(elements_tree, current_parent_path="."):
    elements_list = []
    for element in elements_tree:
        if isinstance(element, str):
            elements_list.append(join(current_parent_path, element))
        elif isinstance(element, list):
            elements_list += get_list(element, current_parent_path=current_parent_path)
        elif isinstance(element, dict):
            for key, val in element.items():
                elements_list += get_list(val, current_parent_path=join(current_parent_path, key))
    return elements_list


class DataSaver:
    def __init__(self, to_save_elements, save_destination, to_ignore):
        self.to_save_elements = to_save_elements
        self.save_destination = save_destination
        self.to_ignore = to_ignore

    def save_elements(self):
        temp_destination = f"{self.save_destination}_tmp"
        _remove_element_if_exists(temp_destination)
        total_elements_count = len(self.to_save_elements)
        for index, to_save_element in enumerate(self.to_save_elements):
            self._save_element(to_save_element, temp_destination)
            print(f"- {index + 1}/{total_elements_count} {to_save_element} saved")
        # if no exception, can now replace previous save by the new one
        print("Creating file archive ...")
        self._replace_save_archive(temp_destination)
        print(f"Everything saved in {self.save_destination}")

    def _save_element(self, element, destination):
        # remove root from element path
        element_name = Path(element).parts[1:]
        # re-create path in save folder
        dest_path = join(destination, join(*element_name))
        if isdir(element):
            copytree(element, dest_path, ignore=self._should_ignore)
        else:
            copy(element, dest_path)

    def _should_ignore(self, _, names):
        return [name
                for name in names
                if name in self.to_ignore]

    def _replace_save_archive(self, to_replace_folder):
        _remove_element_if_exists(self.save_destination)
        dest_path = Path(self.save_destination)
        archive_format = dest_path.suffix.split(".")[-1]
        make_archive(self.save_destination.split(archive_format)[0],
                     archive_format.split(".")[-1],
                     to_replace_folder)
        _remove_element_if_exists(to_replace_folder)


def _remove_element_if_exists(element):
    if exists(element):
        if isdir(element):
            rmtree(element, ignore_errors=False)
        else:
            remove(element)


def _load_config(file_name):
    with open(file_name) as config_file:
        return load(config_file, Loader=FullLoader)


if __name__ == "__main__":
    try:
        start_time = time()
        config = _load_config("save_files.yml")
        save_dest = config["save_destination"]
        print(f"Saving files into: {save_dest}")
        to_save = get_list(config["save"])
        to_ignore = config["ignore"]
        DataSaver(to_save, save_dest, to_ignore).save_elements()
        print(f"Done in {round(time() - start_time, 2)} seconds.")
    except Exception as e:
        print(format_exc())
