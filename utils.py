import pandas as pd

def load_hydropower_data(filepath):
    return pd.read_csv(filepath)

def load_rainfall_data(filepath):
    return pd.read_csv(filepath)

def load_salient_features(filepath):
    return pd.read_csv(filepath)
