# CS-846 Project

Repository selection criteria:

    - Exclude forks
    - Exclude repositories that have no activity in the last 10 days
    - Remove repo that do not have use issue tracker
    - Need min three contributors

## Query.py file 
Conatins script for generating repository lists and also creating 
a dataset of pull request factors.

## machine_learning.py
Uses the pull request factors dataset to train a logistic regression model
and print feature importance scores with p values to check statistical
significance.


