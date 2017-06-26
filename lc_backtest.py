# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 22:19:19 2017

@author: nsheth
"""

import preprocessor
from datetime import datetime

#maybe this should also return the number of samples on which the mean is based, as well as other stats?
def backtest (indexes):
    mean = lc["total_return"].ix[indexes].mean()
    std = lc["total_return"].ix[indexes].std()
    count = lc["total_return"].ix[indexes].count()
    return mean, std, count

lc = preprocessor.loadData([#"C:/Nihar/Finance/LC_2007_2011_loan_data.csv",
                            "C:/Nihar/Finance/LC_2012_2013_loan_data.csv"])
                            #"C:/Nihar/Finance/LC_2014_loan_data.csv"])
lc = preprocessor.preprocess(lc)

#print(lc[lc["issue_date"] < datetime(2008, 1, 1).date()].loc[:, "issue_date", "short_term"].head(30))
#print(lc[(lc["issue_d"] == "Dec-13") & (lc["term"] == 60)])
#print(backtest(lc[(lc["issue_date"] < datetime(2008, 1, 1).date())].index.tolist()))
#print(backtest(lc[(lc["grade"] == "A") & (lc["annual_inc"] > 100000)].index.tolist()))
#print(backtest(lc[lc["grade"] == "A"].index.tolist()))
#print(backtest(lc[lc["grade"] == "C"].index.tolist()))
#print(backtest(lc[lc["grade"] == "D"].index.tolist()))