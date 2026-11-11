import os
import shutil
import sys
from textnode import TextNode, TextType
from inline_markdown import markdown_to_html_node

if len(sys.argv) > 1:
    basepath = sys.argv[1]
else:
    basepath = "/"

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

def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        elif line == "#":
            return ""
    raise ValueError("No H1 found")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    title = extract_title(markdown_content)

    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    full_html = full_html.replace('href="/', f'href="{basepath}')
    full_html = full_html.replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for entry in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, entry)

        if os.path.isdir(from_path):
            new_dest_dir = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(from_path, template_path, new_dest_dir)

        elif os.path.isfile(from_path) and entry.endswith("md"):
            os.makedirs(dest_dir_path, exist_ok=True)

            html_filename = entry.replace(".md", ".html")
            dest_path = os.path.join(dest_dir_path, html_filename)

            generate_page(from_path, template_path, dest_path)


def main():
    source_dir = "static"
    dest_dir = "docs"

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
            dest_dir_path="docs/"
        )

if __name__ == "__main__":
    main()
