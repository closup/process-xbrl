from utils.helper_functions import *
from datetime import datetime, timedelta # for date parsing
from utils.constants import *
from typing import *
from utils.Dimension import Dimension

class Context:
    """ define xbrl context object """

    def __init__(self, time_type : str, date : datetime, col_name : str, dims : List[Dimension]):
        """
        Build out context for each entity: government-type activities, business-type, etc 
        """
        self._date = date
        self._time_type = time_type
        self.place_id = self.get_place_id()
        self.col_name = col_name
        self.id = self.create_id()
        self._dims = dims
    
    def dims(self) -> List[Dimension]:
        return self._dims
    
    def time_type(self):
        return self._time_type

    def date(self):
        """ format date as needed """
        return self._date.strftime("%Y-%m-%d")
    
    def period_start(self) -> datetime:
        """ start of the fiscal year """
        return self._date - timedelta(days=364)
    
    def create_id(self) -> str:
        # TODO: update this to be unique to each dimension
        """ create id which will match context_ref for cells in this context """
        return self._time_type + self._date.strftime('%Y%m%d') + "_" + get_col_no_spaces(self.col_name)
    
    def get_place_id(self) -> str:
        # TODO: replace with a lookup function from Census
        return "0613882" 
    
    def __eq__(self, other):
        """ Equality check """
        return(self.id == other.id)

    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return self.id

    