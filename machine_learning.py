import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
df = pd.read_csv('trial-dataset/records8.csv', index_col=0)
print(df['socialDistance'])

df = df[(df != -1).all(1)]
print(df["socialDistance"])

df = df.drop(columns='No_of_Watchers')
df = df.drop(columns='socialDistance')

columns = ['PRBodySize', 'CommitSize', 'No_of_Files_Changed', 'No_of_Comments', 'timeSpentOnPR', 'repositoryAge','No_of_collaborators', 'No_of_Stars', 'No_of_OpenIssues', 'No_of_followers_Submitter', 'submitterStatus', 'pullrequestDecision']
from sklearn import preprocessing

print(df.describe().transpose())

x = df.values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df = pd.DataFrame(x_scaled, columns=columns)


print(df.describe().transpose())

def rounding(x):
    if x < 0.5:
        return 0
    else:
        return 1


train, test = train_test_split(df, test_size=0.2, random_state=42)
#print(train)
#print(test)
model = LogisticRegression()

X_train = train.iloc[:, 0:-1]
y_train = train['pullrequestDecision']
X_test = test.iloc[:, 0:-1]
y_test = test['pullrequestDecision']

print(X_test.head())
print(y_test.head())
print(model.fit(X=X_train,y=y_train))

y_pred = model.predict(X_test)
#print(model.get_params())


print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))

importance = model.coef_[0]

for i,v in enumerate(importance):
    print('%s & %.5f \\\\' % (columns[i],v))


model = RandomForestClassifier()
model.fit(X=X_train,y=y_train)

y_pred = model.predict(X_test)

print("\n\n\nAccuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))


importance = model.feature_importances_
# summarize feature importance
for i,v in enumerate(importance):
    print('Feature: %s, Score: %.5f' % (columns[i],v))
