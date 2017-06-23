# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 22:19:19 2017

@author: nsheth
"""

import preprocessor

def backtest (indexes):
    return lc["total_return"].ix[indexes].mean()

lc = preprocessor.loadData(["C:/Nihar/Finance/LC_2007_2011_loan_data.csv", "C:/Nihar/Finance/LC_2012_2013_loan_data.csv", "C:/Nihar/Finance/LC_2014_loan_data.csv"])
lc = preprocessor.preprocess(lc)

print(backtest(lc[lc["grade"] == "A"].index.tolist()))