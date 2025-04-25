import pandas as pd
import openpyxl

def load_csv(file_path: str) -> pd.DataFrame:
    """Charge un fichier CSV dans un DataFrame pandas"""
    return pd.read_csv(file_path)

def load_excel(file_path: str) -> pd.DataFrame:
    """Charge un fichier Excel dans un DataFrame pandas"""
    return pd.read_excel(file_path) 