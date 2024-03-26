from lxml import etree
import zipfile
import re
from bs4 import BeautifulSoup
import string

class ExtractComments:
    p_id = 0
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

