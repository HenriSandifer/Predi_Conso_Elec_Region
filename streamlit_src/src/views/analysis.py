import streamlit as st

import pandas as pd
import numpy as np
import random as rnd

# visualization
import seaborn as sns
import matplotlib.pyplot as plt

# machine learning
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier

def load_view():
    st.title('Analysis Page')
    st.code("""
    # data analysis and wrangling
    import pandas as pd
    import numpy as np
    import random as rnd
    
    # visualization
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # machine learning
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC, LinearSVC
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.naive_bayes import GaussianNB
    from sklearn.linear_model import Perceptron
    from sklearn.linear_model import SGDClassifier
    from sklearn.tree import DecisionTreeClassifier


    train_df = pd.read_csv('titanic/train.csv')
    test_df = pd.read_csv('titanic/test.csv')
    combine = [train_df, test_df]
    """)
    
    st.markdown("""
    **Which features are categorical?**
    These values classify the samples into sets of similar samples. Within categorical features are the values nominal, ordinal, ratio, or interval based? Among other things this helps us select the appropriate plots for visualization.
    - Categorical: Survived, Sex, and Embarked. Ordinal: Pclass.

    **Which features are numerical?**

    Which features are numerical? These values change from sample to sample. Within numerical features are the values discrete, continuous, or timeseries based? Among other things this helps us select the appropriate plots for visualization.
    - Continous: Age, Fare. Discrete: SibSp, Parch.
    """)

