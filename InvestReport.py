import streamlit as st
import pyodbc as pyod 
import pandas as pd
import matplotlib.pyplot as plt

# Define the connection string
connection_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=AGILEDB\\DEV2019;"
    "Database=UON;"
    "Uid=erp;"
    "Pwd=Pass@7046.;"
)

# Connect to the database
connection = pyod.connect(connection_str)
cursor = connection.cursor()

# Read data from the database
G_LEntry = pd.read_sql(
    """
    SELECT *, b.[G_L Account No_] 
    FROM [UON PEN RBS$G_L Entry$7d966dd5-a317-4db2-b529-926bbce15abf] a
    JOIN [UON PEN RBS$G_L Entry$437dbf0e-84ff-417a-965d-ed2bb9650972] b
    ON a.[Entry No_] = b.[Entry No_]
    """, 
    connection
)

# Function to rename duplicate columns
def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

# Rename duplicate columns in G_LEntry DataFrame
G_LEntry = rename_duplicate_columns(G_LEntry)

# Function to determine investment type based on "G_L Account No_"
def get_investment_type(account_no):
    switcher = {
        "120-0009": "Coperate Bonds",
        "120-0004": "OffShore",
        "120-0006": "Quoted Equities",
        "120-0010": "ShortTerm Deposit",
        "120-0008": "Treasury Bills",
        "120-0007": "Treasury Bonds",
        "120-0005": "Unquoted Equities"
    }
    return switcher.get(account_no, "Other")

# Create the "Investment Type" column
G_LEntry['Investment Type'] = G_LEntry['G_L Account No__1'].apply(get_investment_type)

# Exclude the "Other" category
G_LEntry_filtered = G_LEntry[G_LEntry['Investment Type'] != "Other"]

# Display the first 10 rows of the DataFrame
st.write("First 10 rows of G_LEntry DataFrame:")
st.dataframe(G_LEntry_filtered.head(10))

# Display the list of columns in the DataFrame
st.write("Columns in G_LEntry DataFrame:")
st.write(G_LEntry_filtered.columns.tolist())

# Create a summary table to group sum of "AmtExt" by "Investment Type"
summary_table = G_LEntry_filtered.groupby('Investment Type')['AmtExt'].sum().reset_index()

# Display the summary table
st.write("Summary Table (Sum of AmtExt by Investment Type):")
st.dataframe(summary_table)


# Plotting the bar chart with data labels
fig, ax = plt.subplots()
bars = ax.bar(summary_table['Investment Type'], summary_table['AmtExt'], color='skyblue')

# Add data labels to the bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05 * max(summary_table['AmtExt']), round(yval, 2), ha='center', va='bottom')

# Customize the chart
ax.set_xlabel('Investment Type')
ax.set_ylabel('Sum of AmtExt')
ax.set_title('Sum of AmtExt by Investment Type')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Display the chart using Streamlit
st.pyplot(fig)


# Plotting the pie chart
fig, ax = plt.subplots()
ax.pie(summary_table['AmtExt'], labels=summary_table['Investment Type'], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(range(len(summary_table))))

# Equal aspect ratio ensures that pie is drawn as a circle.
ax.axis('equal')  
plt.title('Sum of AmtExt by Investment Type')

# Display the chart using Streamlit
st.pyplot(fig)