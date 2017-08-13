import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import preprocessor

payment_cols = ["out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
				   "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d", "collections_12_mths_ex_med", "acc_now_delinq",
				   "tot_coll_amt", "tot_cur_bal", "total_rev_hi_lim", "acc_open_past_24mths", "avg_cur_bal", "bc_open_to_buy", "bc_util", "chargeoff_within_12_mths",
				   "delinq_amnt", "mo_sin_old_il_acct", "mo_sin_old_rev_tl_op", "mo_sin_rcnt_rev_tl_op", "mo_sin_rcnt_tl", "tot_hi_cred_lim",
				   "total_bal_ex_mort", "total_bc_limit", "total_il_high_credit_limit", "grade"]

lc = preprocessor.loadData(["data/LC_2007_2011_loan_data.csv",
							"data/LC_2012_2013_loan_data.csv",
							"data/LC_2014_loan_data.csv"])
lc = preprocessor.preprocess(lc)

print(lc.shape)
							   
payment_data = lc.loc[:, payment_cols]
lc.drop(payment_cols, axis=1, inplace=True)
lc.drop("issue_date", axis=1, inplace=True) #drop issue date column

#create dummy variables for categorical variables
lc = pd.concat([lc, pd.get_dummies(lc["home_ownership"], prefix="home")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["verification_status"], prefix="verif")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["purpose"], prefix="purpose")], axis=1)
lc = pd.concat([lc, pd.get_dummies(lc["sub_grade"], prefix="sub_grade")], axis=1)

lc.drop(["home_ownership", "verification_status", "purpose", "sub_grade"], axis=1, inplace=True)

#based on code at https://github.com/savarin/pyconuk-introtutorial
	   
#reorder columns so variable being predicted is in first column
cols = lc.columns.tolist()
cols.insert(0, cols.pop(cols.index('total_return')))
lc = lc.loc[:, cols]

data = lc.values
X = data[:, 1:]
y = data[:, 0]

X_train, X_test, y_train, y_test = train_test_split(X, y)
model = RandomForestRegressor(n_estimators=100, n_jobs=8)
model.fit(X_train, y_train)
	
y_prediction = model.predict(X_test)

runningSum = [0.0] * 4
runningCount = [0] * 4
defaultCount = [0] * 4
defaultSum = [0.0] * 4
for idx, val in enumerate(y_prediction):
	if val <= 1:
		runningSum[0] += y_test[idx]
		runningCount[0] += 1
		if y_test[idx] < 1:
			defaultSum[0] += y_test[idx]
			defaultCount[0] += 1
	elif val > 1.1 and val < 1.15:
		runningSum[2] += y_test[idx]
		runningCount[2] += 1
		if y_test[idx] < 1:
			defaultSum[2] += y_test[idx]
			defaultCount[2] += 1
	elif val >= 1.15:
		runningSum[3] += y_test[idx]
		runningCount[3] += 1
		if y_test[idx] < 1:
			defaultSum[3] += y_test[idx]
			defaultCount[3] += 1
	else:
		runningSum[1] += y_test[idx]
		runningCount[1] += 1
		if y_test[idx] < 1:
			defaultSum[1] += y_test[idx]
			defaultCount[1] += 1
			
print("Returns: ", [s / c for s, c in zip(runningSum, runningCount)])
print("Default rates: ", [dc / c for dc, c in zip(defaultCount, runningCount)])
print("Average returns for defaulted loans: ", [ds / dc for ds, dc in zip(defaultSum, defaultCount)])
print()
print("Running sums: ", runningSum)
print("Counts: ", runningCount)
print("Default counts: ", defaultCount)
print("Default sums: ", defaultSum)
	
#    print("Actual: ", y_test[0], " ; Predicted: ", y_prediction[0])
#    print("Actual: ", y_test[1], " ; Predicted: ", y_prediction[1])
#    print("Actual: ", y_test[2], " ; Predicted: ", y_prediction[2])
	#print("prediction accuracy:", np.sum(y_test == y_prediction)*1./len(y_test))