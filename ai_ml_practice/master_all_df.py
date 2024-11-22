import pymysql
import pandas as pd

# Database connection
database = pymysql.connect(
    host='localhost',
    user='root',
    password='actowiz',
    database='burger_king'
)

# Table names
tables = [
    "burger_king_details", "boot_barn_details", "charlottetilbury_locatore",
    "city_trends_details", "columbia_sportswear_details", "home_goods_details",
    "lk_bennett_details", "mark_jacobs_details", "patagonia_details",
    "rainbow_store_locator", "ralphlauren", "tj_maxx"
]

# Load and concatenate data
master_df = pd.concat(
    [pd.read_sql(f"SELECT name, name_xpath, name_html FROM {table}", database) for table in tables],
    ignore_index=True
)

# Close connection and export to Excel
database.close()
master_df.to_excel("master_data.xlsx", index=False)

print("Data exported successfully to master_data.xlsx")
