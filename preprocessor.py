# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 21:47:19 2017

@author: nsheth
"""

import pandas as pd
from datetime import datetime
import numpy as np
import os

pd.options.mode.chained_assignment = None  # default='warn', gets rid of annoying warnings

def validate_csv_file (filename):
	with open(filename, "r") as f:
		first_row = next(f)
		if first_row.startswith("Notes offered"):
			return False
		return True

def preprocess_csv_file (filename):
	if validate_csv_file(filename) == True:
		return

	with open(filename, "r") as original, open((filename + "1"), "w") as updated:
		next(original)
		for line in original:
			updated.write(line)
	os.remove(filename)
	os.rename((filename + "1"), filename)

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

#load data out of CSV files
#files should not have been modified by Mac Excel
def loadData (files, extraneous_cols):
	dfs = []
	for file in files:
		preprocess_csv_file(file)

		# low_memory option gets rid of annoying warning
		# don't include extraneous_cols
		dfs.append(pd.read_csv(file, low_memory = False, usecols = lambda col : col not in extraneous_cols))
	return pd.concat(dfs)

#drop extra columns that aren't necessary or important
def dropExtraCols (lc, important_cols):
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
	
	if "int_rate" in lc.columns:
		#convert int rate string to float
		lc["int_rate"] = lc["int_rate"].apply(convertPercStrToFloat)

	if "revol_util" in lc.columns:
		lc["revol_util"] = lc["revol_util"].apply(convertPercStrToFloat)

	if "term" in lc.columns:
		#convert term to ints
		lc["term"] = lc["term"].map({" 36 months" : 36, " 60 months" : 60}).astype(int)

	if "emp_length" in lc.columns:
		#convert employment length to continuous variable
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
	lc = lc.loc[longTerm[longTerm == True].index.tolist()]
	lc.drop("issue_d", axis=1, inplace=True) #now we don't need this anymore
	return lc

#calculate the return on investment for each loan, relies on the fact that loans are matured
def calcReturns (lc):
	#take into account the 1% fee
	lc["total_return"] = lc.apply(lambda row : row["total_pymnt"]*0.99 / row["funded_amnt"], axis=1)
	return lc
	
#combine all these preprocessing steps into one    
def preprocess (lc):
	#since different files are merged, there are duplicate indexes, this flattens it out
	lc.reset_index(drop = True, inplace = True)
	lc = dropExtraCols(lc)
	lc = replacements(lc)
	lc = fillnas(lc)
	lc = keepVintages(lc)
	lc = calcReturns(lc)
	return lc

if __name__ == "__main__":
	#lc = loadData(["data/LC_2015_loan_data.csv"])
	#print(lc.shape)
	#print(lc.columns.tolist())
	preprocess_csv_file("data/LC_2007_2011_loan_data.csv")