# load in a file from URL save a local csv file with the first 10 rows
# 

import time

import pandas as pd
import numpy as np
import pyarrow


def load_csv(filepath):
    print(f"Loading data from {filepath}...")
    start_time = time.time()
    try:
        df = pd.read_csv(filepath, engine='python')
        end_time = time.time()
        load_time = end_time - start_time
        print(f"CSV file loaded in {load_time:.2f} seconds.")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")

        required_columns = ['quantity', 'unit_price', 'order_date']
        # chck if the required columns are present in the dataframe
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns in the CSV file: {', '.join(missing_columns)}")
        else:
            print("All required columns are present in the CSV file.")
        return df
    
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

# call load_csv to load data and print the first 10 rows
filename = "https://drive.google.com/uc?export=download&id=1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA"
sales_data = load_csv(filename)

print(sales_data.head(10))