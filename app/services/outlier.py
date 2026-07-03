import pandas as pd


class OutlierDetector:
    """Handles outlier detection and highlighting."""

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        aggregate_column: str,
        threshold: float = 2.0
    ) -> pd.DataFrame:
        """
        Add is_outlier column to DataFrame.

        Marks rows where value deviates more than threshold * std from mean.
        """
        mean = df[aggregate_column].mean()
        std = df[aggregate_column].std()
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
        df['is_outlier'] = (
            (df[aggregate_column] < lower_bound) |
            (df[aggregate_column] > upper_bound)
        )
        return df

    @staticmethod
    def highlight_outliers(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Apply conditional formatting to highlight outlier rows in a column.

        Uses IQR method: values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
        are considered outliers.
        """
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        styled_df = df.copy()
        styled_df['_style'] = ''

        outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
        styled_df.loc[outlier_mask, '_style'] = (
            'background-color: #ffcccc; font-weight: bold;'
        )

        return styled_df
