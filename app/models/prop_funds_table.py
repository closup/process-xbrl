from app.models import NetPosition, Dimension

class PropFunds(NetPosition):
    """ Extends net position class to add an extra header row """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        super().__init__(excel_file, sheet_name, extra_left_cols)

    @staticmethod
    def create_dim_list(col_name, fund_type = "prop"):
        return [Dimension(col_name, fund_type)]
    
    def n_header_lines(self) -> int:
        # determine number of lines above the first taggable row
        # TODO: fix this hard-coding
        return self._df[self._df.columns[-1]].first_valid_index() + 1