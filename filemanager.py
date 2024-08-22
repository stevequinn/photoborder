"""
File helper functions
"""
import os
from fnmatch import fnmatch

def should_include_file(filename: str, include_patterns: list[str], exclude_patterns: list[str]) -> bool:
    return any(fnmatch(filename, pattern) for pattern in include_patterns) and \
           not any(fnmatch(filename, pattern) for pattern in exclude_patterns)

def get_directory_files(directory: str, recursive: bool, include_patterns: list[str], exclude_patterns: list[str]):
    paths = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if should_include_file(file, include_patterns, exclude_patterns):
                file_path = os.path.join(root, file)
                paths.append(file_path)

        if not recursive:
            break

    return paths
