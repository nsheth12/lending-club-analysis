# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:56:59 2017

@author: Nihar Sheth
"""

import pandas as pd
import numpy as np
import matplotlib as plt
from datetime import datetime

payment_cols = ["out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
                   "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d", "collections_12_mths_ex_med", "acc_now_delinq",
                   "tot_coll_amt", "tot_cur_bal", "total_rev_hi_lim", "acc_open_past_24mths", "avg_cur_bal", "bc_open_to_buy", "bc_util", "chargeoff_within_12_mths",
                   "delinq_amnt", "mo_sin_old_il_acct", "mo_sin_old_rev_tl_op", "mo_sin_rcnt_rev_tl_op", "mo_sin_rcnt_tl", "tot_hi_cred_lim", "total_bal_ex_mort", "total_bc_limit", "total_il_high_credit_limit"]

extraneous_cols = ["initial_list_status", "funded_amnt", "funded_amnt_inv", "emp_title", "pymnt_plan", "zip_code", "title", "addr_state", "grade", "earliest_cr_line"] #few factors here that I'd like to include eventually

#read in loan data from CSV file
lc1 = pd.read_csv("C:/Nihar/Finance/LC_2007_2011_loan_data.csv")
lc2 = pd.read_csv("C:/Nihar/Finance/LC_2012_2013_loan_data.csv")

lc = pd.concat([lc1, lc2])

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

#standardize loan statuses so they are either "on time" or "late"
def generalize_loan_status (loan_status):
    if loan_status == "Fully Paid" or loan_status == "Current":
        return 1
    return 0
    
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

#returns approximation of months from issue to present date
def monthsSinceIssue (stringIssueDate):
    return int((datetime.now().date() - datetime.strptime(stringIssueDate, "%b-%y").date()).days / 30) + 1

#lc = lc.dropna(axis = 1, how = "all") #drop all columns that are completely null
lc = deleteColsWithMatchingCond(notEnoughCoverage, lc)
lc = lc.dropna() #drop any rows with NaN vals (this is a temp solution) TODO: better solution needed
lc = deleteColsWithMatchingCond(isColAllSame, lc) #drop any columns where all values are the same                           

lc.drop(extraneous_cols, axis=1, inplace=True)
                               
payment_data = lc.loc[:, payment_cols]
lc.drop(payment_cols, axis=1, inplace=True)

#weird loan statuses that need to be replaced in the data, using str.replace which is vectorized
#string function
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Fully Paid", "Fully Paid")
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Charged Off", "Charged Off")

lc["term"] = lc["term"].map({" 36 months" : 36, " 60 months" : 60}).astype(int) #convert term to ints
lc["int_rate"] = lc["int_rate"].apply(lambda x : float(str(x)[:-1])) #convert int rate string to float
lc["revol_util"] = lc["revol_util"].apply(lambda x : float(str(x)[:-1])) #convert string to float
lc["emp_length"] = lc["emp_length"].apply(convertEmploymentLength)

#take out loans that haven't matured yet, since we only want matured loans
#there's gotta be a better way to do this
shortTerm = lc.apply(lambda row : monthsSinceIssue(row["issue_d"]) < row["term"], axis=1)
lc.drop(shortTerm[shortTerm].index, inplace=True)
lc.drop("issue_d", axis=1, inplace=True) #now we don't need this anymore

#create dummy variables for categorical variables
lc = pd.concat([lc, pd.get_dummies(lc["home_ownership"], prefix="home")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["verification_status"], prefix="verif")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["purpose"], prefix="purpose")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["sub_grade"], prefix="sub_grade")], axis=1)

lc.drop(["home_ownership", "verification_status", "purpose", "sub_grade"], axis=1, inplace=True)
  
#map unique loan statuses into "on time" or "late"
lc["gen_loan_status"] = lc["loan_status"].map(generalize_loan_status)
lc.drop("loan_status", axis=1, inplace=True) #now we don't need this anymore

#sample query
#lc.loc[lc["grade"] == "A"]["loan_status"].value_counts().plot(kind="bar")
#lc["gen_loan_status"].value_counts().plot(kind="bar")