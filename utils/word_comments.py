from lxml import etree
import zipfile
import re
from bs4 import BeautifulSoup

class ExtractComments:
        
    def get_comments_and_text(docxFileName, html):
        if docxFileName == 'static/input_files/word_documents/CA Clayton 2022 Cover Page and Introductory Section.docx':
            try:
                ooXMLns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

                docxZip = zipfile.ZipFile(docxFileName)
                commentsXML = docxZip.read('word/comments.xml')
                et_comments = etree.XML(commentsXML)
                comments = et_comments.xpath('//w:comment', namespaces=ooXMLns)

                mainXML = docxZip.read('word/document.xml')
                et_main = etree.XML(mainXML)
                paragraphs = et_main.xpath('//w:p[normalize-space(.) and (string-length(.) < 10 or (number(.) != number(.) and not(starts-with(normalize-space(.), "-"))))]', namespaces=ooXMLns)
                
                # Extract selected text for each comment
                soup = BeautifulSoup(html,"html.parser")
                
                for p_tag in soup.find_all('p'):
                    if p_tag.text =='' and not p_tag.img:
                        p_tag.extract()
                cnt=0
                # Display HTML tags 
                for c in comments:
                    # Attributes:
                    comment_text = c.xpath('string(.)', namespaces=ooXMLns)
                    # Extract selected text corresponding to the comment
                    comment_id = c.xpath('@w:id', namespaces=ooXMLns)[0]
                    selected_text = ""
                    
                    updated_html = ''
                    for p, p_html in zip(paragraphs, soup.find_all('p')):      
                        # if cnt>=0 and cnt<20:                  
                        #     # print(p.xpath('string(.)', namespaces=ooXMLns).strip(),"cnt =",cnt, p_html)
                        #     pass
                        # if p.xpath('string(.)', namespaces=ooXMLns).strip() != p_html.text:
                        #     cnt+=1
                        
                        if p.xpath('.//w:commentRangeStart/@w:id', namespaces=ooXMLns) == [comment_id]:
                            selected_text = p.xpath('string(.)', namespaces=ooXMLns).strip()
                            print(selected_text,comment_text)
                            p_html.string= f"<ix:nonfraction > {selected_text} </ix:nonfraction>"

                updated_html = str(soup)
                updated_html = updated_html.replace('&lt;', '<')
                updated_html = updated_html.replace('&gt;', '>')
                print('Comments extracted from this document.')
            except Exception as e:
                print('There are no comments in this document.')
                return None

            return updated_html

