import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.tree import DecisionTreeRegressor
from sklearn import preprocessing


def p_val(x):
    if x <= 0.0001:
        return "$\leq$ 0.0001"
    elif x <= 0.001:
        return "$\leq$ 0.001"
    elif x <= 0.01:
        return "$\leq$ 0.01"
    elif x <= 0.05:
        return "$\leq$ 0.05"
    else:
        return "$>$ 0.05"



pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


df = pd.read_csv("trial-dataset/records-2015-01-13-23.csv", index_col=0)
# remove all rows where any column has a -1 which indicates a missing value
df = df[(df != -1).all(1)]
# Same as number of number of stars
df = df.drop(columns='No_of_Watchers')
# Value is always 0. Need to look into this further.
df = df.drop(columns='socialDistance')
# Max limit of 30
df = df.drop(columns='No_of_collaborators')
# Max limit of 30
df = df.drop(columns='No_of_followers_Submitter')
#df = df.drop(columns='timeSpentOnPR')
#columns = ['PRBodySize', 'CommitSize', 'No_of_Files_Changed', 'No_of_Comments', 'timeSpentOnPR', 'repositoryAge','No_of_collaborators', 'No_of_Stars', 'No_of_OpenIssues', 'No_of_followers_Submitter', 'submitterStatus', 'pullrequestDecision']

print(df.describe().transpose())

# To normalize the data
# x = df.values #returns a numpy array
# min_max_scaler = preprocessing.MinMaxScaler()
# x_scaled = min_max_scaler.fit_transform(x)
# df = pd.DataFrame(x_scaled, columns=df.columns)
pd.options.display.float_format = '${:,.1f}'.format
print(df.describe().transpose()[['mean', 'std', '25%', '50%', '75%', 'max']].to_latex())

train, test = train_test_split(df, test_size=0.20, random_state=42)
#print(train)
#print(test)


model = LogisticRegression()


X_train = train.iloc[:, 0:-1]
y_train = train['pullrequestDecision']
X_test = test.iloc[:, 0:-1]
y_test = test['pullrequestDecision']

std_scale = preprocessing.MinMaxScaler().fit(X_train)
X_train_std = std_scale.transform(X_train)
X_test_std  = std_scale.transform(X_test)
#print(X_test.head())
#print(y_test.head())
model.fit(X=X_train_std,y=y_train)

y_pred = model.predict(X_test_std)
#print(model.get_params())


print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))

importance = model.coef_[0]

print("\n\n Chi2 test")
from sklearn.feature_selection import chi2
scores, pvalues = chi2(X_train_std, y_train)
#print("pvalues:")
#print(pvalues)
for i,v in enumerate(importance):
    print('%s & %.5f  & %s\\\\' % (df.columns[i],v, p_val(pvalues[i])))


# print("\n\n\n SVC with linear kernel : \n\n")
# model = svm.SVC(kernel='linear')
# model.fit(X=X_train,y=y_train)
#
# y_pred = model.predict(X_test)
# #print(model.get_params())
#
#
# print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
# print("Precision:",metrics.precision_score(y_test, y_pred))
# print("Recall:",metrics.recall_score(y_test, y_pred))
#
# importance = model.coef_[0]
#
# for i,v in enumerate(importance):
#     print('%s & %.5f \\\\' % (df.columns[i],v))



print("\n\n Stat model")
import statsmodels.api as sm
logit_model=sm.Logit(y_train,X_train)
result=logit_model.fit()
print(result.summary())


print("\n\n Stat model")
from sklearn.feature_selection import chi2
scores, pvalues = chi2(X_train_std, y_train)
print("pvalues:")
print(pvalues)
print("scores:")
print(scores)
