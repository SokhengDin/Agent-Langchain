from typing import Dict, List, Optional, Annotated
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import joblib

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app import logger

class MLTools:
    """Tools for machine learning model training and evaluation"""

    @staticmethod
    @tool("train_linear_regression")
    async def train_linear_regression(
        file_path       : str
        , target_column : str
        , feature_columns: List[str]
        , test_size     : float = 0.2
        , state         : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Train linear regression model

        Args:
            file_path       : Path to data file
            target_column   : Target variable column
            feature_columns : List of feature columns
            test_size       : Test set proportion

        Returns:
            Dict with model metrics and save path
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            X = df[feature_columns]
            y = df[target_column]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            model = LinearRegression()
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            model_dir = Path("output/models")
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = str(model_dir / "linear_regression.pkl")
            joblib.dump(model, model_path)

            logger.info(f"Linear regression trained - R2: {r2:.4f}")

            return {
                "status"    : 200
                , "message" : "Model trained successfully"
                , "data"    : {
                    "model_type"    : "Linear Regression"
                    , "mse"         : float(mse)
                    , "rmse"        : float(np.sqrt(mse))
                    , "r2_score"    : float(r2)
                    , "model_path"  : model_path
                    , "features"    : feature_columns
                    , "target"      : target_column
                }
            }

        except Exception as e:
            logger.error(f"Error training linear regression: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to train model: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("train_random_forest")
    async def train_random_forest(
        file_path       : str
        , target_column : str
        , feature_columns: List[str]
        , task_type     : str = "regression"
        , n_estimators  : int = 100
        , test_size     : float = 0.2
        , state         : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Train random forest model

        Args:
            file_path       : Path to data file
            target_column   : Target variable
            feature_columns : Feature columns
            task_type       : 'regression' or 'classification'
            n_estimators    : Number of trees
            test_size       : Test set proportion

        Returns:
            Dict with model metrics
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            X = df[feature_columns]
            y = df[target_column]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            if task_type == "regression":
                model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                metrics = {
                    "mse"       : float(mean_squared_error(y_test, y_pred))
                    , "rmse"    : float(np.sqrt(mean_squared_error(y_test, y_pred)))
                    , "r2_score": float(r2_score(y_test, y_pred))
                }
            else:
                model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                metrics = {
                    "accuracy"  : float(accuracy_score(y_test, y_pred))
                }

            feature_importance = dict(zip(feature_columns, model.feature_importances_.tolist()))

            model_dir = Path("output/models")
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = str(model_dir / f"random_forest_{task_type}.pkl")
            joblib.dump(model, model_path)

            logger.info(f"Random Forest {task_type} trained")

            return {
                "status"    : 200
                , "message" : "Model trained successfully"
                , "data"    : {
                    "model_type"            : f"Random Forest {task_type.title()}"
                    , "n_estimators"        : n_estimators
                    , "metrics"             : metrics
                    , "feature_importance"  : feature_importance
                    , "model_path"          : model_path
                }
            }

        except Exception as e:
            logger.error(f"Error training random forest: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to train model: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("make_prediction")
    async def make_prediction(
        model_path  : str
        , input_data: Dict[str, float]
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Make prediction using trained model

        Args:
            model_path  : Path to saved model
            input_data  : Dict of feature values

        Returns:
            Dict with prediction
        """
        try:
            model = joblib.load(model_path)

            features = pd.DataFrame([input_data])
            prediction = model.predict(features)

            return {
                "status"    : 200
                , "message" : "Prediction made"
                , "data"    : {
                    "prediction": float(prediction[0])
                    , "input"   : input_data
                }
            }

        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to predict: {str(e)}"
                , "data"    : None
            }
