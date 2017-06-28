import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import KFold
import preprocessor

payment_cols = ["out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
                   "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d", "collections_12_mths_ex_med", "acc_now_delinq",
                   "tot_coll_amt", "tot_cur_bal", "total_rev_hi_lim", "acc_open_past_24mths", "avg_cur_bal", "bc_open_to_buy", "bc_util", "chargeoff_within_12_mths",
                   "delinq_amnt", "mo_sin_old_il_acct", "mo_sin_old_rev_tl_op", "mo_sin_rcnt_rev_tl_op", "mo_sin_rcnt_tl", "tot_hi_cred_lim",
                   "total_bal_ex_mort", "total_bc_limit", "total_il_high_credit_limit", "grade"]

#standardize loan statuses so they are either "on time" or "late"
def generalize_loan_status (loan_status):
    if loan_status == "Fully Paid" or loan_status == "Current":
        return 1
    return 0

lc = preprocessor.loadData(["C:/Nihar/Finance/LC_2007_2011_loan_data.csv",
                            "C:/Nihar/Finance/LC_2012_2013_loan_data.csv",
                            "C:/Nihar/Finance/LC_2014_loan_data.csv"])
lc = preprocessor.preprocess(lc)
                               
payment_data = lc.loc[:, payment_cols]
lc.drop(payment_cols, axis=1, inplace=True)
lc.drop("issue_date", axis=1, inplace=True) #drop issue date column

#create dummy variables for categorical variables
lc = pd.concat([lc, pd.get_dummies(lc["home_ownership"], prefix="home")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["verification_status"], prefix="verif")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["purpose"], prefix="purpose")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["sub_grade"], prefix="sub_grade")], axis=1)

lc.drop(["home_ownership", "verification_status", "purpose", "sub_grade"], axis=1, inplace=True)
  
##map unique loan statuses into "on time" or "late"
#lc["gen_loan_status"] = lc["loan_status"].map(generalize_loan_status)
#lc.drop("loan_status", axis=1, inplace=True) #now we don't need this anymore

#based on code at https://github.com/savarin/pyconuk-introtutorial
       
#reorder columns so variable being predicted is in first column
cols = lc.columns.tolist()
cols.insert(0, cols.pop(cols.index('total_return')))
lc = lc.loc[:, cols]

data = lc.values
X = data[:, 1:]
y = data[:, 0]

cv = KFold(n=len(data), n_folds=8)

for training_set, test_set in cv:
    X_train = X[training_set]
    y_train = y[training_set]
    X_test = X[test_set]
    y_test = y[test_set]
    model = RandomForestRegressor(n_estimators=100, n_jobs=4)
    model.fit(X_train, y_train)
    
    y_prediction = model.predict(X_test)
    
    runningSum = 0.0
    runningCount = 0
    for idx, val in enumerate(y_prediction):
        if val >= 1.1:
            runningSum += y_test[idx]
            runningCount += 1
    print("Return: ", runningSum / runningCount)
    
#    print("Actual: ", y_test[0], " ; Predicted: ", y_prediction[0])
#    print("Actual: ", y_test[1], " ; Predicted: ", y_prediction[1])
#    print("Actual: ", y_test[2], " ; Predicted: ", y_prediction[2])
    #print("prediction accuracy:", np.sum(y_test == y_prediction)*1./len(y_test))