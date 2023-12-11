# example/st_app.py

import streamlit as st
import pandas as pd
import time
import pickle
import plotly.express as px
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

#st.write(st.secrets['connections'])
st.set_page_config(page_icon=':bar_chart',page_title='Google Sheets',layout='wide')

#----------AUTHENTICATION PROCESS--------------------#
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
#----------------AFTER AUTHENTICATION---------------------#
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome {username}")
    #------CREATING OPTIONS MENU--------#
    selected = option_menu(
         menu_icon=None,
         menu_title=None,
         options=['Data Entry', 'Data Visualization'],
         icons=['pen-fill', 'bar-chart-fill'],
         orientation='horizontal',
         default_index=0
    )
    #--------------CHECKING SELECTED OPTIONS---------------#
    if selected == 'Data Entry':
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
                        alert1 = st.warning('Ensure all Mandatory fields are filled')
                        time.sleep(5)
                        alert1.empty()
                        st.stop()
                    elif existing_data['CompanyName'].str.contains(company_name).any():
                        alert2 = st.warning('A company with this name exists')
                        time.sleep(5)
                        alert2.empty()
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
#---------------------OPTION B----------------------------------------------------------------# 
    if selected == 'Data Visualization':
         conn = st.connection("gsheets", type=GSheetsConnection)

         existing_data = conn.read()
         new_data = existing_data.dropna(axis=1,how='all')

         col1, col2 = st.columns((2))
         with col1:
              st.subheader('DataFrame')
              st.write(new_data)
         with col2:
              st.subheader('Company Wise Sales')
              fig = px.bar(new_data, x='CompanyName', y='Sales(USD)')
              st.plotly_chart(fig,use_container_width=True)
        
         col3, col4 = st.columns((2))
         with col3:
              st.subheader('BusinessType Sales')
              fig = px.pie(new_data, values='Sales(USD)', names='BusinessType',template='plotly_dark')
              fig.update_traces(text=new_data['BusinessType'], textposition='outside')
              st.plotly_chart(fig,use_container_width=True)
         with col4:
              st.subheader('Relationship between Years in Business and Sales')
              fig = px.box(new_data, x='YearsInBusiness', y='Sales(USD)')
              st.plotly_chart(fig,use_container_width=True)

        
         
            