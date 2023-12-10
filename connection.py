# example/st_app.py

import streamlit as st
import pandas as pd
import time
import pickle
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

#st.write(st.secrets['connections'])
st.set_page_config(page_icon=':bar_chart',page_title='Google Sheets')

names = ['Stormy Ndonga', 'User 1']
usernames = ['Storm', 'User']
with open('hashed_pw.pkl', 'rb') as f:
     hashed_passwords = pickle.load(f)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'sheets', 'abcd', cookie_expiry_days=15)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
     st.error('Username/Password is incorrect')
if authentication_status == None:
     st.warning('Please insert Username and Password')
if authentication_status:
    st.title(f"Welcome {username}")
    conn = st.connection("gsheets", type=GSheetsConnection)

    existing_data = conn.read()
    existing_data = existing_data.dropna(how='all')

    business_types = [
            "Technology",
            "Office Supplies",
            "Furniture"
        ]
    products = [
            "Software",
            "Hardware",
            "Papers",
            "Binders",
            "NoteBooks",
            "Chairs",
            "Tables",
            "Sofas",
            "Other"
        ]

    with st.form(key='vendor_form'):
            company_name = st.text_input(label='Company Name*')
            business_type = st.selectbox('Business Type*', options=business_types,index=None)
            products = st.multiselect('Products*', options=products)
            years = st.number_input(label='Years in Business')
            sales = st.number_input(label='Sales')

            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                if not company_name or not business_type or not products:
                    st.warning('Ensure all Mandatory fields are filled')
                    st.stop()
                elif existing_data['CompanyName'].str.contains(company_name).any():
                    st.warning('A company with this name exists')
                    st.stop()
                else:
                    #Create a new dataframe-vendor data
                    company_data = pd.DataFrame([{
                        "CompanyName": company_name,
                        "BusinessType": business_type,
                        "Products":",".join(products),
                        "YearsInBusiness": years,
                        "Sales(USD)": sales
                    }])
                    
                    #Add the new vendor data to data
                    updated_df = pd.concat([existing_data, company_data])
                    updated_df = updated_df.dropna(how='all')
                    #Connecting with the google sheets and updating
                    conn.update(worksheet='Companies', data=updated_df)

                    alert = st.success('Submitted Successfully')
                    time.sleep(5)#wait for 5 seconds
                    alert.empty()#clear the message
    authenticator.logout('Logout', 'main')


    