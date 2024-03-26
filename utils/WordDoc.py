import mammoth
import zipfile
from lxml import etree
from bs4 import BeautifulSoup
import os

class CommentExtractor:
    """
    This class extracts comments from a DOCX file and correlates them
    with the text in a given HTML generated from the DOCX content.
    """ 
    NAMESPACES = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    def __init__(self, docx_file_name):
        self.docx_file_name = docx_file_name
        self.p_id = 0  # Class attribute for paragraph IDs
        
    def extract_comments(self):
        """
        Extracts all comments from the DOCX file and returns a list of comments data.
        Each comment data is a dictionary with 'id', 'text', and 'context_id' (if present).
        """
        with zipfile.ZipFile(self.docx_file_name) as docx_zip:
            comments_xml = docx_zip.read('word/comments.xml')
            et_comments = etree.XML(comments_xml)
            comments = et_comments.xpath('//w:comment', namespaces=self.NAMESPACES)

        comments_data = []
        for c in comments:
            comment_id = c.get(f"{{{self.NAMESPACES['w']}}}id")
            comment_text = c.xpath('string(.)', namespaces=self.NAMESPACES)
            # TODO: readdress to generalize
            context_id = comment_text.split(',')[1].strip() if ',' in comment_text else None
            comments_data.append({
                'id': comment_id,
                'text': comment_text.split(',')[0].strip() if ',' in comment_text else comment_text.strip(),
                'context_id': context_id
            })
        return comments_data

    def get_html_with_comments(self, html):
        """
        Injects comments into the HTML at the correct positions and returns the modified HTML.
        The original HTML is converted into a BeautifulSoup object for parsing and manipulation.
        """
        # Parse the extracted HTML with BeautifulSoup.
        soup = BeautifulSoup(html, "html.parser")

        # Extract each comment, locate its corresponding paragraph and replace it with a marked element.
        for comment in self.extract_comments():
            paragraphs = soup.find_all(True, id=comment['id'])
            for paragraph in paragraphs:
                self.annotate_paragraph_with_comment(paragraph, comment)
        
        return str(soup)

    def annotate_paragraph_with_comment(self, paragraph, comment):
        """
        Replaces a paragraph in the HTML with an annotated version that includes the comment.
        """
        # TODO: replace hard-coding with an attribute in the class that will
        # be formatted in jinja templating
        annotated_paragraph = f'''
            <ix:nonFraction contextRef="{comment['context_id']}" name="acfr:{comment['text']}"
            unitRef="pure" id="p{self.p_id}" decimals="0"
            format="ixt:num-dot-decimal">{paragraph.get_text()}
            </ix:nonFraction>
        '''
        paragraph.replace_with(BeautifulSoup(annotated_paragraph, "html.parser"))
        self.p_id += 1

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

    