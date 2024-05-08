import mammoth
import zipfile
from lxml import etree
from bs4 import BeautifulSoup
from typing import *
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from app.utils.constants import custom_style_map


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
        self.doc = Document(docx_file)
        self.docx_file = docx_file
        html_content = self.convert_to_html(docx_file)
        self.soup = BeautifulSoup(html_content, "lxml")
        
        # Processing steps
        self.remove_links()
        #self.remove_empty_tags()
        self.insert_comments()
        self.identify_and_insert_html_page_breaks()
        #self.add_class_to_larger_fonts_in_html()
        #self.clean_tables()

    @staticmethod
    def convert_image(image):
        """ 
        Save the image; return a dictionary {"src" : <file location>}
        """
        return {"src" : ""}

    def convert_to_html(self, docx_file):
        """ Use mammoth to extract content and images """
        result = mammoth.convert_to_html(docx_file, 
                                         style_map = custom_style_map,
                                         convert_image = mammoth.images.img_element(self.convert_image))
        html_content = result.value
        return html_content

    def remove_links(self):
        """ Remove anchors without hrefs """
        for a in self.soup.find_all('a'):
            a.decompose()
        self.update_html_content()

    def remove_empty_tags(self):
        """ Remove all tags with no content """
        for tag in self.soup.find_all():
            if len(tag.get_text(strip=True)) == 0 and not tag.contents:
                tag.extract()
        self.update_html_content()
    
    def update_html_content(self):
        """ Update the HTML content from the soup object """
        self.html_content = self.soup.prettify()

    def get_html(self):
        """ Return the HTML content """
        # Ensure the content is up-to-date
        self.update_html_content()
        return self.html_content

    def extract_comments(self) -> List[Comment]:
        """
        Extract comments from a Word document and match them to corresponding paragraphs in HTML.
        Returns HTML with comments inserted.
        """
        # initialize list of comments
        comment_list = []
        try:
            # Zip the docx file to extract its xml content
            with zipfile.ZipFile(self.docx_file) as docx_zip:
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
    
    def insert_comments(self):
        """ Add comments into HTML """
        # grab all html code tagged with <p>
        p_tags = self.soup.find_all('p')
        comment_list = self.extract_comments()
        
        # add the relevant ixbrl tag in each corresponding paragraph
        for comment in comment_list:
            if 0 <= comment.p_num < len(p_tags):
                p_tags[comment.p_num].replace_with(comment.ix_tag())
        self.update_html_content()
    
    # Page breaks (see corresponding css)

    def identify_and_insert_html_page_breaks(self):
        """Go through the converted HTML document and insert page breaks before paragraphs that contain only a number and are not contained in a table."""
        for paragraph in self.soup.find_all('p'):
            # Check if paragraph contains only a number and is not a child of a table
            if paragraph.string and paragraph.string.strip().isdigit() and not paragraph.find_parent('table'):
                # Create a div with the 'page-break' class and insert before this paragraph
                page_break_div = self.soup.new_tag("div", **{'class': 'page-break'})
                paragraph.insert_after(page_break_div)
        
        # Update the html_content with the modified soup
        self.update_html_content()

    # ID and make some text larger according to Word format
        # (not functional)
        
    def _add_mark_to_run(self, run):
        # This creates a new XML element to mark the larger text.
        mark_elm = OxmlElement('w:mark')
        run._r.append(mark_elm)

    def identify_larger_text(self, min_font_size_pt):
        """Identify runs with a font size larger than min_font_size_pt and mark them."""
        # Convert the font size to twips, the unit used by python-docx.
        for paragraph in self.doc.paragraphs:
            for run in paragraph.runs:
                if run.font.size and run.font.size.pt > min_font_size_pt:
                    self._add_mark_to_run(run)

    def add_class_to_larger_fonts_in_html(self, min_font_size_pt = 12):
        """Add a custom class to the HTML representation of paragraphs with a font size larger than min_font_size_pt."""
        # First, let's mark the larger text in the Word document using python-docx
        self.identify_larger_text(min_font_size_pt)
        
        # Iterate over all the paragraphs in the HTML
        for p in self.soup.find_all('p'):
            # Check if this paragraph contains a <w:mark>, which indicates larger text
            if p.find('w:mark'):
                # Create a new <span> with the custom_class
                new_span = self.soup.new_tag('span')
                new_span['class'] = "large-text"
                new_span.string = p.text
                
                # Clear the paragraph and replace its content with the new <span>
                p.clear()
                p.append(new_span)

                # Remove the <w:mark> tag as it's no longer needed
                mark = p.find('w:mark')
                if mark:
                    mark.decompose()
        
        # update html with new classes
        self.update_html_content()

    # Fix tables
    def clean_tables(self):
        # Parse the HTML content with BeautifulSoup
        tables = self.soup.find_all('table')
        if not tables:
            return "No table found!"

        for table in tables:
            all_rows = table.find_all('tr')
            
            # Determine which columns are empty (no content)
            num_cols = 0
            empty_cols = set()

            # Initialize empty_cols with all possible column indexes
            for row in all_rows:
                num_cols = max(num_cols, len(row.find_all(['td', 'th'])))
            empty_cols = set(range(num_cols))

            # Check content of all cells to update non_empty_cols
            for row in all_rows:
                for idx, cell in enumerate(row.find_all(['td', 'th'])):
                    if cell.get_text(strip=True):  # If cell has non-whitespace content, remove from empty_cols
                        empty_cols.discard(idx)

            # Iterate backwards through the columns and remove empty ones
            for row in all_rows:
                cols = row.find_all(['td', 'th'])
                for idx in sorted(empty_cols, reverse=True):
                    # If colspan is encountered, reduce it by the number of empty_cols to the right or remove the cell
                    if cols[idx].has_attr('colspan'):
                        colspan = int(cols[idx]['colspan'])
                        # Adjust colspan or remove cell if colspan only spans empty columns
                        new_colspan = colspan - sum(1 for col_idx in range(idx, idx + colspan) if col_idx in empty_cols)
                        if new_colspan <= 1:
                            cols[idx].decompose()  # Remove cell
                        else:
                            cols[idx]['colspan'] = str(new_colspan)
                    else:
                        cols[idx].decompose()  # Remove cell

            # Clean up empty tags like <p>, <strong>, keep only the text.
            for tag in table.find_all(['p', 'strong', 'em']):
                tag.unwrap()

        # Output the cleaned HTML
        self.update_html_content()