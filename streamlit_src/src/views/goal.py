import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



player = 'Roger Federer'
df = pd.read_csv('https://github.com/ipython-books/'
                 'cookbook-2nd-data/blob/master/'
                 'federer.csv?raw=true',
                 parse_dates=['start date'],
                 dayfirst=True)

def load_view():    
    st.title("Page de l'objectif du projet")
    st.markdown("### Section 1 : Introduction - Description du projet. \n This is the legendary Titanic ML competition – the best, first challenge for you to dive into ML competitions and familiarize yourself with how the Kaggle platform works. The competition is simple: use machine learning to create a model that predicts which passengers survived the Titanic shipwreck. \nRead on or watch the video below to explore more details. Once you’re ready to start competing, click on the Join Competition button to create an account and gain access to the competition data. Then check out Alexis Cook’s Titanic Tutorial that walks you through step by step how to make your first submission!")

    st.title("Description des 10 premières lignes de notre dataframe")
    st.dataframe(df)
