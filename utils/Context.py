class Context:
    """ define xbrl context object """
    def __init__(self, id, date, place_id, dimension_member):
        self.id = id
        self.date = str(date).replace("-", "")
        self.time_type = "I" # replace with lookup table
        self.place_id = place_id # replace with a lookup function from Census
        # TODO figure out how to determine these programatically
        self.dimension_member = dimension_member # ie. acfr:GovernmentalActivitiesMember
        self.axis = "acfr:TypeOfGovernmentUnitAxis"