import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from imblearn.over_sampling import SMOTE
import mlflow
import mlflow.sklearn
import optuna
import matplotlib
import subprocess
import json

matplotlib.use("Agg")


# Run 'terraform output -json' to get the outputs as JSON
outputs = subprocess.check_output(["terraform", "output", "-json"])
outputs = json.loads(outputs)

mlflow_lb_dns_name = outputs["mlflow_lb_dns_name"]["value"]


def get_or_create_experiment(experiment_name):
    """
    Retrieve the ID of an existing MLflow experiment or create a new one if it doesn't exist.

    This function checks if an experiment with the given name exists within MLflow.
    If it does, the function returns its ID. If not, it creates a new experiment
    with the provided name and returns its ID.

    Parameters:
    - experiment_name (str): Name of the MLflow experiment.

    Returns:
    - str: ID of the existing or newly created MLflow experiment.
    """

    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)


experiment_id = get_or_create_experiment("BankChurners")
mlflow.set_experiment(experiment_id=experiment_id)

# Set the tracking URI to a valid HTTP or HTTPS URI
mlflow.set_tracking_uri(f"http://{mlflow_lb_dns_name}:5000")

df = pd.read_csv(r"data\BankChurners_preprocessed.csv")
# Define the feature matrix X and the target vector y
X = df.drop(["Attrition_Flag"], axis=1)
y = df["Attrition_Flag"]

smote = SMOTE(random_state=42)
X_smote, y_smote = smote.fit_resample(X, y)


X_train, X_test, y_train, y_test = train_test_split(
    X_smote, y_smote, test_size=0.2, random_state=42
)

# Initialize and fit the logistic regression model
logistic_regression = LogisticRegression(random_state=42, max_iter=1000)
logistic_regression.fit(X_train, y_train)

# Make predictions on the test data
y_pred = logistic_regression.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = pd.crosstab(
    y_test, y_pred, rownames=["Actual"], colnames=["Predicted"], margins=True
)
classification_rep = classification_report(y_test, y_pred)

# Calculate FPR, TPR, and Thresholds for ROC curve
fpr, tpr, thresholds = roc_curve(
    y_test, logistic_regression.predict_proba(X_test)[:, 1]
)
roc_auc = auc(fpr, tpr)


def objective(trial):
    # Suggest hyperparameters
    C = trial.suggest_float("C", 1e-6, 1e6, log=True)
    solver = trial.suggest_categorical(
        "solver", ["newton-cg", "lbfgs", "liblinear", "sag", "saga"]
    )

    # Initialize and fit the logistic regression model
    logistic_regression = LogisticRegression(
        C=C, solver=solver, random_state=42, max_iter=1000
    )
    logistic_regression.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = logistic_regression.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)

    # Return the objective value
    return accuracy


# Create a study object and optimize the objective function
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)

# Get the best parameters
best_params = study.best_params

# Train the model with the best parameters
best_model = LogisticRegression(
    C=best_params["C"], solver=best_params["solver"], random_state=42, max_iter=1000
)
best_model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = best_model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

# Log the model
with mlflow.start_run():
    # Log parameters
    mlflow.log_params(best_params)

    # Log accuracy
    mlflow.log_metric("accuracy", accuracy)

    # Log the model
    mlflow.sklearn.log_model(best_model, "model")

    # Register the model
    mlflow.register_model(
        "runs:/{run_id}/model".format(run_id=mlflow.active_run().info.run_id),
        "BankChurners",
    )
