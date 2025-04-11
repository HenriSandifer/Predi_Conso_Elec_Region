import streamlit as st
from src.router import redirect
def load_view():

    st.title("Page d'acceuil")
    st.markdown("""
    # Titanic Data Science Solutions
    ### This notebook is a companion to the book Data Science Solutions.

    The notebook walks us through a typical workflow for solving data science competitions at sites like Kaggle.

    There are several excellent notebooks to study data science competition entries. However many will skip some of the explanation on how the solution is developed as these notebooks are developed by experts for experts. The objective of this notebook is to follow a step-by-step workflow, explaining each step and rationale for every decision we take during solution development.

    ## Workflow stages
    The competition solution workflow goes through seven stages described in the Data Science Solutions book.

    1. Question or problem definition.
    2. Acquire training and testing data.
    3. Wrangle, prepare, cleanse the data.
    4. Analyze, identify patterns, and explore the data.
    5. Model, predict and solve the problem.
    6. Visualize, report, and present the problem solving steps and final solution.
    7. Supply or submit the results.
    8. The workflow indicates general sequence of how each stage may follow the other. However there are use cases with exceptions.

    We may combine mulitple workflow stages. We may analyze by visualizing data.
    Perform a stage earlier than indicated. We may analyze data before and after wrangling.
    Perform a stage multiple times in our workflow. Visualize stage may be used multiple times.
    Drop a stage altogether. We may not need supply stage to productize or service enable our dataset for a competition.
    Question and problem definition
    Competition sites like Kaggle define the problem to solve or questions to ask while providing the datasets for training your data science model and testing the model results against a test dataset. The question or problem definition for Titanic Survival competition is described here at Kaggle.

    Knowing from a training set of samples listing passengers who survived or did not survive the Titanic disaster, can our model determine based on a given test dataset not containing the survival information, if these passengers in the test dataset survived or not.
    We may also want to develop some early understanding about the domain of our problem. This is described on the Kaggle competition description page here. Here are the highlights to note.

    """)