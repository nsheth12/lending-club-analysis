# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 21:47:19 2017

@author: nsheth
"""

import pandas as pd
from datetime import datetime
import numpy as np

extraneous_cols = ["initial_list_status", "loan_amnt", "funded_amnt_inv", "emp_title",
                   "pymnt_plan", "zip_code", "title", "addr_state", "earliest_cr_line",
                   "loan_status"] #few factors here that I'd like to include eventually

important_cols = ["annual_inc", "verification_status", "term", "home_ownership",
                  "int_rate", "grade", "sub_grade", "issue_d", "emp_length",
                  "funded_amnt", "total_pymnt"] #add back delinq_2yrs, dti, inq_last_6mths

#returns approximation of months from issue to present date
def monthsSinceIssue (issueDate):
#    if issueDate.month == 12 and issueDate.year == 2013:
#        print(int((datetime.now().date() - issueDate).days / 30) + 1)
    return int((datetime.now().date() - issueDate).days / 30) + 1

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
    lc = lc.dropna(how = "any", subset = important_cols)
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

#must have run replacements() first+
def fillnas (lc):
    return lc.apply(lambda x: x.fillna(x.median()) if x.dtype.kind in "biufc" else x)
  
#take out loans that haven't matured yet, since we only want matured loans
#must have run replacements(), fillnas() first 
def keepVintages (lc):
    lc["issue_date"] = lc["issue_d"].apply(lambda dateStr : datetime.strptime(dateStr, "%b-%y").date())
    #longTerm = lc.apply(lambda row : print(row.name, " ", row["issue_date"], " ", row["term"],  " ", monthsSinceIssue(row["issue_date"]) >= row["term"]), axis=1)
    longTerm = lc.apply(lambda row : monthsSinceIssue(row["issue_date"]) >= row["term"], axis=1)
    #somehow this is dropping valid 2007 loans when the 2012-2013 data set is added in
    #lc.drop(shortTerm[shortTerm].index, inplace=True)
    #print(min(longTerm[longTerm == True].index))
    lc = lc.ix[longTerm[longTerm == True].index.tolist()]
    #lc = lc.loc[longTerm[longTerm == True].index, :]
    lc.drop("issue_d", axis=1, inplace=True) #now we don't need this anymore
    return lc

#calculate the return on investment for each loan, relies on the fact that loans are matured
def calcReturns (lc):
    #take into account the 1% fee
    lc["total_return"] = lc.apply(lambda row : row["total_pymnt"]*0.99 / row["funded_amnt"], axis=1)
    return lc
    
#combine all these preprocessing steps into one    
def preprocess (lc):
    lc = dropExtraCols(lc)
    lc = replacements(lc)
    lc = fillnas(lc)
    lc = keepVintages(lc)
    lc = calcReturns(lc)
    return lc