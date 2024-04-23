import mammoth
import zipfile
from lxml import etree
from bs4 import BeautifulSoup
from typing import *

NAMESPACES = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

class Comment:
    """ Class to represent a Word comment """

    def __init__(self, comment):
        self.p_num = None # paragraph number in converted html
        self.selected_text = None
        self.comment_id = comment.get(f'{{{NAMESPACES["w"]}}}id')
        full_text = comment.xpath('string(.)', namespaces = NAMESPACES)
        if ',' in full_text :
            self.comment_text, self.context_id = [s.strip() for s in full_text.split(',')]
        else:
            self.comment_text, self.context_id = full_text, None

    def match_paragraph(self, paragraphs):
        """Find corresponding text in Word document where comment exists"""
        #Find all instances of commentRangeStart in document.xml and match to comment_id
        for i in range(len(paragraphs)):
            # Search for comment range Start inside each paragraph
            range_start = paragraphs[i].xpath('.//w:commentRangeStart/@w:id', namespaces=NAMESPACES)
            # Assume only one comment per text section, or give an error
            if len(range_start) > 1:
                return "Error: only one comment per text section allowed"
            if range_start == [self.comment_id]:
                # Extract selected text corresponding to the comment
                self.selected_text = paragraphs[i].xpath('string(.)', namespaces=NAMESPACES).strip()
                self.p_num = i

    def is_taggable(self):
        return self.context_id is not None

    def ix_tag(self):
        # TODO: replace with better implementation jinja formatting? inherit cell class
        #return f"<b> COMMENT: {self.comment_text} </b>"
        return (f'''\n<ix:nonFraction contextRef="{self.context_id}" name="acfr:{self.comment_text}" unitRef="pure" id="p{self.p_num}_c{self.comment_id}" decimals="0" format="ixt:num-dot-decimal" >
    {self.selected_text}
</ix:nonFraction>\n\n''')

class WordDoc:
    """ Class to represent a Word file """
    def __init__(self, docx_file):
        self.html_content = self.convert_to_html(docx_file)
        self.html_content = self.remove_links()
        self.html_content = self.remove_empty_tags()
        self.html_content = self.insert_comments(docx_file) 

    @staticmethod
    def convert_image(image):
        """ 
        Save the image; return a dictionary {"src" : <file location>}
        """
        return {"src" : ""}

    def convert_to_html(self, docx_file):
        """ Use mammoth to extract content and images """
        result = mammoth.convert_to_html(docx_file, convert_image = mammoth.images.img_element(self.convert_image))
        return result.value
        # TODO: convert images to files
        #self.images = result.messages 
    
    def soup(self):
        return BeautifulSoup(self.html_content, "lxml")

    def get_html(self):
        """Format the parsed HTML onto several lines (human readable)"""
        return self.html_content
    
    def remove_links(self):
        """ ixbrl does not allow anchors without hrefs; for now, just remove these """
        soup = self.soup()
        for a in soup.find_all(['a']):
            a.decompose()
        return soup.prettify()
    
    def remove_empty_tags(self):
        """ Recursively find all tags with no content and remove them """
        soup = self.soup()
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0 and not tag.contents:
                tag.extract()
        return str(soup)
    
    def extract_comments(self, docx_file) -> List[Comment]:
        """
        Extract comments from a Word document and match them to corresponding paragraphs in HTML.
        Returns HTML with comments inserted.
        """
        # initialize list of comments
        comment_list = []
        try:
            # Zip the docx file to extract its xml content
            with zipfile.ZipFile(docx_file) as docx_zip:
                comments_xml = docx_zip.read('word/comments.xml')
                document_xml = docx_zip.read('word/document.xml')

            # Parse the XML to extract comments and document paragraphs
            comments_tree = etree.XML(comments_xml)
            comments = comments_tree.xpath('//w:comment', namespaces=NAMESPACES)
            document_tree = etree.XML(document_xml)
            # create list of non-empty paragraphs
            paragraphs = []
            for p in document_tree.xpath('//w:p', namespaces=NAMESPACES):
                if ''.join(p.itertext()).strip() != '':
                    paragraphs.append(p)

            # Parse each comment and find its associate paragraph in document XML
            for c in comments:
                comment = Comment(c)
                if comment.is_taggable():
                    comment.match_paragraph(paragraphs)
                    comment_list.append(comment)

        except Exception as e:
            print(f"An error occurred while extracting comments: {e}")
        return comment_list
    
    def insert_comments(self, docx_file):
        """ Add comments into html """
        soup = self.soup()
        # grab all html code tagged with <p>
        p_tags = [p for p in soup.find_all('p')]
        comment_list = self.extract_comments(docx_file)
        # add the relevant ixbrl tag in each corresponding paragraph
        for c in comment_list:
            p_tags[c.p_num].replace_with(c.ix_tag())
        # TODO: remove this after fixing the jinja template in the Comment class
        html = str(soup).replace('&gt;', '>').replace('&lt;', '<') 
        return html