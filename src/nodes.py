from textnode import TextType, TextNode
import re

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError("Invalid markdown syntax")

        for i, part in enumerate(parts):
            if part == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        current_text = node.text
        images = extract_markdown_images(current_text)

        if not images:
            new_nodes.append(node)
            continue

        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            sections = current_text.split(image_markdown, 1)

            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

            current_text = sections[1]

        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        current_text = node.text
        links = extract_markdown_links(current_text)

        if not links:
            new_nodes.append(node)
            continue

        for anchor_text, url in links:
            link_markdown = f"[{anchor_text}]({url})"
            sections = current_text.split(link_markdown, 1)

            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))

            current_text = sections[1]

        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes
