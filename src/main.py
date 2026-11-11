import os
import shutil
from textnode import TextNode, TextType
from inline_markdown import generate_page, generate_pages_recursive

def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def copy_recursive(src, dst):
    if not os.path.exists(dst):
        os.mkdir(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Copied file: {src_path} -> {dst_path}")
        elif os.path.isdir(src_path):
            print(f"Creating directory: {dst_path}")
            copy_recursive(src_path, dst_path)

def main():
    source_dir = "static"
    dest_dir = "public"

    clear_directory(dest_dir)
    print(f"Cleared {dest_dir} directory.")

    if os.path.exists(source_dir):
        copy_recursive(source_dir, dest_dir)
        print("Finished copying all contents.")
    else:
        print(f"Source directory '{source_dir}' does not exist.")

    print("Generating HTML pages recursively from content.")
    generate_pages_recursive(
            dir_path_content="content/",
            template_path="template.html",
            dest_dir_path="public/"
        )

if __name__ == "__main__":
    main()
