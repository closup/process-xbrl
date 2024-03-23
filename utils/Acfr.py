
class Acfr:
    """ 
    Class to represent an entire acfr 
    sheets are Excel sheets in the file, contexts are ixbrl contexts
    """

    def __init__(self, sheets):
        self._sheets = sheets
        # create a list of all unique contexts across every sheet
        nested_contexts = [sheet.contexts() for sheet in self._sheets]
        self.contexts = set(context for context_list in nested_contexts for context in context_list)

    def sheets(self):
        return self._sheets
