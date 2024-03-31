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
        print(' Comment Extracted.')
        return result
    
def extract_text_and_images_from_docx(file_path):

    result = mammoth.convert_to_html(file_path)
    html = result.value  # Extracted HTML content
    images = result.messages  # Extracted images, if any    
    updated_html =''
    soup = BeautifulSoup(html,"html.parser")
    p_html =[]
    # Remove a tags    
    for a in soup.find_all(['a']):
        a.decompose()

    for p_tag in soup.find_all('p'):
        validated =True
        
        if p_tag.text.strip() !='' :
            for char in p_tag.text:
                if char in string.ascii_letters:
                    validated = False 
                    break
                
                elif (len(p_tag.text)>5 and ('-' in p_tag.text or '%' in p_tag.text)):
                    validated = False 
                    break


            if validated:        
                p_html.append(p_tag)
    
    result = ExtractComments.get_comments_and_text(file_path,html)
    if result: 
        for  i in range (0,len(result['comments'])):
            comment, selected_text, p_count =result['comments'][i],result['selected_text'][i],result['count'][i]
            context_id = result['context_id'][i]
            p_html[p_count].replace_with(f'''\n\n<ix:nonFraction contextRef="{context_id}" name="acfr:{comment}" unitRef="pure" id="p{ExtractComments.p_id}" decimals="0" format="ixt:num-dot-decimal" >
    {selected_text}
</ix:nonFraction>\n\n''')
            ExtractComments.p_id +=1
            
        updated_html = str(soup)
        updated_html = updated_html.replace('&gt;', '>')
        updated_html = updated_html.replace('&lt;', '<')           
        return updated_html,images
    
    updated_html = str(soup)
    return updated_html, images