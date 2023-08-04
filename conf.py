"""
    Configuration settings here
    You can modify configuration settings here
    acedev 2023.7.30
"""

# original header in the converted xhtml
global original_header
original_header = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
        '''

# new header for the output
global new_header
new_header = '''<?xml version="1.0" ?>
<html xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2022-02-16" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:acfr="https://taxonomies.xbrl.us/grip/2022/acfr" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns="http://www.w3.org/1999/xhtml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xbrli="http://www.xbrl.org/2003/instance" xml:lang="en-US"><head><title>Inline XBRL Sample</title><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><body>'''

# ix header for the output
global ix_header_start
ix_header_start = '''<div style="display:none">
  <ix:header>
    <ix:references>
      <link:schemaRef xlink:href="https://taxonomies.xbrl.us/grip/2022/grip-all_2022.xsd" xlink:type="simple"></link:schemaRef>
    </ix:references>
    <ix:resources>'''

global ix_header_end
ix_header_end ='''
      <xbrli:unit id="USD">
        <xbrli:measure>iso4217:USD</xbrli:measure>
      </xbrli:unit>
    </ix:resources>
  </ix:header>
</div>'''
# place id
global place_id
place_id = "0613882"

# valid characters for the first letter of table cell content
global valid_chars
valid_chars = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "-", ".","$"}

# file path for elements csv
global elements_path
elements_path = "elements.csv"

# need to convert D to I, context names
global d_to_i_contexts
d_to_i_contexts = ["acfr:FundBalance", "acfr:NetPositionAtBeginningOfPeriodAfterAdjustments", "acfr:NetPosition"]
##  "acfr:CashAndCashEquivalentsPerCashFlows",