from app.utils import helper_functions
from app.utils.constants import *
from app.models import Context, Dimension
from typing import *

class Cell:
    """ Class for an individual tagged cell (ix) """

    def __init__(self, id : str, value, xbrl_tag : str, row_name : str, col_name : str, context : Context, n_left_cols : int = 2):
        """ initialization function for the class """
        self._id = id # id for the tab and cell, ex. StatementofNetPosition_D5
        self._xbrl_tag = xbrl_tag
        self._row_name = row_name
        self._context = context
        self._value = helper_functions.format_value(value)
        self._n_left_cols = n_left_cols
        self._first_row = False
        # adjust dimensions based on line item if relevant
        #self.handle_custom_line_item()

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
        
    @property
    def id(self):
        return self._id
    
    def col(self):
        """ original excel column (ex. D) """
        return self._id[self._id.find('_') + 1]
    
    def row(self):
        """ original excel row number """
        return int(self._id[self._id.find('_') + 2:])

    def row_name(self) -> str:
        if self._row_name == "nan":
            return ""
        return self._row_name
    
    def col_name(self) -> str:
        return self._context.col_name

    def xbrl_tag(self):
        return self._xbrl_tag

    def context_ref(self):
        # if self._context is None:
        #     return "ERROR"
        return self._context.id
    
    def in_first_col(self):
        """ is the cell in the first column? """
        return self._id[self._id.find('_') + 1] == ALPHABET[self._n_left_cols]

    def show_value(self):
        if self._value == "" or isinstance(self._value, str):
            return self._value
        try:
            ret = '{:,}'.format(abs(int(round(float(self._value)))))
            return "-" if ret == "0" else ret
        except ValueError:
            print(f"Warning: Unable to format value: {self._value}")
            return str(self._value)
    
    def first_row(self):
        return self._first_row
    
    def set_first_row(self):
        self._first_row = True
    
    def prefix(self):
        """
        Add dollar sign and/or opening parenthesis as relevant
        """
        ret = ""
        if self._first_row:
            ret = "$ "
        if isinstance(self._value, (int, float)) and self._value < 0:
            ret += "("
        return ret
    
    def suffix(self):
        """Add closing parenthesis if relevant"""
        ret = ")" if isinstance(self._value, (int, float)) and self._value < 0 else ""
        return ret
    
    def tr_class(self):
        """
        Define row type to determine formatting
        """
        if self._row_name in ["", "nan"]:
            return "empty_row"
        if self._row_name.isupper() and self._row_name.strip() not in EXCLUDED_HEADERS:
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
    
    def formatted_value(self):
        """
        Combine prefix, value, and suffix for complete formatted representation
        """
        return f"{self.prefix()}{self.show_value()}{self.suffix()}"

    def __repr__(self):
        return self.show_value()

    def index(self):
        """ ex. 5B for a cell originall in B5 in Excel """
        return self.row() + self.col()

    def __lt__(self, other):
        """ less than if earlier in original Excel """
        if self.row() == other.row():
            return self.col() < other.col()
        return self.row() < other.row()
    
    def __eq__(self, other):
        return self.index() == other.index()

    def needs_ix_tag(self):
        return self.show_value() != "" and self._context != None
    
    def handle_custom_line_item(self):
        if self._xbrl_tag and "custom" in self._xbrl_tag.lower():
            self._context.add_dim(Dimension(self._row_name, "custom"))
