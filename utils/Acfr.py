from utils.Sheet import Sheet

class Acfr:
    """ Object to an entire acfr """

    def __init__(self, sheets):
        self.sheets = sheets
        nested_contexts = [sheet.contexts for sheet in self.sheets]
        self.contexts = set(context for context_list in nested_contexts for context in context_list)
