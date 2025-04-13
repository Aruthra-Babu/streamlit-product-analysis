import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit as st

# Streamlit file uploader
st.title("Product Shelf Life Analysis")
st.sidebar.header("Upload your CSV file")

# Use the Streamlit file uploader widget to upload a CSV file
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load dataset from the uploaded file
    df = pd.read_csv(uploaded_file)

    # Convert date columns
    df['Date of Manufacturing'] = pd.to_datetime(df['Date of Manufacturing'], errors='coerce')
    df['Date of Expiry'] = pd.to_datetime(df['Date of Expiry'], errors='coerce')

    # Remove rows with invalid dates
    df.dropna(subset=['Date of Manufacturing', 'Date of Expiry'], inplace=True)

    # Today's date
    today = datetime.today().date()

    # Numeric features
    df['Manufacturing Days'] = (df['Date of Manufacturing'] - pd.Timestamp("1970-01-01")).dt.days
    df['Expiry Days'] = (df['Date of Expiry'] - pd.Timestamp("1970-01-01")).dt.days
    df['Days Since Manufacturing'] = (datetime.today() - df['Date of Manufacturing']).dt.days
    df['Remaining Shelf Life'] = (df['Date of Expiry'] - datetime.today()).dt.days

    # ✅ Final Consumability Logic
    df['Status'] = df.apply(lambda row:
        0 if row['Date of Manufacturing'] > row['Date of Expiry']
        else (1 if row['Date of Expiry'].date() > today else 0), axis=1)

    # Features & Target
    features = ['Manufacturing Days', 'Expiry Days', 'Days Since Manufacturing', 'Remaining Shelf Life']

    # Displaying overall product status (pie chart for Consumable vs Not Consumable)
    status_labels = ['Consumable', 'Not Consumable']
    status_sizes = [df['Status'].sum(), len(df) - df['Status'].sum()]
    status_colors = ['green', 'red']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(status_sizes, labels=status_labels, colors=status_colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    st.write("\n**Overall Shelf Life Status** (Consumable vs Not Consumable)")
    st.pyplot(fig)

    # User input for prediction (selecting a product by index)
    product_index = st.number_input(f"Enter a product number from 1 to {len(df)}", min_value=1, max_value=len(df), step=1)

    if product_index:
        product = df.iloc[product_index - 1]
        st.write(f"\n**Product Name:** {product['Item Name']}")
        st.write(f"**Manufacturing Date:** {product['Date of Manufacturing'].strftime('%Y-%m-%d')}")
        st.write(f"**Expiry Date:** {product['Date of Expiry'].strftime('%Y-%m-%d')}")
        st.write(f"**Days Since Manufacturing:** {product['Days Since Manufacturing']} days")
        st.write(f"**Remaining Shelf Life:** {product['Remaining Shelf Life']} days")
        
        # Status analysis
        status = "Consumable" if product['Status'] == 1 else "Not Consumable"
        st.write(f"**Status:** {status}")

        # Bar graph for Remaining Shelf Life of selected product (just one product)
        plt.figure(figsize=(7, 5))
        colors = ['green' if product['Status'] == 1 else 'red']
        bars = plt.bar(product['Item Name'], product['Remaining Shelf Life'], color=colors)

        # Add labels/icons on top of the bar
        height = bars[0].get_height()
        label = "✔️" if product['Status'] == 1 else "❌"
        plt.text(bars[0].get_x() + bars[0].get_width() / 2, height + 1, label,
                 ha='center', va='bottom', fontsize=10, color='black')

        plt.title(f"Remaining Shelf Life of {product['Item Name']}", fontsize=14)
        plt.xlabel("Product Name")
        plt.ylabel("Remaining Shelf Life (Days)")
        plt.tight_layout()

        st.write(f"\n**Remaining Shelf Life for {product['Item Name']}**")
        st.pyplot(plt)

else:
    st.write("❗ Please upload a CSV file to proceed.")
