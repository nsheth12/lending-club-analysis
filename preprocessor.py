# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 21:47:19 2017

@author: nsheth
"""

import pandas as pd
from datetime import datetime
import numpy as np

extraneous_cols = ["initial_list_status", "loan_amnt", "funded_amnt_inv", "emp_title", "pymnt_plan", "zip_code", "title", "addr_state", "earliest_cr_line", "loan_status"] #few factors here that I'd like to include eventually

#returns approximation of months from issue to present date
def monthsSinceIssue (stringIssueDate):
    return int((datetime.now().date() - datetime.strptime(stringIssueDate, "%b-%y").date()).days / 30) + 1

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
    return len(col.unique()) == 1

def notEnoughCoverage (col):
    return col.isnull().sum() / len(col) >= 0.5

def convertEmploymentLength (value):
    if value == "10+ years":
        return 10
    elif value == "< 1 year":
        return 0
    elif value == "1 year":
        return 1
    elif value == "n/a":
        return 0
    else:
        return int(value[0])

def convertPercStrToFloat (x):
    try:
        return float(str(x)[:-1])
    except:
        return np.NaN

def loadData (files):
    dfs = []
    for file in files:
        dfs.append(pd.read_csv(file))
    return pd.concat(dfs)

def dropExtraCols (lc):
    lc.drop(extraneous_cols, axis=1, inplace=True)
    lc = deleteColsWithMatchingCond(notEnoughCoverage, lc)
    
    #make sure the super-important variables are present
    lc = lc.dropna(how = "any", subset = ["annual_inc", "verification_status", "delinq_2yrs", "dti",
                                          "inq_last_6mths", "installment", "term", "home_ownership",
                                          "int_rate", "grade", "sub_grade", "issue_d", "emp_length",
                                          "funded_amnt", "total_pymnt"])
    lc = deleteColsWithMatchingCond(isColAllSame, lc) #drop any columns where all values are the same
    return lc

def replacements (lc):
    #weird loan statuses that need to be replaced in the data, using str.replace which is vectorized
    #string function
    #lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Fully Paid", "Fully Paid")
    #lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Charged Off", "Charged Off")
    
    lc["int_rate"] = lc["int_rate"].apply(convertPercStrToFloat) #convert int rate string to float
    lc["revol_util"] = lc["revol_util"].apply(convertPercStrToFloat) #convert string to float
    lc["term"] = lc["term"].map({" 36 months" : 36, " 60 months" : 60}).astype(int) #convert term to ints
    lc["emp_length"] = lc["emp_length"].apply(convertEmploymentLength)
    return lc

#must have run replacements() first
def fillnas (lc):
    return lc.apply(lambda x: x.fillna(x.median()) if x.dtype.kind in "biufc" else x)
  
#take out loans that haven't matured yet, since we only want matured loans
#must have run replacements(), fillnas() first 
def keepVintages (lc):
    shortTerm = lc.apply(lambda row : monthsSinceIssue(row["issue_d"]) < row["term"], axis=1)
    lc.drop(shortTerm[shortTerm].index, inplace=True)
    lc.drop("issue_d", axis=1, inplace=True) #now we don't need this anymore
    return lc

#calculate the return on investment for each loan, relies on the fact that loans are matured
def calcReturns (lc):
    lc["total_return"] = lc.apply(lambda row : row["total_pymnt"] / row["funded_amnt"], axis=1)
    return lc
    
#combine all these preprocessing steps into one    
def preprocess (lc):
    lc = dropExtraCols(lc)
    lc = replacements(lc)
    lc = fillnas(lc)
    lc = keepVintages(lc)
    lc = calcReturns(lc)
    return lc