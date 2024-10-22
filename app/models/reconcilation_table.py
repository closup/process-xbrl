from app.models import Table, Cell, Context, Dimension
from app.utils import *
import pandas as pd

class Reconciliation(Table):
    """ Extends net position class to add an extra header row """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 1):
        super().__init__(excel_file, sheet_name, extra_left_cols)
        self._data = []
        self._contexts = []
        self.process_cells()
        self.mark_first_numeric_row()

    def process_cells(self):
        """Create a list of Cell objects to represent Excel data"""
        context = Context(self.time_type, self.date, "Amount", [Dimension("Amount")])
        self._contexts.append(context)

        for _, row in self._df.iterrows():
            xbrl_tag = row.get("XBRL Element", "")  # Assuming "XBRL Element" column exists
            if pd.notna(row["value"]):  # Process all non-NaN values
                cell = Cell(id = row["id"], 
                            xbrl_tag = xbrl_tag, 
                            row_name = str(row["nan"]), 
                            col_name = str(row["header"]),
                            value = row["value"],
                            context = context,
                            n_left_cols = self.extra_left_cols)
                self._data.append(cell)
    
        if self._data:
            self._data.sort()
            print(f"Debug: Number of cells processed: {len(self._data)}")
            print(f"Debug: First cell: {self._data[0]}")
            print(f"Debug: Last cell: {self._data[-1]}")
        else:
            print("Debug: No cells were processed.")
    
        print(f"Debug: DataFrame shape: {self._df.shape}")
        print(f"Debug: DataFrame columns: {self._df.columns}")
        print(f"Debug: First few rows of DataFrame:\n{self._df.head()}")

    def n_header_lines(self) -> int:
        # determine number of lines above the first taggable row
        # TODO: fix to find first numeric row?
        return 4 #self._df[self._df.columns[-1]].first_valid_index()

    def reshape_data(self) -> None:
        """
        Process Excel sheet data to extract values and cell locations
        """   
        # Assign column names
        self._df.columns = ["nan", "Amount"]

        # Drop unneeded rows (above taggable portion)
        self._df.drop(index = self._df.index[:self.n_header_lines() + 1], inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        
        # Record original row number
        self._df["row"] = 1 + self.n_header_lines() + len(self.header()) + self._df.index  
        n_rows_orig = len(self._df) # num of rows before reshaping

        # Reshape using 'melt' to give one row per taggable item
        id_cols = self._df.columns[:self.extra_left_cols].tolist() + ["row"]
        if "XBRL Element" in self._df.columns:
            id_cols.append("XBRL Element")
        val_cols = [col for col in self._df.columns if col not in id_cols and col != "row"]
        self._df = pd.melt(self._df, id_vars=id_cols, value_vars=val_cols, var_name="header")

        # Ensure 'value' column is numeric and preserves negative values
        self._df['value'] = pd.to_numeric(self._df['value'], errors='coerce')

        # Calculate original sheet column and cell in Excel document
        self._df['col'] = [ALPHABET[min(i, len(ALPHABET)-1)] for i in (self.extra_left_cols + (self._df.index // n_rows_orig))]
        cells = [f'{c}{r}' for c, r in zip(self._df['col'], self._df["row"])]
        self._df["id"] = [f'{self.sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        self._df = self._df.sort_values(by=['row', 'col'])

        print(f"Debug: Final DataFrame shape: {self._df.shape}")
        print(f"Debug: Final DataFrame columns: {self._df.columns}")
        print(f"Debug: First few rows of final DataFrame:\n{self._df.head()}")
