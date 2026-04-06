import time
import pandas as pd
import numpy as np
import pyarrow

# columns the analytics need - used to warn the user if any are missing
REQUIRED_COLUMNS = [
    "sales_region", "order_type", "customer_state", "customer_type",
    "product_category", "quantity", "unit_price", "employee_name"
]

# options available in the custom pivot builder
PIVOT_ROW_OPTIONS    = ["employee_name", "sales_region", "product_category", "customer_state", "customer_type"]
PIVOT_COLUMN_OPTIONS = ["order_type", "customer_type", "sales_region"]
PIVOT_VALUE_OPTIONS  = ["quantity", "unit_price"]
PIVOT_AGG_OPTIONS    = ["sum", "mean", "count"]

# stores every pivot table created this session so the user can review them
results_store = {}


# load the sales data from a URL or local filepath
# returns None if the file is missing or unreadable so the main program can stop
def load_data(filepath):
    print(f"\nLoading data from {filepath}...")
    start_time = time.time()

    try:
        df = pd.read_csv(filepath, engine='python')
        end_time = time.time()
        load_time = end_time - start_time
        print(f"CSV file loaded in {load_time:.2f} seconds.")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")

        # replace any missing values with 0 so pivot tables don't break
        df.fillna(0, inplace=True)

        # warn the user if any columns the analytics depend on are missing
        missing = []
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                missing.append(col)
        if missing:
            print(f"Warning: These required columns are missing - some analytics may not work:")
            print(f"  {', '.join(missing)}")
        else:
            print("All required columns are present.")

        return df

    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None


# check that all needed columns exist before running an analytic
# returns True if all present, False if any are missing
def check_columns(df, needed):
    missing = []
    for col in needed:
        if col not in df.columns:
            missing.append(col)
    if missing:
        print(f"\nCannot run this analytic - missing column(s): {', '.join(missing)}")
        return False
    return True


# print a pivot table with a title
def show_table(df, title):
    print()
    print("-" * 60)
    print(title)
    print("-" * 60)
    print(df.to_string())
    print()


# ask if the user wants to export a result to Excel, and save it if so
# also stores the result in results_store for the session
def ask_export(label, df):
    results_store[label] = df

    choice = input("Export to Excel? (y/n): ").strip().lower()
    if choice == "y":
        filename = input("Enter filename (without .xlsx): ").strip()
        if filename == "":
            filename = "export"
        filepath = filename + ".xlsx"
        try:
            df.to_excel(filepath)
            print(f"Saved to {filepath}")
        except Exception as e:
            print(f"Could not save: {e}")


# ask the user to pick from a numbered list, returns the selected items
# if allow_empty is True, pressing Enter returns an empty list (used for optional fields)
def pick_from_list(prompt, options, allow_empty=False):
    for i in range(len(options)):
        print(f"  {i + 1}. {options[i]}")

    while True:
        raw = input(prompt).strip()

        if raw == "" and allow_empty:
            return []

        # split by comma and convert each part to a 0-based index
        parts = raw.split(",")
        indices = []
        valid = True
        for part in parts:
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(options):
                    indices.append(idx)
                else:
                    valid = False
                    break
            else:
                valid = False
                break

        if valid and len(indices) > 0:
            return indices

        print(f"Please enter number(s) from 1 to {len(options)}, separated by commas.")


# menu functions 
# each function takes the dataframe as its only argument
# this keeps them consistent so they can all be stored in the menu tuple

# show the first n rows of the data
def show_first_n_rows(df):
    total = len(df)
    print()
    print("Enter rows to display:")
    print(f"  - Enter a number 1 to {total}")
    print("  - To see all rows, enter 'all'")
    print("  - To skip preview, press Enter")

    # keep asking until the user enters something valid
    while True:
        raw = input("Your choice: ").strip().lower()

        if raw == "":
            print("(Skipped)")
            return
        elif raw == "all":
            n = total
            break
        elif raw.isdigit() and 1 <= int(raw) <= total:
            n = int(raw)
            break
        else:
            print(f"Invalid input. Please enter a number between 1 and {total}, 'all', or press Enter.")

    result = df.head(n)
    show_table(result, f"First {n} rows")
    ask_export(f"First {n} rows", result)


# total sale_price grouped by region and order type
def total_sales_by_region_order_type(df):
    if not check_columns(df, ["sales_region", "order_type", "unit_price"]):
        return

    pt = pd.pivot_table(df, values="unit_price", index="sales_region",
                        columns="order_type", aggfunc="sum", fill_value=0,
                        margins=True, margins_name="Total")
    show_table(pt, "Total Sales by Region and Order Type")
    ask_export("Total Sales by Region and Order Type", pt)


# average sale_price by region broken down by state and sale type
def avg_sales_by_region_state_sale_type(df):
    if not check_columns(df, ["sales_region", "customer_state", "order_type", "unit_price"]):
        return

    pt = pd.pivot_table(df, values="unit_price", index=["sales_region", "customer_state"],
                        columns="order_type", aggfunc="mean", fill_value=0)
    show_table(pt, "Average Sales by Region / State / Sale Type")
    ask_export("Average Sales by Region / State / Sale Type", pt)


# total sale_price by customer type and order type, shown by state
def sales_by_customer_order_by_state(df):
    if not check_columns(df, ["customer_type", "order_type", "customer_state", "unit_price"]):
        return

    pt = pd.pivot_table(df, values="unit_price", index=["customer_type", "order_type"],
                        columns="customer_state", aggfunc="sum", fill_value=0)
    show_table(pt, "Sales by Customer Type and Order Type (by State)")
    ask_export("Sales by Customer Type and Order Type (by State)", pt)


# total quantity and sale_price by region and product
def total_qty_price_by_region_product(df):
    if not check_columns(df, ["sales_region", "product_category", "quantity", "unit_price"]):
        return

    pt = pd.pivot_table(df, values=["quantity", "unit_price"],
                        index=["sales_region", "product_category"],
                        aggfunc="sum", fill_value=0,
                        margins=True, margins_name="Total")
    show_table(pt, "Total Quantity and Sale Price by Region and Product")
    ask_export("Total Quantity and Sale Price by Region and Product", pt)


# total quantity and sale_price by order type and customer type
def total_qty_price_by_customer_type(df):
    if not check_columns(df, ["order_type", "customer_type", "quantity", "unit_price"]):
        return

    pt = pd.pivot_table(df, values=["quantity", "unit_price"],
                        index=["order_type", "customer_type"],
                        aggfunc="sum", fill_value=0,
                        margins=True, margins_name="Total")
    show_table(pt, "Total Quantity and Sale Price by Customer Type")
    ask_export("Total Quantity and Sale Price by Customer Type", pt)


# max and min sale_price for each product category
def max_min_price_by_category(df):
    if not check_columns(df, ["product_category", "unit_price"]):
        return

    pt = pd.pivot_table(df, values="unit_price", index="product_category",
                        aggfunc=["max", "min"], fill_value=0)
    show_table(pt, "Max and Min Sale Price by Category")
    ask_export("Max and Min Sale Price by Category", pt)


# count of unique employees in each region
def unique_employees_by_region(df):
    if not check_columns(df, ["sales_region", "employee_name"]):
        return

    pt = pd.pivot_table(df, values="employee_name", index="sales_region",
                        aggfunc=pd.Series.nunique, fill_value=0)
    pt.columns = ["Unique Employees"]
    show_table(pt, "Number of Unique Employees by Region")
    ask_export("Unique Employees by Region", pt)


# let the user build their own pivot table by choosing rows, columns, values, and aggregation
def create_custom_pivot(df):
    print("\nCustom Pivot Table Builder")

    # only offer columns that actually exist in the dataframe
    row_opts = []
    for col in PIVOT_ROW_OPTIONS:
        if col in df.columns:
            row_opts.append(col)

    col_opts = []
    for col in PIVOT_COLUMN_OPTIONS:
        if col in df.columns:
            col_opts.append(col)

    val_opts = []
    for col in PIVOT_VALUE_OPTIONS:
        if col in df.columns:
            val_opts.append(col)

    if len(row_opts) == 0 or len(val_opts) == 0:
        print("Not enough columns in this dataset to build a custom pivot.")
        return

    print("\nSelect rows:")
    row_indices = pick_from_list("Enter number(s) separated by commas: ", row_opts)
    selected_rows = []
    for i in row_indices:
        selected_rows.append(row_opts[i])

    print("\nSelect columns (optional - press Enter to skip):")
    col_indices = pick_from_list("Enter number(s) separated by commas: ", col_opts, allow_empty=True)
    selected_cols = None
    if len(col_indices) > 0:
        selected_cols = []
        for i in col_indices:
            selected_cols.append(col_opts[i])

    print("\nSelect values:")
    val_indices = pick_from_list("Enter number(s) separated by commas: ", val_opts)
    selected_vals = []
    for i in val_indices:
        selected_vals.append(val_opts[i])

    print("\nSelect aggregation function:")
    agg_index = pick_from_list("Enter a number: ", PIVOT_AGG_OPTIONS)
    selected_agg = PIVOT_AGG_OPTIONS[agg_index[0]]

    try:
        pt = pd.pivot_table(df, values=selected_vals, index=selected_rows,
                            columns=selected_cols, aggfunc=selected_agg, fill_value=0)
    except Exception as e:
        print(f"Could not build pivot table: {e}")
        return

    label = "Custom: " + selected_agg + "(" + ", ".join(selected_vals) + ") by " + ", ".join(selected_rows)
    if selected_cols:
        label = label + " x " + ", ".join(selected_cols)

    show_table(pt, label)
    ask_export(label, pt)


# display all pivot tables created this session
def show_all_results(df):
    if len(results_store) == 0:
        print("\nNo results stored yet. Run some analytics first.")
        return

    print(f"\nStored results this session ({len(results_store)} total):")
    for label in results_store:
        show_table(results_store[label], label)

    # option to export everything to one Excel workbook with one sheet per result
    choice = input("Export all results to one Excel workbook? (y/n): ").strip().lower()
    if choice == "y":
        filename = input("Enter filename (without .xlsx): ").strip()
        if filename == "":
            filename = "all_results"
        filepath = filename + ".xlsx"
        try:
            writer = pd.ExcelWriter(filepath)
            sheet_num = 1
            for label in results_store:
                sheet_name = "Result_" + str(sheet_num)
                results_store[label].to_excel(writer, sheet_name=sheet_name)
                sheet_num = sheet_num + 1
            writer.close()
            print(f"Saved to {filepath}")
        except Exception as e:
            print(f"Could not save: {e}")


# menu setup 
# each item is (label shown in menu, function to call)
# to add, remove, or reorder items just edit this tuple - nothing else needs to change

MENU_ITEMS = (
    ("Show the first n rows of sales data",                       show_first_n_rows),
    ("Total sales by region and order_type",                      total_sales_by_region_order_type),
    ("Average sales by region with average by state and sale type", avg_sales_by_region_state_sale_type),
    ("Sales by customer type and order type by state",            sales_by_customer_order_by_state),
    ("Total sales quantity and price by region and product",      total_qty_price_by_region_product),
    ("Total sales quantity and price by customer type",           total_qty_price_by_customer_type),
    ("Max and min sales price by category",                       max_min_price_by_category),
    ("Number of unique employees by region",                      unique_employees_by_region),
    ("Create a custom pivot table",                               create_custom_pivot),
    ("Show all stored results",                                   show_all_results),
)


# print the menu with a list of results stored so far this session
def show_menu():
    print()
    print("--- Sales Data Dashboard ---")

    if len(results_store) > 0:
        print(f"Results stored this session ({len(results_store)}):")
        for label in results_store:
            print(f"  - {label}")
        print()

    for i in range(len(MENU_ITEMS)):
        print(str(i + 1) + ". " + MENU_ITEMS[i][0])
    print(str(len(MENU_ITEMS) + 1) + ". Exit")


if __name__ == "__main__":
    # main program 

    print("Welcome to the Sales Data Dashboard!")
    print()

    # load the data - if it fails, load_data prints the error and returns None
    df = load_data("https://drive.google.com/uc?export=download&id=1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA")

    if df is None:
        print("Exiting.")
    else:
        # keep showing the menu until the user chooses Exit
        running = True
        while running:
            show_menu()
            choice = input("\nEnter your choice: ").strip()

            exit_number = len(MENU_ITEMS) + 1

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice = int(choice)

            if choice == exit_number:
                print("\nGoodbye!")
                running = False
            elif 1 <= choice <= len(MENU_ITEMS):
                # call the function for the chosen menu item, passing in the dataframe
                MENU_ITEMS[choice - 1][1](df)
            else:
                print(f"Please enter a number from 1 to {exit_number}.")