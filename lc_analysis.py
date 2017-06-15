# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:56:59 2017

@author: Nihar Sheth
"""

import pandas as pd
import numpy as np
import matplotlib as plt

#read in loan data from CSV file
lc = pd.read_csv("C:/Nihar/Finance/LC_2007_2011_loan_data.csv")

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

def isColAllSame (col):
    if len(col.unique()) == 1:
        return True
    return False

lc = lc.dropna(axis = 1, how = "all") #drop all columns that are completely null
lc = lc.dropna(subset = ["policy_code"]) #drop any rows with NaN vals where they shouldn't be
lc = deleteColsWithMatchingCond(isColAllSame, lc) #drop any columns where all values are the same
