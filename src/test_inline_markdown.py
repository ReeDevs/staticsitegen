import unittest
from textnode import TextNode, TextType
from inline_markdown import text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node, extract_title

class TestMarkdown(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_headings(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)

        # False cases for headings
        self.assertEqual(block_to_block_type("####### Heading 7"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("#NoSpace"), BlockType.PARAGRAPH)

    def test_code_blocks(self):
        code_block = "```\ndef my_func():\n    return True\n```"
        self.assertEqual(block_to_block_type(code_block), BlockType.CODE)

        # Single line minimal code block
        self.assertEqual(block_to_block_type("```code```"), BlockType.CODE)

        # False cases for code blocks
        self.assertEqual(block_to_block_type("``not enough backticks``"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```unclosed code"), BlockType.PARAGRAPH)

    def test_quote_blocks(self):
        single_quote = "> This is a quote line."
        multi_quote = "> First line\n>Second line with no space\n> Third line"
        self.assertEqual(block_to_block_type(single_quote), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(multi_quote), BlockType.QUOTE)

        # False cases for quotes
        broken_quote = "> Line 1\nLine 2 missing chevron\n> Line 3"
        self.assertEqual(block_to_block_type(broken_quote), BlockType.PARAGRAPH)

    def test_unordered_lists(self):
        single_item = "- Item 1"
        multi_items = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(single_item), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type(multi_items), BlockType.UNORDERED_LIST)

        # False cases for unordered lists
        self.assertEqual(block_to_block_type("-No space after dash"), BlockType.PARAGRAPH)
        broken_list = "- Item 1\n* Item 2 with asterisks\n- Item 3"
        self.assertEqual(block_to_block_type(broken_list), BlockType.PARAGRAPH)

    def test_ordered_lists(self):
        single_item = "1. First item"
        multi_items = "1. Item one\n2. Item two\n3. Item three"
        self.assertEqual(block_to_block_type(single_item), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type(multi_items), BlockType.ORDERED_LIST)

        # False cases for ordered lists
        self.assertEqual(block_to_block_type("1.No space"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("2. Starting at wrong number"), BlockType.PARAGRAPH)

        broken_sequence = "1. One\n3. Skipped two"
        self.assertEqual(block_to_block_type(broken_sequence), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        simple_paragraph = "Just a standard sentence block with multiple words."
        multi_line_paragraph = "Line one of a text block.\nLine two of a text block."
        self.assertEqual(block_to_block_type(simple_paragraph), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type(multi_line_paragraph), BlockType.PARAGRAPH)

    def test_paragraphs2(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )


    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_standard_h1(self):
        """Should extract a standard H1 title and strip surrounding whitespace."""
        self.assertEqual(extract_title("# Hello"), "Hello")
        self.assertEqual(extract_title("#   Hello World   "), "Hello World")

    def test_multiline_markdown(self):
        """Should find the H1 even if it's buried in other markdown elements."""
        markdown_text = (
            "## Subtitle\n"
            "Some paragraph text.\n"
            "# The Real Title\n"
            "More content here."
        )
        self.assertEqual(extract_title(markdown_text), "The Real Title")

    def test_empty_h1(self):
        """Should handle an empty or whitespace-only H1 gracefully."""
        self.assertEqual(extract_title("# "), "")
        self.assertEqual(extract_title("#"), "")

    def test_no_h1_raises_exception(self):
        """Should raise a ValueError if no line starts with a single #."""
        with self.assertRaises(ValueError):
            extract_title("## This is an H2")
        with self.assertRaises(ValueError):
            extract_title("Just text, no headers at all.")

    def test_false_positives(self):
        """Should not match lines where # is embedded or part of an H2+."""
        with self.assertRaises(ValueError):
            extract_title("This is # not a title")
        with self.assertRaises(ValueError):
            extract_title("### Triple Hash Title")

if __name__ == "__main__":
    unittest.main()
