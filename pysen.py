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
import markdown
import frontmatter
import http.server
import socketserver
from functools import partial


__license__ = "MIT"


site_name = "verse"
html_theme = "poetry"  # directory name from under themes/
build_export_directory = f"public/{site_name}"


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
  filename = os.path.splitext(os.path.basename(file_path))[0]
  title = filename.replace('-', ' ').title()

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


def remove_everything_inside_directory(directory_path):
  try:
    # Iterate over all files and subdirectories inside the directory
    for filename in os.listdir(directory_path):
      file_path = os.path.join(directory_path, filename)

      # Remove files
      if os.path.isfile(file_path):
        os.unlink(file_path)

      # Remove directories (recursively)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)

    print(f"Successfully removed everything inside '{directory_path}'.")
  except Exception as e:
    print(f"Error: {e}")


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


def copy_directory_content(source_path, destination_path):
  try:
    # Ensure destination directory exists
    if not os.path.exists(destination_path):
      os.makedirs(destination_path)

    # Iterate through items in the source directory
    for item in os.listdir(source_path):
      source_item = os.path.join(source_path, item)
      destination_item = os.path.join(destination_path, item)

      # Copy file or directory
      if os.path.isdir(source_item):
        shutil.copytree(source_item, destination_item)
      else:
        shutil.copy2(source_item, destination_item)

    print(f"Contents of '{source_path}' copied to '{destination_path}' successfully.")

  except shutil.Error as e:
    print(f"Error: {e}")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


def load_template(html_theme, template_name):
  # Load Jinja template from the 'themes' directory
  template_loader = FileSystemLoader(f"themes/{html_theme}/layouts")
  template_env = Environment(loader=template_loader)
  return template_env.get_template(template_name)


def build_list_page(html_theme, base_template, build_export_directory, ctx):
  template = load_template(html_theme, base_template)
  rendered_output = template.render(ctx=ctx)
  # Save the rendered output to an HTML file
  with open(f"{build_export_directory}/{base_template}", "w") as web_page:
    web_page.write(rendered_output)


def build_detail_page(html_theme, base_template, build_export_directory, content_file_path, ctx):
  template = load_template(html_theme, base_template)
  rendered_output = template.render(ctx=ctx)
  post_filename = os.path.basename(content_file_path)
  post_save_directory = f"{build_export_directory}/{post_filename.split('.')[0]}"
  create_directory(post_save_directory)
  # Save the rendered output to an HTML file
  with open(f"{post_save_directory}/index.html", "w") as web_page:
    web_page.write(rendered_output)


def get_post_info(file_path):
  document = frontmatter.load(file_path)
  front_matter = document.metadata
  markdown_content = document.content
  html_content = markdown.markdown(markdown_content)
  ctx = {
      "title": front_matter.get("title", "Untitled"),
      "date": front_matter.get("date", "Undated"),
      "draft": front_matter.get("draft", True),
      "content": html_content,
      "filename": os.path.basename(file_path).split(".")[0],
  }
  return ctx


def build_site():
  content_directory = "content"
  post_directory = f"{content_directory}/posts"

  # Recreate build_export_directory directory
  create_directory(build_export_directory)
  remove_everything_inside_directory(build_export_directory)

  # Set site values
  site_ctx = {
      "name": site_name,
      "display_name": "Verse",
      "tagline": "",
      "footer": f'Copyright © 2024 <a href="https://hasithsen.pages.dev" class="text-decoration-none">hsen</a>. Powered by <a href="https://github.com/hasithsen/pysen" class="text-decoration-none">Pysen</a>.',
  }

  # Get post filename list from content directory
  post_file_paths = [os.path.join(post_directory, f) for f in os.listdir(
      post_directory) if os.path.isfile(os.path.join(post_directory, f))]
  post_ctx_list = []
  # Get post info for each post
  for file_path in post_file_paths:
    # Get post info
    post_ctx = get_post_info(file_path)
    # Skip drafts
    if post_ctx['draft']:
      continue
    post_ctx_list.append(post_ctx)
    # We have post info
    # if post has associated asset directory, copy it to build_export_directory
    directory_path = file_path.split(".")[0] + "/"
    if check_file_status(directory_path):
      copy_directory_content(directory_path, build_export_directory + '/' + post_ctx["filename"])
    # build post page
    build_detail_page(html_theme, "post.html",
                      build_export_directory, file_path, (site_ctx, post_ctx))

  # Get about page info
  file_path = f"{content_directory}/about.md"
  post_ctx = get_post_info(file_path)
  # Build about page
  build_detail_page(html_theme, "about.html",
                    build_export_directory, file_path, (site_ctx, post_ctx))
  # Build index page
  build_list_page(html_theme, "index.html",
                  build_export_directory, (site_ctx, post_ctx_list))

  # Copy theme assets
  source_directory = f"themes/{html_theme}/assets"
  destination_directory = f"{build_export_directory}/assets"

  copy_directory(source_directory, destination_directory)


def serve_site():
  port = 8000
  directory = "public"

  Handler = partial(http.server.SimpleHTTPRequestHandler, directory=directory)

  with socketserver.TCPServer(("", port), Handler) as httpd:
    print(
        f"Serving on port {port} (http://localhost:{port}/) from the directory: {directory}")
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print("\nServer stopped.")


def main():
  parser = argparse.ArgumentParser(
      description="pysen - Simple static site generator.")
  parser.add_argument(
      "action", nargs="?", choices=["new", "serve", "server"], help="Specify the action to perform.")
  parser.add_argument(
      "file_path", nargs="?", help="Specify the file path for new post.")

  args = parser.parse_args()

  if args.action == "new":
    file_status = check_file_status(args.file_path)
    if file_status == 0:
      create_post(args.file_path)
    elif file_status == 1:
      print(f"The file '{args.file_path}' already exists, didn't touch.")
    else:
      print(f"Cannot determine the status of the file '{args.file_path}'.")
  elif args.action in ("serve", "server"):
    serve_site()
  else:
    build_site()


if __name__ == "__main__":
  main()
