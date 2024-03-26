from lxml import etree
import zipfile
from bs4 import BeautifulSoup
import string
import mammoth

class WordDoc:
    def __init__(self, docx_file_name: str):
        result = mammoth.convert_to_html(docx_file_name)
        self._raw_html = result.value
        self._images = result.messages
        self._soup = BeautifulSoup(self._raw_html, "html.parser")

    def remove_links(self):
        """ ixbrl does not allow anchors without hrefs; for now, just remove these """
        for a in self._soup.find_all(['a']):
            a.decompose()

    def validate_paragraphs(self):
        """ ? """
        valid_paragraphs = []
        for p_tag in self._soup.find_all('p'):
            if self.is_valid_paragraph(p_tag.text):
                valid_paragraphs.append(p_tag)
        return valid_paragraphs

    @staticmethod
    def is_valid_paragraph(text):
        """" ? """
        if text.strip() == '':
            return False
        for char in text:
            if char in string.ascii_letters or \
               (len(text) > 5 and ('-' in text or '%' in text)):
                return False
        return True

    def replace_paragraphs_with_comments(self, comments_data, paragraphs):
        """ unclear... """
        for i, comment in enumerate(comments_data['comments']):
            selected_text = comments_data['selected_text'][i]
            p_count = comments_data['count'][i]
            context_id = comments_data['context_id'][i]
            paragraphs[p_count].replace_with(
                f'\n\n<ix:nonFraction contextRef="{context_id}" '
                f'name="acfr:{comment}" unitRef="pure" id="p{ExtractComments.p_id}" '
                f'decimals="0" format="ixt:num-dot-decimal" >{selected_text}'
                '</ix:nonFraction>\n\n'
            )

    def process_document(self):
        """ return processed html and images """
        self.remove_links()
        paragraphs = self.validate_paragraphs()
        comments_data = self.get_comments_and_text(self._file_path, self._raw_html)

        if comments_data:
            self.replace_paragraphs_with_comments(comments_data, paragraphs)

        updated_html = str(self._soup)
        updated_html = updated_html.replace('&gt;', '>').replace('&lt;', '<')

        return updated_html, self._images

        
    def get_comments_and_text(docxFileName, html):
        try:
            ooXMLns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            docxZip = zipfile.ZipFile(docxFileName)
            commentsXML = docxZip.read('word/comments.xml')
            et_comments = etree.XML(commentsXML)
            comments = et_comments.xpath('//w:comment', namespaces=ooXMLns)

            mainXML = docxZip.read('word/document.xml')
            et_main = etree.XML(mainXML)

            paragraphs = et_main.xpath(f'''
                //w:p[
                    normalize-space(.) and  
                    not(.="00") and 
                    (string-length(.) = 1 or not(starts-with(normalize-space(.), "-"))) and 
                    (
                        string-length(.) <=5 or 
                        (
                            translate(., "{string.digits}", "") != "" and 
                            string-length(normalize-space(translate(., "{string.digits}-", ""))) != 0
                        )
                        and not(contains(normalize-space(.), "%"))
                    )
                ]
            ''', namespaces=ooXMLns)
            cleaned_paragraphs = []
            for p in paragraphs:
                text = p.xpath('string(.)', namespaces=ooXMLns).strip()
                if not any(char.isalpha() for char in text):
                    cleaned_paragraphs.append(p)

            result = {'context_id':[],'comments':[],'selected_text':[],'count':[]}
            soup = BeautifulSoup(html,"html.parser")

            for c in comments:
                # Attributes:
                comment_text = c.xpath('string(.)', namespaces=ooXMLns)
                # Extract selected text corresponding to the comment
                comment_id = c.xpath('@w:id', namespaces=ooXMLns)[0]
                count=0
                for p, p_html in zip(cleaned_paragraphs, soup.find_all('p')): 
            
                    if p.xpath('.//w:commentRangeStart/@w:id', namespaces=ooXMLns) == [comment_id]:
                        selected_text = p.xpath('string(.)', namespaces=ooXMLns).strip()
                        if ',' in comment_text :
                            result['context_id'].append(comment_text.split(',')[1].strip())

                            result['comments'].append(comment_text.split(',')[0].strip())

                        result['selected_text'].append(selected_text)
                        result['count'].append(count)
                        
                    count+=1                

            print('There are no comments in this document.')
        except Exception as e:
            return None
        print(' Comment Extracted.',len(soup.find_all('p')) )
        return result

