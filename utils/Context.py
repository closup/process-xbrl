from utils.helper_functions import *

# look up period or instance by statement
period_dict = {"statement_of_net_position" : "I",
               "balance_sheet" : "I",
               "statement_of_revenues,_expenditures_and_changes_in_fund_balance" : "D",
               "statement_of_net_position" : "I",
               "statement_of_revenues,_expenses_and_changes_in_net_position" : "D",
               "statement_of_cash_flows" : "D"}

# Explicit members of axes plus their axis name
explicit_axis_members = {"governmental_activities" : "TypeOfGovernmentUnit",
                         "business-type_activities" : "TypeOfGovernmentUnit",
                         "general_fund" : "GovernmentalFunds",
                         "total" : "GovernmentalFunds"}

# Axes with typed members
# ALL FundIdentifier
# typed_axis_members = {"Balance Sheet" : "FundIdentifier",
#                       "Statement of Revenues, Expenditures and Changes in Fund Balance" : "FundIdentifier",
#                       "Statement of Net Position" : }

class Context:
    """ define xbrl context object """
    __slots__ = ["id", "date", "time_type", "place_id", "memberType",
                 "dimension_member", "axis"]

    def __init__(self, context_name_map, statement, date, col_name):
        self.id = context_name_map[col_name]
        self.date = date.replace("-", "")
        self.time_type = period_dict[statement] # replace with lookup table
        self.place_id = "0613882" # replace with a lookup function from Census
        if(col_name in explicit_axis_members):
            self.axis = f"acfr:{explicit_axis_members[col_name]}Axis"
            self.memberType = "explicit"
            self.dimension_member = f'acfr:{print_nicely(col_name).replace(" ", "")}Member'
        else:
            self.axis = "afcr:FundIdentifierAxis"
            self.memberType = "typed"
            self.dimension_member = print_nicely(col_name)
        
    def __eq__(self, other):
        """ Equality check """
        return(hash(self) == hash(other))

    def __hash__(self):
        return hash(self.id)