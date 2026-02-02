# Credit Card Approval Prediction

## Problem

Build a machine learning model that predicts whether a credit card application will be approved based on applicant attributes.

## Why machine learning

Approval decisions depend on multiple applicant features that interact in non-linear ways. A supervised ML classifier can learn these patterns from historical labeled examples and generalize to new applications.

## Dataset

Source: Kaggle – Credit Card Application dataset  
Location:

- Kaggle page: <https://www.kaggle.com/datasets/nazishjaveed/credit-card-application/data>
- File used: Credit_Card_Applications.csv

## Project structure

- backend/ : Flask API (serves the model for prediction)
- frontend/ : React UI (calls the API for predictions)

## Notes

- The dataset file is not committed to the repository.
- Anyone reproducing this project should download the dataset from Kaggle and place it locally as described in the README for later steps.
