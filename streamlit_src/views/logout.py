import streamlit as st
from src.controllers.auth import logout
from src.router import redirect

def load_view():
    logout()
    redirect("/login", reload=True)


