import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.metrics import accuracy_score
pd.set_option('display.max_columns', None)

df = pd.read_csv('trial-dataset/records8.csv', index_col=0)
print(df['socialDistance'])

print(df.describe().transpose())

train, test = train_test_split(df, test_size=0.2, random_state=42)
#print(train)
#print(test)
model = LinearRegression()

X_train = train.iloc[:, 1:12]
y_train = train.iloc[:,13]
X_test = test.iloc[:, 1:12]
y_test = test.iloc[:,13]
print(X_test)
print(y_test)

model.fit(X=X_train,y=y_train)

y_pred = model.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred.round()))
print("Precision:",metrics.precision_score(y_test, y_pred.round()))
print("Recall:",metrics.recall_score(y_test, y_pred.round()))