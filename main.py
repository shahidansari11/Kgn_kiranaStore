import streamlit as st
import pandas as pd
import  time

st.header("🛒 KGN KIRANA STORE")
st.subheader("📞 Phone: 9145206349")
st.markdown("🚚 Home Delivery: **FREE**")


with st.form("order_form"):
    name = st.text_input("Enter your name")
    order = st.text_area("Enter your order")
    address = st.text_area("Enter your full address")
    phone = st.text_input("Enter your phone number")

    submitted = st.form_submit_button("✅ Submit Order")

if submitted:
    
        
        if not name or not order or not address or not phone:
            st.error("⚠️ Please fill all the details!")
        elif not phone.isdigit() or len(phone) != 10:
         st.error("⚠️ Please enter a valid 10-digit phone number.")
        else:
            df = pd.DataFrame([[name, order, address, phone]],
                          columns=["Name", "Order", "Address", "Phone"])
        df.to_csv("orders.csv", mode="a", header=False, index=False)
        data = pd.read_csv("orders.csv", names=["Name", "Order", "Address", "Phone"])
        


        st.success("✅ Your order has been placed successfully!")

        st.markdown(f"""
        **Name:** {name}  
        **Order:** {order}  
        **Address:** {address}  
        **Phone:** {phone}  
        """)
        st.balloons()
        st.snow()
        st.progress(50)
        with st.spinner("Placing your order..."):
            
            time.sleep(2)


st.balloons()


if st.button("📋 View All Orders"): 
        pd.read_csv("orders.csv")
        try:
            data=pd.read_csv("orders.csv")
            st.dataframe(data)
        except FileNotFoundError:
         st.warning("⚠️ Abhi tak koi order nahi aaya hai.")


st.markdown("🙏 Thank you for visiting us!")
