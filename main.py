import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# ----------------- Helper Functions -----------------

def load_orders_data():
    """Loads orders from the CSV file. Returns an empty DataFrame if the file doesn't exist."""
    if os.path.isfile("orders.csv"):
        return pd.read_csv("orders.csv")
    return pd.DataFrame(columns=["OrderID", "Name", "Order", "Address", "Phone", "Timestamp", "Status"])

def save_orders_data(df):
    """Saves the entire DataFrame to the CSV file, overwriting the existing file."""
    df.to_csv("orders.csv", index=False)

def add_order(name, order, address, phone):
    """Adds a new order to the CSV file."""
    df = load_orders_data()
    
    # Generate a new OrderID
    if not df.empty and 'OrderID' in df.columns and df['OrderID'].notna().any():
        order_id = df["OrderID"].max() + 1
    else:
        order_id = 1
        
    # Create new order details
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Pending"
    
    # Create a DataFrame for the new order
    new_order_df = pd.DataFrame(
        [[order_id, name, order, address, phone, timestamp, status]],
        columns=["OrderID", "Name", "Order", "Address", "Phone", "Timestamp", "Status"]
    )
    
    # Append the new order to the existing DataFrame and save
    updated_df = pd.concat([df, new_order_df], ignore_index=True)
    save_orders_data(updated_df)
    
    return order_id, timestamp, status

# ----------------- Page Configuration -----------------
st.set_page_config(page_title="KGN Kirana Store", page_icon="🛒", layout="centered")

# ----------------- Header -----------------
st.header("🛒 KGN KIRANA STORE")
st.markdown("*Proprietor:* Irfan Ansari")
st.markdown("📞 *Phone:* 9145206349")
st.markdown("🚚 *Home Delivery:* FREE")

# ----------------- Order Form -----------------
with st.form("order_form"):
    st.markdown("### Place Your Order")
    name = st.text_input("Enter your name")
    order = st.text_area("Enter your order (e.g., 1kg Sugar, 2L Milk)")
    address = st.text_area("Enter your full address")
    phone = st.text_input("Enter your 10-digit phone number")
    submitted = st.form_submit_button("✅ Submit Order")

if submitted:
    # --- Form Validation ---
    if not all([name.strip(), order.strip(), address.strip(), phone.strip()]):
        st.error("⚠ Please fill in all the details!")
    elif not phone.isdigit() or len(phone) != 10:
        st.error("⚠ Please enter a valid 10-digit phone number.")
    else:
        try:
            # --- Add Order and Show Success ---
            order_id, timestamp, status = add_order(name, order, address, phone)
            
            st.success(f"✅ Your order has been placed successfully! Your Order ID is *{order_id}*")
            st.balloons()

            with st.expander("View Order Details"):
                st.markdown(f"*Order ID:* {order_id}")
                st.markdown(f"*Name:* {name}")
                st.markdown(f"*Order:* {order}")
                st.markdown(f"*Address:* {address}")
                st.markdown(f"*Phone:* {phone}")
                st.markdown(f"*Timestamp:* {timestamp}")
                st.markdown(f"*Status:* {status}")
            
            # --- Progress Animation ---
            progress_text = "Finalizing your order..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(0.5)
            my_bar.empty()
            st.info("You will be notified once the order is confirmed.")

        except Exception as e:
            st.error(f"An error occurred while placing your order: {e}")

# ----------------- Admin Panel -----------------
st.markdown("---")
st.subheader("👨‍💼 Admin Section")

# --- Password Protection ---
# IMPORTANT: For a real application, use st.secrets for secure password management.
admin_pass = st.text_input("Enter admin password", type="password", key="admin_password")

# --- Check Password ---
# NOTE: Replace "Shahid@2068" with a password from st.secrets in a real app.
if admin_pass == "Shahid@2068":
    st.success("Access Granted!")
    st.header("📋 Admin Panel: View & Manage Orders")
    
    try:
        data = load_orders_data()

        if data.empty:
            st.warning("⚠ No orders yet!")
        else:
            # --- Display Orders in a more organized way ---
            for index, row in data.iterrows():
                st.markdown(f"#### Order #{row['OrderID']}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Name", value=row["Name"], key=f"name_{index}_{row['OrderID']}", disabled=True)
                    st.text_input("Phone", value=row["Phone"], key=f"phone_{index}_{row['OrderID']}", disabled=True)
                    st.text_input("Status", value=row["Status"], key=f"status_{index}_{row['OrderID']}", disabled=True)

                with col2:
                    st.text_area("Address", value=row["Address"], key=f"address_{index}_{row['OrderID']}", height=100, disabled=True)
                    st.text_area("Order", value=row["Order"], key=f"order_{index}_{row['OrderID']}", height=100, disabled=True)
                
                # --- Action Buttons ---
                action_cols = st.columns(3)
                if action_cols[0].button("✅ Confirm Order", key=f"confirm_{index}_{row['OrderID']}", use_container_width=True, type="primary", disabled=(row['Status'] == 'Confirmed')):
                    data.loc[index, "Status"] = "Confirmed"
                    save_orders_data(data)
                    st.toast(f"Order {row['OrderID']} confirmed!")
                    time.sleep(1) # Give toast time to show
                    st.rerun()

                if action_cols[1].button("🚚 Mark as Shipped", key=f"ship_{index}_{row['OrderID']}", use_container_width=True, disabled=(row['Status'] != 'Confirmed')):
                    data.loc[index, "Status"] = "Shipped"
                    save_orders_data(data)
                    st.toast(f"Order {row['OrderID']} marked as shipped!")
                    time.sleep(1)
                    st.rerun()
                
                if action_cols[2].button("❌ Cancel Order", key=f"cancel_{index}_{row['OrderID']}", use_container_width=True):
                    data.loc[index, "Status"] = "Cancelled"
                    save_orders_data(data)
                    st.toast(f"Order {row['OrderID']} has been cancelled.")
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("---")

            # --- Full Data View ---
            with st.expander("📊 Show All Orders in a Table"):
                st.dataframe(data)

    except FileNotFoundError:
        st.warning("⚠ No orders file found. Place an order to create one.")
    except Exception as e:
        st.error(f"An error occurred in the admin panel: {e}")

elif admin_pass: # If password is typed but incorrect
    st.error("❌ Wrong password! Access denied.")

st.markdown("<div style='text-align: center; margin-top: 2rem;'>🙏 Thank you for visiting us!</div>", unsafe_allow_html=True)

