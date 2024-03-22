
from utils.helper_functions import *
from utils.constants import *

class Cell:
    """ Class for an individual tagged cell (ix) """

    def __init__(self, id : str, value, xbrl_tag : str, row_name : str, col_name : str, time_id : str, n_left_cols : int = 2):
        """ initialization function for the class """
        self.id = id # id for the tab and cell, ex. StatementofNetPosition_D5
        self.xbrl_tag = xbrl_tag
        self.row_name, self.col_name = row_name, col_name
        self.context_ref = time_id + "_" + get_col_no_spaces(col_name)
        self.value = value

    def sign(self):
        """ get sign of value (ie. negative or positive) """
        if not (type(self.value) is str) and self.value < 0:
            return "negative"
        return ""
    
    def format(self):
        """ ixbrl format for the dollar value in the cell"""
        if self.value == 0:
            return 'ixt:fixed-zero' 
        return 'ixt:num-dot-decimal'
        
    @property
    def id(self):
        return self.id
    
    @property
    def row_name(self):
        return self.row_name
    
    @property
    def format(self):
        return self.format
    
    @property
    def xbrl_tag(self):
        return self.xbrl_tag
    
    @property
    def context_ref(self):
        return self.context_ref
    
    def in_first_col(self):
        """ is the cell in the first column? """
        return self.id[self.id.find('_') + 1] == ALPHABET[self.n_left_cols]

    def show_value(self):
        """
        Format the value as it should appear in the html table
        (ie. add a $ if the first row; add commas, etc)
        """
        if self.value == "":
            return ""
        ret = '{:,}'.format(abs(self.value))
        if ret == "0":
            ret = "-"
        return ret
    
    def prefix(self):
        """
        Add dollar sign and/or negative sign as relevant
        """
        ret = ""
        if self.value < 0:
            ret = "-" + ret
        if self.first_row:
            ret = "$ " + ret
        return ret
    
    def tr_class(self):
        """
        Define row type to determine formatting
        """
        if self.name == "":
            return "empty_row"
        if self.name.isupper():
            return "section_header"
        if self.name[-1] == ":":
            return "subsection_header"
        if "total" in self.name.lower():
            return "total"
        return "row" 
    
    def td_class(self):
        """ Return CSS class for individual table cell """
        if "total" in self.name.lower():
            return "data_total"
        return self.tr_class()
    
    def __repr__(self):
        return self.show_value()