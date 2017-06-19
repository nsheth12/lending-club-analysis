# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:56:59 2017

@author: Nihar Sheth
"""

import pandas as pd
import numpy as np
import matplotlib as plt

extraneous_cols = ["out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
                   "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d", "collections_12_mths_ex_med", "acc_now_delinq",
                   "tot_coll_amt", "tot_cur_bal", "total_rev_hi_lim", "acc_open_past_24mths", "avg_cur_bal", "bc_open_to_buy", "bc_util", "chargeoff_within_12_mths",
                   "delinq_amnt", "mo_sin_old_il_acct", "mo_sin_old_rev_tl_op", "mo_sin_rcnt_rev_tl_op", "mo_sin_rcnt_tl", "tot_hi_cred_lim", "total_bal_ex_mort", "total_bc_limit", "total_il_high_credit_limit"]

#read in loan data from CSV file
#lc1 = pd.read_csv("C:/Nihar/Finance/LC_2007_2011_loan_data.csv")
lc = pd.read_csv("C:/Nihar/Finance/LC_2012_2013_loan_data.csv")

#lc = pd.concat([lc1, lc2])

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
    return len(col.unique()) == 1

#standardize loan statuses so they are either "on time" or "late"
def generalize_loan_status (loan_status):
    if loan_status == "Fully Paid" or loan_status == "Current":
        return "On Time"
    return "Late"
    
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

#lc = lc.dropna(axis = 1, how = "all") #drop all columns that are completely null
lc = deleteColsWithMatchingCond(notEnoughCoverage, lc)
lc = lc.dropna() #drop any rows with NaN vals (this is a temp solution) TODO: better solution needed
lc = deleteColsWithMatchingCond(isColAllSame, lc) #drop any columns where all values are the same                           

del lc["initial_list_status"]
del lc["funded_amnt"]
del lc["funded_amnt_inv"]
del lc["emp_title"] #so many possible values, so unf, not possible to use
del lc["pymnt_plan"] #not enough "y" to justify this being a column
del lc["zip_code"] #since zip code has two digits missing, it's basically useless
                               
payment_data = lc.loc[:, extraneous_cols]

lc.drop(extraneous_cols, axis=1, inplace=True)

#weird loan statuses that need to be replaced in the data, using str.replace which is vectorized
#string function
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Fully Paid", "Fully Paid")
lc["loan_status"] = lc["loan_status"].str.replace("Does not meet the credit policy. Status:Charged Off", "Charged Off")

lc["term"] = lc["term"].map({" 36 months" : 36, " 60 months" : 60}).astype(int) #convert term to ints
lc["int_rate"] = lc["int_rate"].apply(lambda x : float(str(x)[:-1])) #convert int rate string to float
lc["emp_length"] = lc["emp_length"].apply(convertEmploymentLength)
  
#map unique loan statuses into "on time" or "late"
lc["gen_loan_status"] = lc["loan_status"].map(generalize_loan_status)

#sample query
#lc.loc[lc["grade"] == "A"]["loan_status"].value_counts().plot(kind="bar")
#lc["gen_loan_status"].value_counts().plot(kind="bar")