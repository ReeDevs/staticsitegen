from decimal import HAVE_THREADS
from enum import Enum
import os
import re
from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node
from nodes import split_nodes_delimiter, split_nodes_image, split_nodes_link

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = []
    for block in markdown.split("\n\n"):
        if block.strip():
            blocks.append(block.strip())
    return blocks

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block) -> BlockType:
    if re.match(r"#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```") and len(block) >= 6:
        return BlockType.CODE

    lines = block.split("\n")

    is_quote = True
    for line in lines:
        if not line.startswith(">"):
            is_quote = False
            break
    if is_quote:
        return BlockType.QUOTE

    is_unordered = True
    for line in lines:
        if not line.startswith("- "):
            is_unordered = False
            break
    if is_unordered:
        return BlockType.UNORDERED_LIST

    is_ordered = True
    for i, line in enumerate(lines):
        expected_prefix = f"{i + 1}. "
        if not line.startswith(expected_prefix):
            is_ordered = False
            break
    if is_ordered:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    results = []
    for node in text_nodes:
        results.append(text_node_to_html_node(node))
    return results

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    collected_blocks = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                no_break = block.replace("\n", " ")
                children = text_to_children(no_break)
                collected_blocks.append(ParentNode("p", children))

            case BlockType.QUOTE:
                pattern = re.compile("^>\s?", re.MULTILINE)
                lines = [pattern.sub("", line) for line in block.splitlines()]
                cleaned = "".join(lines)
                children = text_to_children(cleaned)
                collected_blocks.append(ParentNode("blockquote", children))

            case BlockType.UNORDERED_LIST:
                li_nodes = []
                for line in block.strip().split("\n"):
                    line = line.strip()

                    if line.startswith("- ") or line.startswith("* "):
                        line_text = line[2:]
                    elif line.startswith("-") or line.startswith("*"):
                        line_text = line[1:]
                    else:
                        line_text = line

                    children = text_to_children(line_text.strip())
                    li_node = ParentNode(tag="li", children = children)
                    li_nodes.append(li_node)

                collected_blocks.append(ParentNode(tag="ul", children = li_nodes))

            case BlockType.ORDERED_LIST:
                li_nodes = []
                for line in block.strip().split("\n"):
                    line = line.strip()

                    line_text = re.sub(r'^\s*\d+[\.\)]?\s*', "", line)

                    children = text_to_children(line_text.strip())
                    li_node = ParentNode(tag="li", children = children)
                    li_nodes.append(li_node)

                collected_blocks.append(ParentNode(tag="ol", children = li_nodes))

            case BlockType.HEADING:
                match = re.match(r'^(#{1,6}) (.*)', block)

                if match:
                    hashes, rest_of_text = match.groups()
                    level = len(hashes)
                    children = text_to_children(rest_of_text)
                    header = ParentNode(f"h{level}", children)
                    collected_blocks.append(header)

            case BlockType.CODE:
                block = block[3:-3]
                no_break = block.lstrip("\n")
                html_node = text_node_to_html_node(TextNode(no_break, TextType.TEXT))
                collected_blocks.append(ParentNode(tag="pre", children=[ParentNode(tag="code", children=[html_node])]))

    return ParentNode(tag="div", children=collected_blocks)
