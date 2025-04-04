import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

bucket_name = 'predi-conso-elec-region'
s3 = boto3.client('s3')

def get_latest_predictions():
    response = s3.get_object(Bucket=bucket_name, Key='predictions/latest_predictions.csv')
    return pd.read_csv(BytesIO(response['Body'].read()))

st.title("Energy Consumption Prediction")
df_pred = get_latest_predictions()
st.line_chart(df_pred.set_index("Datetime")["Predicted_Consumption"])
