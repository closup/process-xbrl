class Context:
    """ define xbrl context object """
    __slots__ = ["id", "date", "time_type", "place_id", 
                 "dimension_member", "axis"]

    def __init__(self, context_name_map, date, col_name):
        self.id = context_name_map[col_name]
        self.date = date.replace("-", "")
        self.time_type = "I" # replace with lookup table
        self.place_id = "0613882" # replace with a lookup function from Census
        # TODO expand and move this HARDCODING
        dim_dict = {"business-type_activities" :"acfr:BusinessTypeActiviesMember",
                    "governmental_activities" : " acfr:GovernmentalActivitiesMember",
                    "total" : None}
        self.dimension_member = dim_dict[col_name]
        self.axis = "acfr:TypeOfGovernmentUnitAxis"

    def __eq__(self, other):
        """ Equality check """
        return(hash(self) == hash(other))

    def __hash__(self):
        return hash(self.id)