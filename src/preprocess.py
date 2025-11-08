"""Preprocessing pipeline for salary prediction model."""
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer


def create_preprocessor(categorical_cols, numeric_cols):
    """
    Create a preprocessor for categorical and numeric columns.
    
    Args:
        categorical_cols: List of categorical column names
        numeric_cols: List of numeric column names
    
    Returns:
        ColumnTransformer: Fitted preprocessor
    """
    cat_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    num_transformer = StandardScaler()

    preprocessor = ColumnTransformer([
        ("cat", cat_transformer, categorical_cols),
        ("num", num_transformer, numeric_cols)
    ])
    return preprocessor

