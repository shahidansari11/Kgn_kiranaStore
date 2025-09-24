import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

st.set_page_config(page_title="KGN Kirana Store", page_icon="🛒", layout="centered")
st.header("🛒 KGN KIRANA STORE")
st.subheader("Pro: Irfan Ansari")
st.subheader("📞 Phone: 9145206349")
st.markdown("🚚 Home Delivery: **FREE**")


with st.form("order_form"):
    st.markdown("### Place Your Order")
    name = st.text_input("Enter your name")
    order = st.text_area("Enter your order")
    address = st.text_area("Enter your full address")
    phone = st.text_input("Enter your phone number")
    submitted = st.form_submit_button("✅ Submit Order")

if submitted:
    if not name.strip() or not order.strip() or not address.strip() or not phone.strip():
        st.error("⚠️ Please fill all the details!")
    elif not phone.isdigit() or len(phone) != 10:
        st.error("⚠️ Please enter a valid 10-digit phone number.")
    else:
        file_exists = os.path.isfile("orders.csv")
        
        
        order_id = 1
        if file_exists:
            existing_df = pd.read_csv("orders.csv")
            if not existing_df.empty:
                order_id = existing_df["OrderID"].max() + 1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Pending"
        
        df = pd.DataFrame([[order_id, name, order, address, phone, timestamp, status]], 
                          columns=["OrderID","Name", "Order", "Address", "Phone", "Timestamp", "Status"])
        df.to_csv("orders.csv", mode="a", header=not file_exists, index=False)

        
        st.success(f"✅ Your order has been placed successfully! Your Order ID is {order_id}")
        st.balloons()
        st.markdown(f"""
        **Order ID:** {order_id}  
        **Name:** {name}  
        **Order:** {order}  
        **Address:** {address}  
        **Phone:** {phone}  
        **Timestamp:** {timestamp}  
        **Status:** {status}  
        """)
        st.progress(0)
        for i in range(1, 101, 10):
            st.progress(i)
            time.sleep(0.1)
        st.snow()


st.markdown("---")
admin_pass = st.text_input("Enter admin password", type="password")

if admin_pass == "Shahid@2068":
    st.subheader("📋 Admin Panel: View & Manage Orders")
    try:
        data = pd.read_csv("orders.csv")
        for index, row in data.iterrows():
            col1, col2, col3 = st.columns([1, 4, 2])
            with col1:
                st.write(row['OrderID'])
            with col2:
                st.write(f"{row['Name']} | {row['Order']} | {row['Status']}")
            with col3:
                if row['Status'] == "Pending":
                    if st.button(f"✅ Confirm {row['OrderID']}", key=f"confirm_{row['OrderID']}"):
                        data.at[index, 'Status'] = "Confirmed"
                        data.to_csv("orders.csv", index=False)
                        st.success(f"Order {row['OrderID']} confirmed!")
        edited_df = st.data_editor(data, num_rows="dynamic")
        st.dataframe(edited_df)

        
        if st.button("💾 Save Changes"):
            edited_df.to_csv("orders.csv", index=False)
            st.success("✅ Orders updated successfully!")
    except FileNotFoundError:
        st.warning("⚠️ No orders yet!")

elif admin_pass:
    st.error("❌ Wrong password! Access denied.")

st.markdown("🙏 Thank you for visiting us!")

