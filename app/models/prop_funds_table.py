from app.models import NetPosition

class PropFunds(NetPosition):
    """ Extends net position class to add an extra header row """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        super().__init__(excel_file, sheet_name, extra_left_cols)