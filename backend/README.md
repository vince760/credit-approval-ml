# Credit Approval Prediction (Credit Risk)

## Problem

Build a machine learning model that predicts whether a credit application should be approved based on applicant and loan attributes (age, income, employment length, loan amount, interest rate, credit history signals, etc.).

## Why machine learning

Approval decisions depend on multiple applicant and loan features that interact in non-linear ways. A supervised ML classifier can learn patterns from historical labeled examples and generalize to new applications.

## Dataset

Source: Kaggle – Credit Risk Dataset (laotse)  
Location:

- Kaggle page: <https://www.kaggle.com/datasets/laotse/credit-risk-dataset>
- File used: credit_risk_dataset.csv

## Target definition

The dataset is labeled for credit risk (default / non-default). This project treats “approval” as the inverse of default risk:

- Model predicts probability of default.
- Application is approved when predicted default probability is below a fixed threshold (used by the API/UI).

## Project structure

- backend/ : Flask API (serves the trained model for prediction)
- frontend/ : React UI (collects applicant + loan inputs and calls the API)
- artifacts/ : model + metrics outputs used by the API

## Notes

- The dataset file is not committed to the repository.
- To reproduce, download the dataset from Kaggle and place it at:
  `data/credit_risk_dataset.csv`
