# load in a file from URL save a local csv file with the first 10 rows
# 

import pandas as pd
import numpy as np
import pyarrow

filename = "https://drive.google.com/file/d/1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA"

df = pd.read_csv(filename, engine='pyarrow')

out_file = "sales_data_test.csv"
df.head(10).to_csv(out_file, index=False)
