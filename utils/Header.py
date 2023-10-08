
############
# SUPERCEDED
############


from utils.helper_functions import print_nicely

class Header:
    """ Excel sheet/ html header for given sheet """
    __slots__ = ['city', 'scope', 'statement', 'date']

    def __init__(self, city, scope, statement, date):
        self.city = city
        self.scope = scope
        self.statement = statement
        self.date = date

    def index(self):
        # index used for the contexts map dictionary
        return f"{self.scope}@{self.statement}"
    
    def __repr__(self):
        ret = ""
        for slot in self.__slots__:
            ret = ret + "<br>" + print_nicely(getattr(self, slot))
        return ret
    
