
import os
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (10, 6)

def parse_currency_or_number(x):
    """Convert values like '₹80,000' or '80000' or '50.5' to float, return NaN on failure."""
    try:
        s = str(x)
        # remove anything except digits, dot, minus
        s = re.sub(r'[^\d\.\-]', '', s)
        if s == '' or s == '.' or s == '-':
            return float('nan')
        return float(s)
    except Exception:
        return float('nan')

def ensure_numeric(df, col):
    """Ensure column is numeric; if object dtype -> try parsing; else coerce to numeric."""
    if col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(parse_currency_or_number)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        df[col] = pd.NA
    return df


INPUT_CSV = "sales_data.csv"                 
PROCESSED_CSV = "sales_data_processed.csv"
CATEGORY_SUMMARY_CSV = "category_sales_summary.csv"
FIG_LINE = "total_sales_over_time.png"
FIG_BAR = "sales_by_category.png"
FIG_PIE = "sales_by_product_pie.png"


if not os.path.exists(INPUT_CSV):
    print(f"'{INPUT_CSV}' not found — creating a sample dataset as '{INPUT_CSV}' for testing.")
    sample = pd.DataFrame({
        "Date": ["2024-01-01","2024-01-05","2024-01-10","2024-01-15","2024-01-20","2024-02-05"],
        "Product": ["Laptop","Headphones","Chair","Desk","Mouse","Sofa"],
        "Category": ["Electronics","Electronics","Furniture","Furniture","Electronics","Furniture"],
        "Units_Sold": [10,25,15,8,50,5],
        "Unit_Price": [80000,2000,3500,7500,500,25000],
       
    })
    sample["Total_Sales"] = sample["Units_Sold"] * sample["Unit_Price"]
    sample.to_csv(INPUT_CSV, index=False)
    print(f"Sample file '{INPUT_CSV}' created. You can replace it with your own CSV later.\n")


try:
    
    df = pd.read_csv(INPUT_CSV)
except Exception as e:
    print("Error reading CSV file:", e)
    sys.exit(1)


df.columns = df.columns.str.strip()


if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].isna().all():
        print("Warning: All 'Date' values could not be parsed -> using row index as Date.")
        df['Date'] = pd.to_datetime(df.index)
else:
    print("Warning: No 'Date' column found -> creating a Date column from the row index.")
    df['Date'] = pd.to_datetime(df.index)


df = ensure_numeric(df, 'Units_Sold')
df = ensure_numeric(df, 'Unit_Price')
df = ensure_numeric(df, 'Total_Sales')


if 'Total_Sales' not in df.columns or df['Total_Sales'].isna().sum() > (0.5 * len(df)):
   
    df['Units_Sold'] = df['Units_Sold'].fillna(0)
    df['Unit_Price'] = df['Unit_Price'].fillna(0)
    df['Total_Sales'] = df['Units_Sold'] * df['Unit_Price']


df['Units_Sold'] = df['Units_Sold'].fillna(0)
df['Unit_Price'] = df['Unit_Price'].fillna(0)
df['Total_Sales'] = df['Total_Sales'].fillna(0)


df = df.sort_values('Date').reset_index(drop=True)


print("\n--- Summary statistics for numeric columns ---")
print(df[["Units_Sold", "Unit_Price", "Total_Sales"]].describe().round(2))


try:
    daily_sales = df.groupby('Date', as_index=True)['Total_Sales'].sum()
    plt.figure()
    daily_sales.plot(marker='o')
    plt.title("Total Sales Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Sales")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(FIG_LINE)
    plt.show()
    print(f"Line chart saved to '{FIG_LINE}'")
except Exception as e:
    print("Could not create line chart:", e)


try:
    if 'Category' not in df.columns:
        print("Warning: 'Category' column not found — skipping category bar chart.")
    else:
        category_sales = df.groupby('Category')['Total_Sales'].sum().sort_values(ascending=False)
        plt.figure()
        category_sales.plot(kind='bar')
        plt.title("Total Sales by Category")
        plt.xlabel("Category")
        plt.ylabel("Total Sales")
        plt.tight_layout()
        plt.savefig(FIG_BAR)
        plt.show()
        print(f"Bar chart saved to '{FIG_BAR}'")
except Exception as e:
    print("Could not create bar chart:", e)


try:
    if 'Product' not in df.columns:
        print("Warning: 'Product' column not found — skipping product pie chart.")
    else:
        prod_sales = df.groupby('Product')['Total_Sales'].sum().sort_values(ascending=False)
        TOP_N = 6
        if len(prod_sales) > TOP_N:
            top = prod_sales.iloc[:TOP_N].copy()
            other_sum = prod_sales.iloc[TOP_N:].sum()
            top.loc["Other"] = other_sum
            pie_series = top
        else:
            pie_series = prod_sales

        plt.figure()
        pie_series.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.ylabel('')
        plt.title("Sales Distribution by Product")
        plt.tight_layout()
        plt.savefig(FIG_PIE)
        plt.show()
        print(f"Pie chart saved to '{FIG_PIE}'")
except Exception as e:
    print("Could not create pie chart:", e)


try:
    df.to_csv(PROCESSED_CSV, index=False)
    print(f"Processed data saved to '{PROCESSED_CSV}'")
    if 'Category' in df.columns:
        category_sales.to_csv(CATEGORY_SUMMARY_CSV)
        print(f"Category summary saved to '{CATEGORY_SUMMARY_CSV}'")
except Exception as e:
    print("Error saving CSV files:", e)

print("\n✅ Done. If you still see an error, paste the exact traceback here and I'll fix it.")
