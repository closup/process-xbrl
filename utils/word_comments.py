from lxml import etree
import zipfile

class ExtractComments:
    def get_comments_and_text(docxFileName):
        try:
            ooXMLns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            docxZip = zipfile.ZipFile(docxFileName)
            # Extract comments
            commentsXML = docxZip.read('word/comments.xml')
            et_comments = etree.XML(commentsXML)
            comments = et_comments.xpath('//w:comment', namespaces=ooXMLns)
            # Extract main document content
            mainXML = docxZip.read('word/document.xml')
            et_main = etree.XML(mainXML)
            paragraphs = et_main.xpath('//w:p', namespaces=ooXMLns)
            comment_details = {"Comment":[],"SelectedText":[]}
            # Extract selected text for each comment
            for c in comments:
                # Attributes:
                comment_text = c.xpath('string(.)', namespaces=ooXMLns)
                # Extract selected text corresponding to the comment
                comment_id = c.xpath('@w:id', namespaces=ooXMLns)[0]
                selected_text = ""
                for p in paragraphs:
                    if p.xpath('.//w:commentRangeStart/@w:id', namespaces=ooXMLns) == [comment_id]:
                        selected_text = p.xpath('string(.)', namespaces=ooXMLns)
                        break        
                comment_details['Comment'].append(comment_text)
                comment_details['SelectedText'].append(selected_text.strip())
        except:
            print('There is no comments in this page')
            return None
        return comment_details

## NOTE : Able to get the comment using lxml,zip file
# from lxml import etree
# import zipfile
# ooXMLns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
# def get_comments(docxFileName):
#   docxZip = zipfile.ZipFile(docxFileName)
#   commentsXML = docxZip.read('word/comments.xml')
#   et = etree.XML(commentsXML)
#   comments = et.xpath('//w:comment',namespaces=ooXMLns)
#   for c in comments:
#     # attributes:
#     print(c.xpath('@w:author',namespaces=ooXMLns))
#     print(c.xpath('@w:date',namespaces=ooXMLns))
#     # string value of the comment:
#     print(c.xpath('string(.)',namespaces=ooXMLns))
# get_comments('static/input_files/word_documents/CA Clayton 2022 Cover Page and Introductory Section.docx')



## NOTE getting only the comments not the reference text
# doc = Document(file_path) # Trying to get the commented text from the document
# nsmap = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
# comments = []
# # get the comments from the document  
# for rel in doc.part.rels.values():
#     if "comments" in rel.target_ref:
#         comment_part = rel.target_part
#         xml_content = comment_part.blob
#         root = etree.fromstring(xml_content)
        
#         for comment in root.findall(".//w:comment", namespaces=nsmap):
#             comment_id = comment.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')

#             comment_text = ""
#             for p in comment.findall(".//w:p", namespaces=nsmap):
#                 for r in p.findall(".//w:r", namespaces=nsmap):
                    
#                     text = "".join([t.text for t in r.findall(".//w:t", namespaces=nsmap) if t.text])
#                     comment_text += text.strip()
            
#             comments.append((comment_id, comment_text.strip()))



## NOTE : getting some commands but not working in python v > 12 
# import aspose.words as aw

# doc = aw.Document("static/input_files/word_documents/CA Clayton 2022 Cover Page and Introductory Section.docx")


# class ExtractContentHelper:

#     @staticmethod
#     def extract_content(start_node: aw.Node, end_node: aw.Node, is_inclusive: bool):

#         # First, check that the nodes passed to this method are valid for use.
#         ExtractContentHelper.verify_parameter_nodes(start_node, end_node)

#         # Create a list to store the extracted nodes.
#         nodes = []

#         # If either marker is part of a comment, including the comment itself, we need to move the pointer
#         # forward to the Comment Node found after the CommentRangeEnd node.
#         if end_node.node_type == aw.NodeType.COMMENT_RANGE_END and is_inclusive:
#             node = ExtractContentHelper.find_next_node(aw.NodeType.COMMENT, end_node.next_sibling)
#             if node is not None:
#                 end_node = node

#         # Keep a record of the original nodes passed to this method to split marker nodes if needed.
#         original_start_node = start_node
#         original_end_node = end_node

#         # Extract content based on block-level nodes (paragraphs and tables). Traverse through parent nodes to find them.
#         # We will split the first and last nodes' content, depending if the marker nodes are inline.
#         start_node = ExtractContentHelper.get_ancestor_in_body(start_node)
#         end_node = ExtractContentHelper.get_ancestor_in_body(end_node)

#         is_extracting = True
#         is_starting_node = True
#         # The current node we are extracting from the document.
#         curr_node = start_node

#         # Begin extracting content. Process all block-level nodes and specifically split the first
#         # and last nodes when needed, so paragraph formatting is retained.
#         # Method is a little more complicated than a regular extractor as we need to factor
#         # in extracting using inline nodes, fields, bookmarks, etc. to make it useful.
#         while is_extracting:

#             # Clone the current node and its children to obtain a copy.
#             clone_node = curr_node.clone(True)
#             is_ending_node = curr_node == end_node

#             if is_starting_node or is_ending_node:

#                 # We need to process each marker separately, so pass it off to a separate method instead.
#                 # End should be processed at first to keep node indexes.
#                 if is_ending_node:
#                     # !isStartingNode: don't add the node twice if the markers are the same node.
#                     ExtractContentHelper.process_marker(clone_node, nodes, original_end_node, curr_node, is_inclusive, False, not is_starting_node, False)
#                     is_extracting = False

#                 # Conditional needs to be separate as the block level start and end markers, maybe the same node.
#                 if is_starting_node:
#                     ExtractContentHelper.process_marker(clone_node, nodes, original_start_node, curr_node, is_inclusive, True, True, False)
#                     is_starting_node = False
#             else:
#                 # Node is not a start or end marker, simply add the copy to the list.
#                 nodes.append(clone_node)

#             # Move to the next node and extract it. If the next node is None,
#             # the rest of the content is found in a different section.
#             if curr_node.next_sibling is None and is_extracting:
#                 # Move to the next section.
#                 next_section = curr_node.get_ancestor(aw.NodeType.SECTION).next_sibling.as_section()
#                 curr_node = next_section.body.first_child
#             else:
#                 # Move to the next node in the body.
#                 curr_node = curr_node.next_sibling

#         # For compatibility with mode with inline bookmarks, add the next paragraph (empty).
#         if is_inclusive and original_end_node == end_node and not original_end_node.is_composite:
#             ExtractContentHelper.include_next_paragraph(end_node, nodes)

#         # Return the nodes between the node markers.
#         return nodes

#     #ExStart:CommonGenerateDocument
#     @staticmethod
#     def generate_document(src_doc: aw.Document, nodes):

#         dst_doc = src_doc.clone(False).as_document()

#         # Import each node from the list into the new document. Keep the original formatting of the node.
#         importer = aw.NodeImporter(src_doc, dst_doc, aw.ImportFormatMode.USE_DESTINATION_STYLES)

#         # Put the section from the source document to retain original section page setup.
#         dst_doc.append_child(importer.import_node(src_doc.last_section, True))

#         # Remove all children from the impirted section.
#         dst_doc.first_section.body.remove_all_children();

#         for node in nodes:
#             import_node = importer.import_node(node, True)
#             dst_doc.first_section.body.append_child(import_node)

#         return dst_doc
#     #ExEnd:CommonGenerateDocument

#     #ExStart:CommonExtractContentHelperMethods
#     @staticmethod
#     def verify_parameter_nodes(start_node: aw.Node, end_node: aw.Node):

#         # The order in which these checks are done is important.
#         if start_node is None:
#             raise ValueError("Start node cannot be None")
#         if end_node is None:
#             raise ValueError("End node cannot be None")

#         if start_node.document != end_node.document:
#             raise ValueError("Start node and end node must belong to the same document")

#         if start_node.get_ancestor(aw.NodeType.BODY) is None or end_node.get_ancestor(aw.NodeType.BODY) is None:
#             raise ValueError("Start node and end node must be a child or descendant of a body")

#         # Check the end node is after the start node in the DOM tree.
#         # First, check if they are in different sections, then if they're not,
#         # check their position in the body of the same section.
#         start_section = start_node.get_ancestor(aw.NodeType.SECTION).as_section()
#         end_section = end_node.get_ancestor(aw.NodeType.SECTION).as_section()

#         start_index = start_section.parent_node.index_of(start_section)
#         end_index = end_section.parent_node.index_of(end_section)

#         if start_index == end_index:

#             if (start_section.body.index_of(ExtractContentHelper.get_ancestor_in_body(start_node)) >
#                 end_section.body.index_of(ExtractContentHelper.get_ancestor_in_body(end_node))):
#                 raise ValueError("The end node must be after the start node in the body")

#         elif start_index > end_index:
#             raise ValueError("The section of end node must be after the section start node")

#     @staticmethod
#     def find_next_node(node_type: aw.NodeType, from_node: aw.Node):

#         if from_node is None or from_node.node_type == node_type:
#             return from_node

#         if from_node.is_composite:

#             node = ExtractContentHelper.find_next_node(node_type, from_node.as_composite_node().first_child)
#             if node is not None:
#                 return node

#         return ExtractContentHelper.find_next_node(node_type, from_node.next_sibling)


#     @staticmethod
#     def process_marker(clone_node: aw.Node, nodes, node: aw.Node, block_level_ancestor: aw.Node,
#         is_inclusive: bool, is_start_marker: bool, can_add: bool, force_add: bool):

#         # If we are dealing with a block-level node, see if it should be included and add it to the list.
#         if node == block_level_ancestor:
#             if can_add and is_inclusive:
#                 nodes.append(clone_node)
#             return

#         # cloneNode is a clone of blockLevelNode. If node != blockLevelNode, blockLevelAncestor
#         # is the node's ancestor that means it is a composite node.
#         assert clone_node.is_composite

#         # If a marker is a FieldStart node check if it's to be included or not.
#         # We assume for simplicity that the FieldStart and FieldEnd appear in the same paragraph.
#         if node.node_type == aw.NodeType.FIELD_START:
#             # If the marker is a start node and is not included, skip to the end of the field.
#             # If the marker is an end node and is to be included, then move to the end field so the field will not be removed.
#             if (is_start_marker and not is_inclusive) or (not is_start_marker and is_inclusive):
#                 while node.next_sibling is not None and node.node_type != aw.NodeType.FIELD_END:
#                     node = node.next_sibling

#         # Support a case if the marker node is on the third level of the document body or lower.
#         node_branch = ExtractContentHelper.fill_self_and_parents(node, block_level_ancestor)

#         # Process the corresponding node in our cloned node by index.
#         current_clone_node = clone_node
#         for i in range(len(node_branch) - 1, -1, -1):

#             current_node = node_branch[i]
#             node_index = current_node.parent_node.index_of(current_node)
#             current_clone_node = current_clone_node.as_composite_node().get_child_nodes(node_type=current_node.node_type,is_deep=True)[node_index]

#             ExtractContentHelper.remove_nodes_outside_of_range(current_clone_node, is_inclusive or (i > 0), is_start_marker)

#         # After processing, the composite node may become empty if it has doesn't include it.
#         if can_add and (force_add or clone_node.as_composite_node().has_child_nodes):
#             nodes.append(clone_node)

#     @staticmethod
#     def remove_nodes_outside_of_range(marker_node: aw.Node, is_inclusive: bool, is_start_marker: bool):

#         is_processing = True
#         is_removing = is_start_marker
#         next_node = marker_node.parent_node.first_child

#         while is_processing and next_node is not None:

#             current_node = next_node
#             is_skip = False

#             if current_node == marker_node:
#                 if is_start_marker:
#                     is_processing = False
#                     if is_inclusive:
#                         is_removing = False
#                 else:
#                     is_removing = True
#                     if is_inclusive:
#                         is_skip = True

#             next_node = next_node.next_sibling
#             if is_removing and not is_skip:
#                 current_node.remove()

#     @staticmethod
#     def fill_self_and_parents(node: aw.Node, till_node: aw.Node):

#         nodes = []
#         current_node = node

#         while current_node != till_node:
#             nodes.append(current_node)
#             current_node = current_node.parent_node

#         return nodes

#     @staticmethod
#     def include_next_paragraph(node: aw.Node, nodes):

#         paragraph = ExtractContentHelper.find_next_node(aw.NodeType.PARAGRAPH, node.next_sibling).as_paragraph()
#         if paragraph is not None:

#             # Move to the first child to include paragraphs without content.
#             marker_node = paragraph.first_child if paragraph.has_child_nodes else paragraph
#             root_node = ExtractContentHelper.get_ancestor_in_body(paragraph)

#             ExtractContentHelper.process_marker(root_node.clone(True), nodes, marker_node, root_node,
#                 marker_node == paragraph, False, True, True)

#     @staticmethod
#     def get_ancestor_in_body(start_node: aw.Node):

#         while start_node.parent_node.node_type != aw.NodeType.BODY:
#             start_node = start_node.parent_node
#         return start_node

# # class ExtractContentHelper:

# #     @staticmethod
# #     def extract_content(start_node: aw.Node, end_node: aw.Node, is_inclusive: bool):

# #         # First, check that the nodes passed to this method are valid for use.
# #         ExtractContentHelper.verify_parameter_nodes(start_node, end_node)

# #         # Create a list to store the extracted nodes.
# #         nodes = []

# #         # If either marker is part of a comment, including the comment itself, we need to move the pointer
# #         # forward to the Comment Node found after the CommentRangeEnd node.
# #         if end_node.node_type == aw.NodeType.COMMENT_RANGE_END and is_inclusive:
# #             node = ExtractContentHelper.find_next_node(aw.NodeType.COMMENT, end_node.next_sibling)
# #             if node is not None:
# #                 end_node = node

# #         # Keep a record of the original nodes passed to this method to split marker nodes if needed.
# #         original_start_node = start_node
# #         original_end_node = end_node

# #         # Extract content based on block-level nodes (paragraphs and tables). Traverse through parent nodes to find them.
# #         # We will split the first and last nodes' content, depending if the marker nodes are inline.
# #         start_node = ExtractContentHelper.get_ancestor_in_body(start_node)
# #         end_node = ExtractContentHelper.get_ancestor_in_body(end_node)

# #         is_extracting = True
# #         is_starting_node = True
# #         # The current node we are extracting from the document.
# #         curr_node = start_node

# #         # Begin extracting content. Process all block-level nodes and specifically split the first
# #         # and last nodes when needed, so paragraph formatting is retained.
# #         # Method is a little more complicated than a regular extractor as we need to factor
# #         # in extracting using inline nodes, fields, bookmarks, etc. to make it useful.
# #         while is_extracting:

# #             # Clone the current node and its children to obtain a copy.
# #             clone_node = curr_node.clone(True)
# #             is_ending_node = curr_node == end_node

# #             if is_starting_node or is_ending_node:

# #                 # We need to process each marker separately, so pass it off to a separate method instead.
# #                 # End should be processed at first to keep node indexes.
# #                 if is_ending_node:
# #                     # !isStartingNode: don't add the node twice if the markers are the same node.
# #                     ExtractContentHelper.process_marker(clone_node, nodes, original_end_node, curr_node, is_inclusive,
# #                                                          False, not is_starting_node, False)
# #                     is_extracting = False

# #                 # Conditional needs to be separate as the block level start and end markers, maybe the same node.
# #                 if is_starting_node:
# #                     ExtractContentHelper.process_marker(clone_node, nodes, original_start_node, curr_node, is_inclusive,
# #                                                          True, True, False)
# #                     is_starting_node = False
# #             else:
# #                 # Node is not a start or end marker, simply add the copy to the list.
# #                 nodes.append(clone_node)

# #             # Move to the next node and extract it. If the next node is None,
# #             # the rest of the content is found in a different section.
# #             if curr_node.next_sibling is None and is_extracting:
# #                 # Move to the next section.
# #                 next_section = curr_node.get_ancestor(aw.NodeType.SECTION).next_sibling.as_section()
# #                 curr_node = next_section.body.first_child
# #             else:
# #                 # Move to the next node in the body.
# #                 curr_node = curr_node.next_sibling

# #         # For compatibility with mode with inline bookmarks, add the next paragraph (empty).
# #         if is_inclusive and original_end_node == end_node and not original_end_node.is_composite:
# #             ExtractContentHelper.include_next_paragraph(end_node, nodes)

# #         # Return the nodes between the node markers.
# #         return nodes

# #     @staticmethod
# #     def generate_document(src_doc: aw.Document, nodes):

# #         dst_doc = src_doc.clone(False).as_document()

# #         # Import each node from the list into the new document. Keep the original formatting of the node.
# #         importer = aw.NodeImporter(src_doc, dst_doc, aw.ImportFormatMode.USE_DESTINATION_STYLES)

# #         # Put the section from the source document to retain original section page setup.
# #         dst_doc.append_child(importer.import_node(src_doc.last_section, True))

# #         # Remove all children from the imported section.
# #         dst_doc.first_section.body.remove_all_children()

# #         for node in nodes:
# #             import_node = importer.import_node(node, True)
# #             dst_doc.first_section.body.append_child(import_node)

# #         return dst_doc

# #     @staticmethod
# #     def verify_parameter_nodes(start_node: aw.Node, end_node: aw.Node):

# #         # The order in which these checks are done is important.
# #         if start_node is None:
# #             raise ValueError("Start node cannot be None")
# #         if end_node is None:
# #             raise ValueError("End node cannot be None")

# #         if start_node.document != end_node.document:
# #             raise ValueError("Start node and end node must belong to the same document")

# #         if start_node.get_ancestor(aw.NodeType.BODY) is None or end_node.get_ancestor(aw.NodeType.BODY) is None:
# #             raise ValueError("Start node and end node must be a child or descendant of a body")

# #         # Check the end node is after the start node in the DOM tree.
# #         # First, check if they are in different sections, then if they're not,
# #         # check their position in the body of the same section.
# #         start_section = start_node.get_ancestor(aw.NodeType.SECTION).as_section()
# #         end_section = end_node.get_ancestor(aw.NodeType.SECTION).as_section()

# #         start_index = start_section.parent_node.index_of(start_section)
# #         end_index = end_section.parent_node.index_of(end_section)

# #         if start_index == end_index:

# #             if (start_section.body.index_of(ExtractContentHelper.get_ancestor_in_body(start_node)) >
# #                     end_section.body.index_of(ExtractContentHelper.get_ancestor_in_body(end_node))):
# #                 raise ValueError("The end node must be after the start node in the body")

# #         elif start_index > end_index:
# #             raise ValueError("The section of end node must be after the section start node")

# #     @staticmethod
# #     def find_next_node(node_type: aw.NodeType, from_node: aw.Node):

# #         if from_node is None or from_node.node_type == node_type:
# #             return from_node

# #         if from_node.is_composite:

# #             node = ExtractContentHelper.find_next_node(node_type, from_node.as_composite_node().get_child_nodes().get(aw.NodeType==node_type))  # Corrected the access to child nodes
# #             if node is not None:
# #                 return node

# #         return ExtractContentHelper.find_next_node(node_type, from_node.next_sibling)

# #     @staticmethod
# #     def process_marker(clone_node: aw.Node, nodes, node: aw.Node, block_level_ancestor: aw.Node,
# #                     is_inclusive: bool, is_start_marker: bool, can_add: bool, force_add: bool):

# #         # If we are dealing with a block-level node, see if it should be included and add it to the list.
# #         if node == block_level_ancestor:
# #             if can_add and is_inclusive:
# #                 nodes.append(clone_node)
# #             return

# #         # cloneNode is a clone of blockLevelNode. If node != blockLevelNode, blockLevelAncestor
# #         # is the node's ancestor that means it is a composite node.
# #         assert clone_node.is_composite

# #         # If a marker is a FieldStart node check if it's to be included or not.
# #         # We assume for simplicity that the FieldStart and FieldEnd appear in the same paragraph.
# #         if node.node_type == aw.NodeType.FIELD_START:
# #             # If the marker is a start node and is not included, skip to the end of the field.
# #             # If the marker is an end node and is to be included, then move to the end field so the field will not be removed.
# #             if (is_start_marker and not is_inclusive) or (not is_start_marker and is_inclusive):
# #                 while node.next_sibling is not None and node.node_type != aw.NodeType.FIELD_END:
# #                     node = node.next_sibling

# #         # Support a case if the marker node is on the third level of the document body or lower.
# #         node_branch = ExtractContentHelper.fill_self_and_parents(node, block_level_ancestor)

# #         # Process the corresponding node in our cloned node by index.
# #         current_clone_node = clone_node
# #         for i in range(len(node_branch) - 1, -1, -1):

# #             current_node = node_branch[i]
# #             node_index = current_node.parent_node.index_of(current_node)

# #             current_clone_node = current_clone_node.as_composite_node().get_child_nodes(node_type=current_node.node_type,is_deep=False)[node_index]

# #             ExtractContentHelper.remove_nodes_outside_of_range(current_clone_node, is_inclusive or (i > 0), is_start_marker)

# #         # After processing, the composite node may become empty if it doesn't include it.
# #         if can_add and (force_add or clone_node.as_composite_node().has_child_nodes):
# #             nodes.append(clone_node)



# #     @staticmethod
# #     # Inside remove_nodes_outside_of_range method
# #     def remove_nodes_outside_of_range(marker_node: aw.Node, is_inclusive: bool, is_start_marker: bool):
# #         if marker_node is None or marker_node.parent_node is None:
# #             return

# #         is_processing = True
# #         is_removing = is_start_marker
# #         current_node = marker_node.parent_node.first_child

# #         while is_processing and current_node is not None:
# #             next_node = current_node.next_sibling
# #             is_skip = False

# #             if current_node == marker_node:
# #                 if is_start_marker:
# #                     is_processing = False
# #                     if is_inclusive:
# #                         is_removing = False
# #                 else:
# #                     is_removing = True
# #                     if is_inclusive:
# #                         is_skip = True

# #             if is_removing and not is_skip:
# #                 current_node.remove()

# #             current_node = next_node


# #     @staticmethod
# #     def fill_self_and_parents(node: aw.Node, till_node: aw.Node):

# #         nodes = []
# #         current_node = node

# #         while current_node != till_node:
# #             nodes.append(current_node)
# #             current_node = current_node.parent_node

# #         return nodes

# #     @staticmethod
# #     def include_next_paragraph(node: aw.Node, nodes):

# #         paragraph = ExtractContentHelper.find_next_node(aw.NodeType.PARAGRAPH, node.next_sibling).as_paragraph()
# #         if paragraph is not None:

# #             # Move to the first child to include paragraphs without content.
# #             marker_node = paragraph.first_child if paragraph.has_child_nodes else paragraph
# #             root_node = ExtractContentHelper.get_ancestor_in_body(paragraph)

# #             ExtractContentHelper.process_marker(root_node.clone(True), nodes, marker_node, root_node,
# #                                                  marker_node == paragraph, False, True, True)

# #     @staticmethod
# #     def get_ancestor_in_body(start_node: aw.Node):

# #         while start_node.parent_node.node_type != aw.NodeType.BODY:
# #             start_node = start_node.parent_node
# #         return start_node

# # lic = aw.License()
# # lic.set_license("X:/awnet/TestData/Licenses/Aspose.Words.Python.NET.lic")
# # build a map of comment id to comment range start.
# starts = {}
# for s in doc.get_child_nodes(aw.NodeType.COMMENT_RANGE_START, True):
#     range_start = s.as_comment_range_start()
#     starts[range_start.id] = range_start


# # build a map of comment id to comment range end.
# ends = {}
# for e in doc.get_child_nodes(aw.NodeType.COMMENT_RANGE_END, True):
#     range_end = e.as_comment_range_end()
#     ends[range_end.id] = range_end

# word_comments = []
# reffered_comments = []
# # loop through the comments in the document
# for c in doc.get_child_nodes(aw.NodeType.COMMENT, True):
#     comment = c.as_comment()
    

#     comment_start = starts[comment.id]
#     comment_end = ends[comment.id]
#     # Firstly, extract the content between these nodes
#     extracted_nodes_exclusive = ExtractContentHelper.extract_content(comment_start, comment_end, False)
#     dst_doc = ExtractContentHelper.generate_document(doc, extracted_nodes_exclusive)
#     print(comment.to_string(aw.SaveFormat.TEXT))
#     print()
#     print(dst_doc.to_string(aw.SaveFormat.TEXT).strip())

#     # print comment and commented text
#     # print("Comment: '" + comment.to_string(aw.SaveFormat.TEXT).strip() + "'")
#     # print("Commented text: '" + dst_doc.to_string(aw.SaveFormat.TEXT).strip() + "'")
#     # print(comment.to_string(aw.SaveFormat.TEXT).strip())
#     # print(dst_doc.to_string(aw.SaveFormat.TEXT).strip() )

# # print(word_comments)
# # print(reffered_comments[0].split('\n'))




# #     for comment in root.findall(".//w:comment", namespaces=nsmap):
# #         comment_id = comment.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')

# #         comment_text = ""
# #         # for s in word_doc.get_child_nodes(aw.NodeType.COMMENT_RANGE_START, True):
# #         #     range_start = s.as_comment_range_start()

# #         # for e in word_doc.get_child_nodes(aw.NodeType.COMMENT_RANGE_END, True):
# #         #     range_end = e.as_comment_range_end()

# #         for p in comment.findall(".//w:p", namespaces=nsmap):
# #             for r in p.findall(".//w:r", namespaces=nsmap):
# #                 text = "".join([t.text for t in r.findall(".//w:t", namespaces=nsmap) if t.text])
# #                 comment_text += text.strip()
# #         comments.append((comment_id, comment_text.strip()))

# # # After collecting all comments, process them with their respective start and end nodes
#         # for comment_id,  range_start, range_end, comment_text in comments:
#         #     if range_start and range_end:
#         #         extracted_nodes_exclusive = ExtractContentHelper.extract_content(range_start, range_end, False)
#         #         dst_doc = ExtractContentHelper.generate_document(word_doc, extracted_nodes_exclusive)
#         #         print((comment_id, comment_text), dst_doc.to_string(aw.SaveFormat.TEXT).strip(),'\n')

