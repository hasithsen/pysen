#!/usr/bin/env python3

"""
pysen

Simple static site generator
"""

import argparse
import datetime
import os
from tzlocal import get_localzone
from jinja2 import Template, Environment, FileSystemLoader
import shutil


__license__ = "MIT"
__version__ = "2023.12.03-2"
__maintainer__ = "Hasith Dhananjaya Senevirathne"
__email_ = "sen.hasith@gmail.com"


def get_local_time_with_offset():
  # Get the system's local timezone
  local_timezone = get_localzone()

  # Get the current time in the system's local timezone
  current_local_time = datetime.datetime.now(local_timezone)

  # Extract the timezone offset in the format +HH:MM
  offset_hours, offset_minutes = divmod(
      current_local_time.utcoffset().seconds // 60, 60)
  formatted_timezone_offset = f"{'+' if offset_hours >= 0 else '-'}{abs(offset_hours):02d}:{offset_minutes:02d}"

  # Format the date and time with the manually included timezone offset
  return current_local_time.strftime(
      f'%Y-%m-%dT%H:%M:%S{formatted_timezone_offset}')


def check_file_status(file_path):
  """
  Check the status of a file.

  Returns:
      0 if the file does not exist.
      1 if the file exists.
      -1 if an error occurs (e.g., cannot determine the file status).
  """
  try:
    if os.path.exists(file_path):
      return 1  # File exists
    else:
      return 0  # File does not exist
  except Exception as e:
    print(f"Error checking file status: {e}")
    return -1  # Error occurred


def create_post(file_path):
  # extract filename sans extension
  title = os.path.splitext(os.path.basename(file_path))[0]

  # date: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')}
  content = f"""---
title: "{title}"
date: {get_local_time_with_offset()}
draft: true
---
"""

  with open(file_path, "w") as file:
    file.write(content)

  print(f"File '{file_path}' created successfully.")


def remove_directory(directory_path):
  try:
    # Remove the directory and its contents
    shutil.rmtree(directory_path)
    print(
        f"Directory '{directory_path}' and its contents removed successfully.")
  except FileNotFoundError:
    print(f"Directory '{directory_path}' not found.")
  except PermissionError:
    print(f"Permission error: Unable to remove directory '{directory_path}'.")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


def create_directory(directory_path):
  try:
    # Create a directory at the specified path
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created successfully.")
  except FileExistsError:
    print(f"Directory '{directory_path}' already exists.")
  except PermissionError:
    print(f"Permission error: Unable to create directory '{directory_path}'.")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


def copy_directory(source_path, destination_path):
  try:
    # Copy the entire directory from source_path to destination_path
    shutil.copytree(source_path, destination_path)
    print(
        f"Directory '{source_path}' copied to '{destination_path}' successfully.")
  except shutil.Error as e:
    print(f"Error: {e}")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


def build_site():
  html_theme = "poetry"  # directory name from under themes/
  build_export_directory = "public"

  # load templates folder to environment (security measure)
  env = Environment(loader=FileSystemLoader(f"themes/{html_theme}/layouts"))

  # load the `index.jinja` template
  index_template = env.get_template("index.html")
  output_from_parsed_template = index_template.render(
      site={
          "name": "Verse",
          "author": "Hasith Senevirathne",
          "tagline": "",
          "footer": f'Copyright © 2023 <a href="https://hasithsen.pages.dev">hsen</a>.',
      },
      post={
          "title": "post title here",
          "date": "",
          "content": "sample content here",
      }
  )

  # Recreate build_export_directory directory
  remove_directory(build_export_directory)
  create_directory(build_export_directory)

  # write the parsed template
  with open(f"{build_export_directory}/index.html", "w") as web_page:
    web_page.write(output_from_parsed_template)

  # Copy assets
  source_directory = f"themes/{html_theme}/assets"
  destination_directory = f"{build_export_directory}/assets"

  copy_directory(source_directory, destination_directory)


def main():
  parser = argparse.ArgumentParser(
      description="pysen - Simple static site generator.")
  parser.add_argument(
      "action", nargs="?", choices=["new"], help="Specify the action to perform.")
  parser.add_argument(
      "file_path", nargs="?", help="Specify the file path new post.")

  args = parser.parse_args()

  if args.action == "new":
    file_status = check_file_status(args.file_path)
    if file_status == 0:
      create_post(args.file_path)
    elif file_status == 1:
      print(f"The file '{args.file_path}' already exists, didn't touch.")
    else:
      print(f"Cannot determine the status of the file '{args.file_path}'.")
  else:
    build_site()


if __name__ == "__main__":
  main()
