import psycopg2
import csv

# Path to the output CSV file
csv_path = "/Users/work/Desktop/properties.csv"

# Connect to the PostgreSQL database
conn = psycopg2.connect(dbname="properties", user="work", password="", host="localhost")
cursor = conn.cursor()

# Query to select all data from the properties table
query = "SELECT * FROM properties"

# Execute the query
cursor.execute(query)

# Fetch all rows from the executed query
rows = cursor.fetchall()

# Get the column names from the cursor description
column_names = [desc[0] for desc in cursor.description]

# Write the data to a CSV file
with open(csv_path, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    # Write the column names as the first row
    writer.writerow(column_names)
    # Write the data rows
    writer.writerows(rows)

# Close the cursor and connection
cursor.close()
conn.close()

print(f"Data from 'properties' table has been exported to {csv_path}")
