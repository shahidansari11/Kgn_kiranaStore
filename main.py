import streamlit as st
import pandas as pd
import os
from datetime import datetime
import random
import string
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import time

# ---------------- CONFIG ----------------
ORDERS_FILE = "orders.csv"
ORDER_ITEMS_FILE = "order_items.csv"
BILLS_DIR = "bills"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="KGN Kirana Store", page_icon="🛒", layout="centered")

# ---------------- WELCOME ----------------
welcome_placeholder = st.empty()
welcome_placeholder.markdown(
    "<h1 style='text-align: center;'>स्वागत है | Welcome | خوش آمدید</h1>",
    unsafe_allow_html=True
)
time.sleep(2)
welcome_placeholder.empty()
st.markdown("---")

# ---------------- HELPERS ----------------
def load_orders():
    columns = ["OrderID", "Name", "Phone", "Email", "Address", "Order", "TotalPrice", "Status", "Timestamp"]
    if os.path.exists(ORDERS_FILE):
         try:
            return pd.read_csv(
                ORDERS_FILE,
                dtype={"OrderID": str},
                encoding="utf-8",      # Unicode safe
                on_bad_lines='skip',   # Skip corrupted lines
                skip_blank_lines=True  # Skip empty rows
            )
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df
            except Exception as e:
               st.error(f"Error reading orders.csv: {e}")
               return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)
def save_orders(df):
    df.to_csv(ORDERS_FILE, index=False)

def load_order_items():
    if os.path.exists(ORDER_ITEMS_FILE):
         try:
            return pd.read_csv(
                ORDER_ITEMS_FILE,
                encoding="utf-8",
                on_bad_lines='skip',
                skip_blank_lines=True
            )
         except Exception as e:
            st.error(f"Error reading order_items.csv: {e}")
            return pd.DataFrame(columns=["OrderID", "Item", "Qty", "UnitPrice", "ItemTotal"])
            return pd.read_csv(ORDER_ITEMS_FILE)
    return pd.DataFrame(columns=["OrderID", "Item", "Qty", "UnitPrice", "ItemTotal"])

def save_order_items(df):
    df.to_csv(ORDER_ITEMS_FILE, index=False)

def parse_order_items(order_text):
    order_text = str(order_text)
    items = []
    for part in order_text.split(","):
        words = part.strip().split()
        if len(words) >= 2:
            try:
                qty = float(words[0])
                item = " ".join(words[1:])
                items.append({"qty": qty, "item": item})
            except:
               items.append({"qty": 1, "item": part.strip()})
        else:
            items.append({"qty": 1, "item": part.strip()})
    return items

def generate_unique_order_id(existing_ids):
    while True:
        new_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if new_id not in existing_ids:
            return new_id

# Default item prices (example, update as needed)
ITEM_PRICES = {
    "rice": 50,
    "biscuit": 10,
    "sugar": 40,
    "dal": 100
}

# ---------------- PDF BILL ----------------
def generate_pdf_bill(order_row, order_items):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ---------- HEADER ----------
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-50, "🛒 KGN KIRANA STORE")

    c.setFont("Helvetica", 10)
    header_info = "Vill: Bhatahawaha, Thana & Post: Thakraha, Dist: West Champaran (Bihar), Pin: 845404"
    c.drawCentredString(width/2, height-65, header_info)
    c.drawCentredString(width/2, height-80, "📞 Phone: 9145206349")

    # Pro and Date left
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, height-30, "Pro. Irfan Ansari")
    c.drawString(50, height-45, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ---------- CUSTOMER INFO ----------
    c.setFont("Helvetica-Bold", 12)
    y = height - 100
    c.drawString(50, y, f"Name: {order_row.Name}")
    c.drawString(50, y-18, f"Phone: {order_row.Phone}")

    # Address
    c.setFont("Helvetica-Bold", 12)
    y_address = y - 36
    c.drawString(50, y_address, "Address:")
    y_address -= 15
    c.setFont("Helvetica", 12)
    address_lines = simpleSplit(order_row.Address, c._fontname, c._fontsize, width-100)
    for line in address_lines:
        c.drawString(70, y_address, line)
        y_address -= 15

    # Order ID
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_address-10, f"Order ID: {order_row.OrderID}")

    # ---------- ORDER ITEMS ----------
    c.setFont("Helvetica-Bold", 12)
    y_items = y_address - 40
    c.drawString(50, y_items, "Item")
    c.drawString(250, y_items, "Qty")
    c.drawString(350, y_items, "Unit Price")
    c.drawString(450, y_items, "Item Total")
    y_items -= 20

    c.setFont("Helvetica", 12)
    for item in order_items.itertuples():
        if y_items < 100:
            c.showPage()
            y_items = height - 50
        c.drawString(50, y_items, str(item.Item))
        c.drawString(250, y_items, str(item.Qty))
        c.drawString(350, y_items, f"₹{item.UnitPrice}")
        c.drawString(450, y_items, f"₹{item.ItemTotal}")
        y_items -= 20

    # ---------- GRAND TOTAL ----------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y_items-10, "Grand Total:")
    c.drawString(450, y_items-10, f"₹{order_row.TotalPrice}")

    # ---------- FOOTER ----------
    c.setFont("Helvetica-Oblique", 10)
    footer_text = f"Authorized by KGN Kirana Store | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    c.drawRightString(width-50, 30, footer_text)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

os.makedirs(BILLS_DIR, exist_ok=True)

# ---------------- FRONT PAGE CUSTOMER ORDER ----------------
def render_header():
    st.markdown("<h2 style='text-align: center;'>🛒 KGN KIRANA STORE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Vill: Bhatahawaha, Thana & Post: Thakraha, Dist: West Champaran (Bihar), Pin: 845404</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>📞 Phone: 9145206349</p>", unsafe_allow_html=True)

render_header()

col_left, col_right = st.columns([1,1])
with col_left:
    st.markdown("**Pro. Irfan Ansari**")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col_right:
    st.write("")  # empty right column
st.markdown("---")

st.subheader("📝 Place Your Order")
with st.form("order_form"):
    name = st.text_input("Your Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Your Address")
    order_text = st.text_area("Enter your order (e.g., `2 rice, 3 biscuit`)")
    submitted = st.form_submit_button("📩 Submit Order")

if submitted:
    if name and phone and address and order_text:
        orders = load_orders()
        order_items_df = load_order_items()
        order_id = generate_unique_order_id(orders["OrderID"].tolist())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parsed_items = parse_order_items(order_text)
        temp_list = []
        total_price = 0
        for item in parsed_items:
            qty = item["qty"]
            unit_price = ITEM_PRICES.get(item["item"].lower(), 0)
            item_total = qty * unit_price
            total_price += item_total
            temp_list.append({"OrderID": order_id,"Item": item["item"],"Qty": qty,"UnitPrice": unit_price,"ItemTotal": item_total})
        new_order = pd.DataFrame([[order_id, name, phone, "", address, order_text, total_price, "Pending", timestamp]],
                                 columns=["OrderID","Name","Phone","Email","Address","Order","TotalPrice","Status","Timestamp"])
        orders = pd.concat([orders, new_order], ignore_index=True)
        order_items_df = pd.concat([order_items_df, pd.DataFrame(temp_list)], ignore_index=True)
        save_orders(orders)
        save_order_items(order_items_df)

        # ✅ Customer popup
        st.success(f"✅ Order placed! Your Order ID is {order_id}")
        st.components.v1.html(f"""
        <script>
        alert("🎉 Your order {order_id} has been successfully placed!");
        </script>
        """, height=0)

        # 🔔 Admin notification
        st.info(f"📣 New order received: {order_id} from {name}")

        st.balloons()
    else:
        st.error("⚠️ Please fill all fields.")

# ---------------- ORDER TRACKING ----------------
st.subheader("🔎 Track Your Order / View My Order")
track_id = st.text_input("Enter your Order ID")
if st.button("View My Order Details"):
    orders = load_orders()
    items_df = load_order_items()
    if track_id in orders["OrderID"].values:
        order_row = orders.loc[orders["OrderID"]==track_id].iloc[0]
        order_items = items_df[items_df["OrderID"]==track_id]
        total_price = order_items["ItemTotal"].sum()
        order_row.TotalPrice = total_price

        render_header()

        # ----- CUSTOMER INFO -----
        st.write(f"**Name:** {order_row.Name}")
        st.write(f"**Phone:** {order_row.Phone}")
        st.write(f"**Address:** {order_row.Address}")
        st.write(f"**Order ID:** {order_row.OrderID}")
        st.write(f"**Status:** {order_row.Status}")
        st.write(f"**Total Price (Estimated/Confirmed):** ₹{order_row.TotalPrice}")

        st.table(order_items[["Item","Qty","UnitPrice","ItemTotal"]])

        # ----- PDF DOWNLOAD -----
        pdf_buffer = generate_pdf_bill(order_row, order_items)
        st.download_button("📥 Download PDF Bill", data=pdf_buffer, file_name=f"Bill_{track_id}.pdf", mime="application/pdf")
        st.balloons()
    else:
        st.error("❌ Order not found.")

# ---------------- ADMIN PANEL ----------------
st.subheader("🔐 Admin Panel")
password = st.text_input("Enter Admin Password", type="password")
if password == "1234":
    st.success("✅ Access Granted")
    orders = load_orders()
    items_df = load_order_items()
    if orders.empty:
        st.info("No orders yet.")
    else:
        st.subheader("📊 All Orders (Admin CSV View)")
        orders_editor = st.data_editor(orders, use_container_width=True, num_rows="dynamic")
        for _, row in orders.sort_values("Timestamp", ascending=False).iterrows():
            if pd.isna(row.Order) or str(row.Order).strip() == "":
                continue
            order_items_parsed = parse_order_items(row.Order)
            total_price = 0
            updated_items = []
            st.markdown(f"### Order #{row.OrderID} — {row.Name} ({row.Phone})")
            st.write(f"🏠 Address: {row.Address}")
            st.write(f"📝 Raw Order: {row.Order}")
            for item in order_items_parsed:
                col1, col2, col3 = st.columns([2,1,1])
                qty_val = col1.number_input(f"Qty ({item['item']})", min_value=0, value=int(item['qty']), step=1, key=f"qty_{row.OrderID}_{item['item']}")
                unit_price = col2.number_input(f"₹ per unit ({item['item']})", min_value=0.0, step=1.0, key=f"unit_{row.OrderID}_{item['item']}")
                item_total = qty_val * unit_price
                col3.write(f"Total: ₹{item_total}")
                total_price += item_total
                updated_items.append({"OrderID": row.OrderID, "Item": item["item"], "Qty": qty_val, "UnitPrice": unit_price, "ItemTotal": item_total})
            st.write(f"### 🧾 Grand Total: ₹{total_price}")
            colA, colB = st.columns(2)
            if colA.button("💾 Confirm Prices", key=f"confirm_{row.OrderID}"):
                orders.loc[orders["OrderID"]==row.OrderID, "TotalPrice"] = total_price
                orders.loc[orders["OrderID"]==row.OrderID, "Status"] = "Confirmed"
                save_orders(orders)
                items_df = items_df[items_df["OrderID"]!=row.OrderID]
                items_df = pd.concat([items_df, pd.DataFrame(updated_items)], ignore_index=True)
                save_order_items(items_df)

                row.TotalPrice = total_price
                pdf_buffer = generate_pdf_bill(row, pd.DataFrame(updated_items))
                pdf_path = os.path.join(BILLS_DIR, f"Bill_{row.OrderID}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(pdf_buffer.getvalue())

                # ✅ Admin popup for confirmation
                st.success(f"✅ Prices confirmed for Order {row.OrderID}. PDF saved.")
                st.components.v1.html(f"""
                <script>
                alert("🧾 Order {row.OrderID} has been confirmed!");
                </script>
                """, height=0)

                st.write(f"📁 Saved bill to `{pdf_path}`")
                st.download_button("📥 Download Generated Bill (PDF)", data=pdf_buffer, file_name=f"Bill_{row.OrderID}.pdf", mime="application/pdf")
st.markdown("<div style='text-align: center; margin-top: 2rem;'>🙏 Thank you for visiting us!</div>", unsafe_allow_html=True)
