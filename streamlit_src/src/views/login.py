import streamlit as st
from src.controllers.auth import auth
from src.controllers.signup import signup

from src.router import redirect
def load_view():
    st.title('Login')

    email = st.text_input('Email', '')
    password = st.text_input('Password', '', type='password')
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        log_in_button = st.button('Login')
    with col2:
        sign_up_button = st.button('Sign up')


    if log_in_button:
        res = auth(email, password)
        if not res:
            st.text("Wrong Account")
        else: 
            st.text("login in progress")
            redirect("home", reload=True)
    
    elif sign_up_button:
        res = signup(email, password)
        if not res:
            st.text("E-mail already used. Please, log in.")
        else: 
            st.text("Sign up in progress...")
            redirect("home", reload=True)