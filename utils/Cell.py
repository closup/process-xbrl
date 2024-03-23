
from utils.helper_functions import *
from utils.constants import *

class Cell:
    """ Class for an individual tagged cell (ix) """

    def __init__(self, id : str, value, xbrl_tag : str, row_name : str, col_name : str, date_id : str, n_left_cols : int = 2):
        """ initialization function for the class """
        self._id = id # id for the tab and cell, ex. StatementofNetPosition_D5
        self._xbrl_tag = xbrl_tag
        self._row_name, self._col_name = row_name, col_name
        self._context_ref = date_id + "_" + get_col_no_spaces(col_name)
        self._value = value
        self._n_left_cols = n_left_cols
        self._first_row = False

    def sign(self):
        """ get sign of value (ie. negative or positive) """
        if not (type(self._value) is str) and self._value < 0:
            return "negative"
        return ""
    
    def format(self):
        """ ixbrl format for the dollar value in the cell"""
        if self._value == 0:
            return 'ixt:fixed-zero' 
        return 'ixt:num-dot-decimal'
        
    def id(self):
        return self._id

    def row_name(self) -> str:
        return self._row_name
    
    def col_name(self) -> str:
        return self._col_name

    def xbrl_tag(self):
        return self._xbrl_tag

    def context_ref(self):
        return self._context_ref
    
    def in_first_col(self):
        """ is the cell in the first column? """
        return self._id[self._id.find('_') + 1] == ALPHABET[self._n_left_cols]

    def show_value(self):
        """
        Format the value as it should appear in the html table
        (ie. add a $ if the first row; add commas, etc)
        """
        if self._value == "" or type(self._value) is str:
            return self._value
        ret = '{:,}'.format(abs(self._value))
        if ret == "0":
            ret = "-"
        return ret
    
    def first_row(self):
        return self._first_row
    
    def set_first_row(self):
        self._first_row = True
    
    def prefix(self):
        """
        Add dollar sign and/or negative sign as relevant
        """
        ret = ""
        if self._value < 0:
            ret = "-" + ret
        if self._first_row:
            ret = "$ " + ret
        return ret
    
    def tr_class(self):
        """
        Define row type to determine formatting
        """
        if self._row_name == "":
            return "empty_row"
        if self._row_name.isupper():
            return "section_header"
        if self._row_name[-1] == ":":
            return "subsection_header"
        if "total" in self._row_name.lower():
            return "total"
        return "row" 
    
    def td_class(self):
        """ Return CSS class for individual table cell """
        if "total" in self._row_name.lower():
            return "data_total"
        return self.tr_class()
    
    def __repr__(self):
        return self.show_value()