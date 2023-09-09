import imp
import os
import re
import inspect
import logging

global environment_handlers
global source_handlers
environment_handlers = {}
source_handlers = {}

"""
This finds all modules in a directory

:param path: The path to the directory
:returns: A set of modules in the directory
"""
def modules_in_dir(path: str) -> set:
	result = set()
	for entry in os.listdir(path):
		if os.path.isfile(os.path.join(path, entry)):
			matches = re.search("(.+\.py)$", entry)
			if matches:
				result.add(matches.group(0))
	return result

"""
This automatically loads all modules in a directory

:param path: The path to the directory
"""
def import_dir(path: str):
	for filename in sorted(modules_in_dir(path)):
		search_path = os.path.join(os.getcwd(), path)
		module_name, _ = os.path.splitext(filename)
		fp, path_name, description = imp.find_module(module_name, [search_path,])
		imp.load_module(module_name, fp, path_name, description)

"""
This provides a dynamic way to load environment handlers through a decorator

:param environment: The name of the environment
:returns: A function for decoration
"""
def add_environment(environment: str) -> callable:
	# Get the current frame
	frame = inspect.stack()[1]
	# From the current frame, extract the relative path to the file
	path = frame[0].f_code.co_filename
	def wrapper(function):
		environment_handlers[environment] = function
		logging.debug(f"Loaded environment handler {environment} from {path}")
	return wrapper

"""
This provides a dynamic way to load wallpaper sources through a decorator

:param source: The name of the source
:returns: A function for decoration
"""
def add_source(source: str) -> callable:
	# Get the current frame
	frame = inspect.stack()[1]
	# From the current frame, extract the relative path to the file
	path = frame[0].f_code.co_filename
	def wrapper(function):
		source_handlers[source] = function
		logging.debug(f"Loaded wallpaper source {source} from {path}")
	return wrapper