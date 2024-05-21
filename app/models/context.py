from app.utils import *
from datetime import datetime, timedelta # for date parsing
from typing import *
from app.models import Dimension

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
        self._dims = dims
        self.id = self.create_id()
    
    def dims(self) -> List[Dimension]:
        return self._dims
    
    def time_type(self):
        return self._time_type

    def date(self):
        """ format date as needed """
        return self._date.strftime("%Y-%m-%d")
    
    def period_start(self) -> datetime:
        """ start of the fiscal year """
        start = self._date - timedelta(days=364)
        return start.strftime("%Y-%m-%d")
    
    def create_id(self) -> str:
        """ create id which will match context_ref for cells in this context 
        this should be a unique combo of time type, date, and all dimensions"""
        ret = ""
        for dim in self.dims():
            ret = ret + "_" + dim._member_name
        try:
            return self._time_type + self._date.strftime('%Y%m%d') + ret
        finally:
            print(f"Date parse error: {self._date}")
            return self._time_type + "date_parse_error" + ret
        
    
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

    
