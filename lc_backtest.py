# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 22:19:19 2017

@author: nsheth
"""

import preprocessor
import pandas as pd
from datetime import datetime

#maybe this should also return the number of samples on which the mean is based, as well as other stats?
def backtest (indexes):
    data = lc["total_return"].ix[indexes]
    mean = data.mean()
    #std = data.std()
    #count = data.count()
    return mean

lc = preprocessor.loadData(["C:/Nihar/Finance/LC_2007_2011_loan_data.csv",
                            "C:/Nihar/Finance/LC_2012_2013_loan_data.csv",
                            "C:/Nihar/Finance/LC_2014_loan_data.csv"])
lc = preprocessor.preprocess(lc)

#print("Source Verified ", backtest(lc[lc["verification_status"] == "Source Verified"].index.tolist()))
#print("Verified ", backtest(lc[lc["verification_status"] == "Verified"].index.tolist()))
#print("Not Verified ", backtest(lc[lc["verification_status"] == "Not Verified"].index.tolist()))

print(pd.pivot_table(lc, index=["grade"], values=["total_return"]))

#print(backtest(lc[(lc["grade"] == "A") & (lc["annual_inc"] > 100000)].index.tolist()))
#print(backtest(lc[lc["grade"] == "A"].index.tolist()))
#print(backtest(lc[lc["grade"] == "C"].index.tolist()))
#print(backtest(lc[lc["grade"] == "D"].index.tolist()))