import streamlit as st
import pandas as pd
import os
from datetime import date
from io import BytesIO

FILE_NAME = "site_expenses.csv"

# Expense columns
EXPENSE_COLUMNS = ["Fuel", "Food", "Purchase", "Hotel", "Other Expenses"]

# Create CSV if it doesn't exist
if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=[
        "Date",
        "Project Name",
        "Person Name",
        "Category"] + EXPENSE_COLUMNS + ["Total", "Narration"]
    ).to_csv(FILE_NAME, index=False)

st.set_page_config(page_title="Site Expense Manager", layout="wide")
st.title("🏗️ Site Expense Management System")

# Load data
df = pd.read_csv(FILE_NAME)

# ---------------- ADD / EDIT EXPENSE ----------------
st.header("➕ Add / Edit Expense")

# Select row to edit
edit_index = st.selectbox(
    "Select a row to edit (or 'New Entry')",
    ["New Entry"] + df.index.astype(str).tolist()
)

if edit_index != "New Entry":
    edit_index = int(edit_index)
    row = df.loc[edit_index]
    expense_date = st.date_input("Date", pd.to_datetime(row["Date"]))
    project_name = st.text_input("Project Name", row["Project Name"])
    person_name = st.text_input("Person Name", row["Person Name"])
    category = st.selectbox(
        "Category",
        ["Installation", "Additional Site Expense", "Delivery", "Installation + Delivery", "Measurement"],
        index=["Installation", "Additional Site Expense", "Delivery", "Installation + Delivery", "Measurement"].index(row["Category"])
    )
    expense_values = {}
    for exp in EXPENSE_COLUMNS:
        expense_values[exp] = st.number_input(f"{exp} (₹)", value=float(row[exp]), min_value=0.0, step=1.0)
    narration = st.text_area("Narration / Details", row["Narration"])
else:
    expense_date = st.date_input("Date", date.today())
    project_name = st.text_input("Project Name")
    person_name = st.text_input("Person Name")
    category = st.selectbox(
        "Category",
        ["Installation", "Additional Site Expense", "Delivery", "Installation + Delivery", "Measurement"]
    )
    expense_values = {}
    for exp in EXPENSE_COLUMNS:
        expense_values[exp] = st.number_input(f"{exp} (₹)", min_value=0.0, step=1.0)
    narration = st.text_area("Narration / Details")

# Calculate total
total_amount = sum(expense_values.values())

# Buttons for Save / Update
if st.button("Save Entry" if edit_index == "New Entry" else "Update Entry"):
    if project_name and person_name:
        new_row = {
            "Date": expense_date.isoformat(),
            "Project Name": project_name,
            "Person Name": person_name,
            "Category": category,
            **expense_values,
            "Total": total_amount,
            "Narration": narration
        }

        if edit_index == "New Entry":
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            st.success(f"✅ Expense Saved Successfully. Total: ₹{total_amount}")
            # Clear fields by rerunning the app
            st.experimental_rerun()
        else:
            df.loc[edit_index] = new_row
            df.to_csv(FILE_NAME, index=False)
            st.success(f"✅ Expense Updated Successfully. Total: ₹{total_amount}")
    else:
        st.warning("⚠️ Project Name and Person Name are required")

# ---------------- VIEW RECORDS ----------------
st.header("📋 Expense Records")

project_filter = st.selectbox(
    "Filter by Project",
    ["All"] + sorted(df["Project Name"].dropna().unique().tolist())
)

if project_filter != "All":
    view_df = df[df["Project Name"] == project_filter]
else:
    view_df = df

st.table(view_df)

# ---------------- SUMMARY ----------------
st.header("📊 Expense Summary (Project-wise)")

if not view_df.empty:
    summary = view_df.groupby("Project Name")[EXPENSE_COLUMNS + ["Total"]].sum().reset_index()
    st.table(summary)
else:
    st.info("No data available")

# ---------------- DOWNLOAD EXCEL ----------------
st.header("⬇️ Download Excel")

def to_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Expenses")
    return output.getvalue()

excel_data = to_excel(view_df)

st.download_button(
    label="Download Excel Report",
    data=excel_data,
    file_name="site_expense_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
