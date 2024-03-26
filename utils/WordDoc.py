import mammoth
import zipfile
from lxml import etree
from bs4 import BeautifulSoup
from typing import *

class CommentExtractor:
    """
    A class to extract comments from a Word document and
    match them to corresponding paragraphs in an HTML representation.
    """
    
    NAMESPACES = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    def __init__(self, docx_file_name):
        self.docx_file_name = docx_file_name
    
    def get_comments_and_text(self, html : str) -> Tuple[str, List[str]]:
        """
        Extract comments from a Word document and match them to corresponding paragraphs in HTML.
        Returns a tuple containing the HTML with comments inserted and a list of extracted comments.
        """
        try:
            # Open the DOCX file as a ZIP and read the comments and document XML.
            with zipfile.ZipFile(self.docx_file_name) as docx_zip:
                comments_xml = docx_zip.read('word/comments.xml')
                document_xml = docx_zip.read('word/document.xml')

            # Parse the XML to extract comments and document paragraphs.
            comments_tree = etree.XML(comments_xml)
            comments = comments_tree.xpath('//w:comment', namespaces=self.NAMESPACES)
            document_tree = etree.XML(document_xml)
            paragraphs = document_tree.xpath('//w:p', namespaces=self.NAMESPACES)

            # Initialize BeautifulSoup with the provided HTML content.
            soup = BeautifulSoup(html, "html.parser")

            # Initialize a dictionary to hold extracted comment data.
            extracted_comments = []

            # Parse each comment and find its associate paragraph in document XML.
            for comment in comments:
                comment_data = self.parse_comment(comment)
                
                # Match comment to paragraph using comment range tags in the document XML.
                comment_range_start = comment_data['comment_range_start']
                matched_paragraph = self.find_matching_paragraph(paragraphs, comment_range_start)
                if matched_paragraph is not None:
                    comment_data['selected_text'] = ''.join(matched_paragraph.itertext())
                    self.insert_comment_into_html(soup, comment_data)
                extracted_comments.append(comment_data)

            return str(soup), extracted_comments
        except Exception as e:
            print(f"An error occurred while extracting comments: {e}")
            return html, []
        
    def parse_comment(self, comment):
        """Extract attributes and text from a comment element."""
        comment_id = comment.get(f'{{{self.NAMESPACES["w"]}}}id')
        comment_text = comment.xpath('string(.)', namespaces=self.NAMESPACES)
        comment_range_start = comment.xpath('.//w:commentRangeStart', namespaces=self.NAMESPACES)[0]
        return {'id': comment_id, 'text': comment_text, 'comment_range_start': comment_range_start}

    def find_matching_paragraph(self, paragraphs, comment_range_start):
        """Find the paragraph in the Word document XML that matches the comment range start."""
        for paragraph in paragraphs:
            paragraph_comment_starts = paragraph.xpath('.//w:commentRangeStart', namespaces=self.NAMESPACES)
            if paragraph_comment_starts and paragraph_comment_starts[0] == comment_range_start:
                return paragraph
        return None

    def insert_comment_into_html(self, soup, comment_data):
        """
        Insert the comment into the BeautifulSoup HTML representation.
        """
        comment_id = comment_data['id']
        paragraphs = soup.find_all('p', {'id': comment_id})
        for p in paragraphs:
            new_tag = soup.new_tag('span', **{'class': 'comment', 'data-comment-id': comment_id})
            new_tag.string = comment_data['text']
            p.insert_after(new_tag)
            
class WordDoc:

    def __init__(self, docx_file_name: str):
        # initialize values
        self.docx_file_name = docx_file_name
        self.html_content = ""
        self.images = []
        self.comments = []
        # process
        self.convert_to_html()

    def convert_to_html(self):
        """ Use mammoth to extract content and images """
        with open(self.docx_file_name, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            self.html_content = result.value
            self.images = result.messages  # Images are part of the messages in mammoth

    