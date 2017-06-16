# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:56:59 2017

@author: Nihar Sheth
"""

import pandas as pd
import numpy as np
import matplotlib as plt

#read in loan data from CSV file
lc1 = pd.read_csv("C:/Nihar/Finance/LC_2007_2011_loan_data.csv")
lc2 = pd.read_csv("C:/Nihar/Finance/LC_2012_2013_loan_data.csv")

lc = pd.concat([lc1, lc2])

#get total number of loan entries
totalRows = len(lc.index)

#delete any columns that cause func to return true when passed in
def deleteColsWithMatchingCond (func, df):
    toDelete = df.apply(func) #apply function column by column 
            
    for colName, value in toDelete.iteritems():
        #for each column, if func returns true, delete the column
        if value:
            del df[colName]
    
    return df

#check if all values in dataframe column are the same
def isColAllSame (col):
    if len(col.unique()) == 1:
        return True
    return False

#standardize loan statuses so they are either "on time" or "late"
def generalize_loan_status (loan_status):
    if loan_status == "Fully Paid" or loan_status == "Current":
        return "On Time"
    return "Late"

lc = lc.dropna(axis = 1, how = "all") #drop all columns that are completely null
lc = lc.dropna(subset = ["policy_code"]) #drop any rows with NaN vals where they shouldn't be
lc = deleteColsWithMatchingCond(isColAllSame, lc) #drop any columns where all values are the same

#weird loan statuses that need to be replaced in the data, using str.replace which is vectorized
#string function
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Fully Paid", "Fully Paid")
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Charged Off", "Charged Off")

#map unique loan statuses into "on time" or "late"
lc["gen_loan_status"] = lc["loan_status"].map(generalize_loan_status)

#sample query
#lc.loc[lc["grade"] == "A"]["loan_status"].value_counts().plot(kind="bar")
lc["gen_loan_status"].value_counts().plot(kind="bar")