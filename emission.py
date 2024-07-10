#Collab link - https://colab.research.google.com/drive/11yjy74FsLn8z_dHt5ywr5oO2j7XUnYiM?usp=sharing
## Below one is the code that we have downloded from Collab
"""emission.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11yjy74FsLn8z_dHt5ywr5oO2j7XUnYiM
"""

from google.colab import drive
drive.mount('/content/drive')

# importing required libraries
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
from sklearn import tree
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn import linear_model

data = pd.read_csv('/content/drive/MyDrive/CO2 Emissions_Canada.csv')

data.shape

"""# Data Exploration"""

# Count the occurrences of each category in the 'Make' column
value_counts = data['Make'].value_counts()

# Set the size of the figure
plt.figure(figsize=(20, 6))

# Create a bar plot
plt.bar(value_counts.index, value_counts)

# Set labels and title
plt.xlabel('Make')
plt.ylabel('Count')
plt.title('Bar Plot of Make')
plt.xticks(rotation='vertical')

# Display the plot
plt.show()

"""The above bar plot shows the number of vehicles manufactured by each company."""

# Create a figure and axis object
fig, ax = plt.subplots(figsize=(15, 8))

# Plot the boxplot
sns.boxplot(x="Make", y="CO2 Emissions(g/km)", data=data, ax=ax)

# Rotate x-axis labels
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

# Show the plot
plt.show()

"""From the above plot, we can see that, luxury cars tend to produce higher emission levels."""

# Set the size of the figure
plt.figure(figsize=(12, 8))

# Create a histogram with different colors for each category of 'Cylinders'
sns.histplot(data=data, x='CO2 Emissions(g/km)', hue='Cylinders', alpha=0.5)
plt.xlabel('CO2 Emissions(g/km)')
plt.ylabel('Frequency')
plt.title('Histogram of CO2 Emissions by Cylinders')

# Display the plot
plt.show()

"""Based on the histogram:
* Most data points are concentrated in the 200-300 range of CO2 emissions.
* There's a correlation between higher cylinder counts and increased CO2 emissions.
"""

# Set the size of the figure
plt.figure(figsize=(15, 10))

# Create a box plot for 'CO2 Emissions(g/km)' grouped by 'Cylinders'
sns.boxplot(data=data, x='Cylinders', y='CO2 Emissions(g/km)')

# Set labels and title
plt.xlabel('Cylinders')
plt.ylabel('CO2 Emissions(g/km)')
plt.title('Box Plot of CO2 Emissions by Cylinders')

# Display the plot
plt.show()

"""From the above boxplot, we can see that, as the number of cylinders increase, there is also increase in the emissions of CO2 from vehicle which indicates a positive correlation between the "Cylinders" and "CO2 Emissions"

# Feature Selection

We select only the columns we believe are useful for predicting emissions. We exclude columns like Make and Model because they have many categories and are less likely to impact our model's accuracy.
"""

df = data.loc[:, ['Engine Size(L)',
                     'Cylinders',
                     'Fuel Consumption City (L/100 km)',
                     'Fuel Consumption Hwy (L/100 km)',
                     'Fuel Consumption Comb (L/100 km)',
                     'Fuel Consumption Comb (mpg)',
                     'CO2 Emissions(g/km)']]

df

df.isnull().sum()

"""There are no null values in the data"""

# Define mapping dictionaries
strip_digits = {ord(char): None for char in '01456789'}
gear_change = {ord(char): None for char in 'AMVS'}

# Apply transformations
gears = [int(x.translate(gear_change)) if x.translate(gear_change) else np.nan for x in data['Transmission']]
transm = [x.translate(strip_digits) for x in data['Transmission']]

# Create DataFrame with new columns
df['Gears'] = pd.Series(gears).fillna(pd.Series(gears).mode()[0])
df['Transmission'] = pd.Series(transm)

df

fuel_type_encoded = pd.get_dummies(data['Fuel Type'], prefix='FT', dtype='int')
transmission_encoded = pd.get_dummies(df['Transmission'], prefix='Transmission', dtype='int')

df_X = pd.concat([df, fuel_type_encoded, transmission_encoded], axis=1)
df_y = df['CO2 Emissions(g/km)']

df_X.drop(['CO2 Emissions(g/km)', 'Transmission'], axis=1, inplace=True)
df_X.head()

# Select only numeric columns from the DataFrame
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
corr_matrix = df[numeric_columns].corr()
plt.figure(figsize=(5,5))
sns.heatmap(corr_matrix, vmin=-1, vmax=1, annot=True)
plt.title("Correlation Heatmap", fontsize=15, fontweight="bold")
plt.show()

"""From the above correlation heatmap, we can see that except "Gears" (probably because "Gears" is derived from a categorical feature "Transmission") features all the other variables are highly correlated. Specifically,  "Engine Size (L)", "Cylinders", "Fuel Consumption City (L/100 km)", "Fuel Consumption Hwy (L/100 km)", "Fuel Consumption Comb (L/100 km)" are highly positively correlated with the "CO2 Emissions(g/km)" and "Fuel Consumption Comb (mpg)" is highly negatively correlated with "CO2 Emissions(g/km)"
"""

print(df_X.shape)
df_X.head()

df_y.head()

"""# PCA"""

from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt

# Apply PCA with 10 components
pca_X = PCA(n_components=10)
pc_X = pca_X.fit_transform(df_X)

# Calculate and print the cumulative sum values for each Principal Component
cumulative_variance_ratio = np.cumsum(pca_X.explained_variance_ratio_) * 100
print(cumulative_variance_ratio)

# Create a bar plot showing the ratio of variance explained by each Principal Component
plt.figure(figsize=(10, 8))
sns.barplot(x=np.arange(1, 11), y=pca_X.explained_variance_ratio_.round(3), color="b")

# Add labels to the bars with the variance explained ratios
for index, value in enumerate(pca_X.explained_variance_ratio_.round(3)):
    plt.text(index, value, str(value), ha='center', va='bottom')

plt.title('Ratio of Variance Explained by PCs')
plt.xlabel('Principal Component')
plt.ylabel('Ratio of Variance explained')
plt.show()

# Store the transformed components
pc_df = pd.DataFrame(data=pc_X)
pc_df.head()

X = pc_df.iloc[:,:5].values

y = df['CO2 Emissions(g/km)']

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=36)

result_df = pd.DataFrame(columns=["Model", "R2 Score", "Adjusted R2", "RMSE", "MAE"])

n = len(y_test)
p = x_test.shape[1]

# Linear Regression
linear_reg=LinearRegression()
linear_reg.fit(x_train, y_train)
y_pred = linear_reg.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Linear Regression_PCA', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Linear Regression_PCA")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

knn_rmse = []
for K in range(1, 30):
    model = KNeighborsRegressor(n_neighbors = K)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    knn_rmse.append(rmse)
plt.plot(range(1, 30), knn_rmse)
plt.title('RMSE for various values of K (Neighbours)_PCA')
plt.xlabel('K - Neighbours_PCA')
plt.ylabel('RMSE')
plt.show()

# KNN Regressor
knn = KNeighborsRegressor(n_neighbors=3, weights = 'distance', algorithm = 'brute')
knn.fit(x_train,y_train)
y_pred = knn.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['KNN Regressor_PCA', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("KNN Regressor_PCA")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

params = {'criterion' : ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
          'splitter' : ['best', 'random'],
          'max_depth' : [i for i in range(1,5)],
          'max_features' : ['auto', 'sqrt', 'log2'],
          'random_state' : [i for i in range(0,10)]}
dtr = tree.DecisionTreeRegressor()
model = GridSearchCV(dtr, params, scoring = 'neg_mean_squared_error')
model.fit(x_train,y_train)
model.best_params_

# Decision Tree Regressor
dtr = tree.DecisionTreeRegressor(criterion='squared_error', max_depth=4, max_features='auto', random_state=3, splitter='best')
dtr = dtr.fit(x_train, y_train)
y_pred = dtr.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Decision Tree Regressor_PCA', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Decision Tree Regressor_PCA")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

params = {'kernel' :['linear', 'poly', 'rbf']}
svr = SVR()
model = GridSearchCV(svr, params, scoring = 'neg_mean_squared_error')
model.fit(x_train,y_train)
model.best_params_

# Support Vector Regressor
svr = SVR(kernel='rbf')
svr.fit(x_train,y_train)
y_pred = svr.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Support Vector Regressor_PCA', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Support Vector Regressor_PCA")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

plt.figure(figsize=(8,6))
plt.bar(x = result_df['Model'][:4], height = result_df['Adjusted R2'][:4])
plt.title("Comparison of Adjusted R2 Score for different Models_PCA")
plt.xlabel("Model")
plt.ylabel("Adjusted R2 Score")
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(8,6))
plt.bar(x = result_df['Model'], height = result_df['RMSE'])
plt.title("Comparison of RMSE for different Models_PCA")
plt.xlabel("Model")
plt.ylabel("RMSE")
plt.xticks(rotation=45)
plt.show()

df_X.head()

df_y.head()

#splitting the train and test data
x_train, x_test, y_train, y_test = train_test_split(df_X, df_y, test_size=0.25, random_state=36)

# Linear Regression
linear_reg=LinearRegression()
linear_reg.fit(x_train, y_train)
y_pred = linear_reg.predict(x_test)

n = len(y_test)
p = x_test.shape[1]

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Linear Regression', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Linear Regression")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

x_test.columns

knn_rmse = []
for K in range(1, 30):
    model = KNeighborsRegressor(n_neighbors = K)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    knn_rmse.append(rmse)
plt.plot(range(1, 30), knn_rmse)
plt.title('RMSE for various values of K (Neighbours)')
plt.xlabel('K - Neighbours')
plt.ylabel('RMSE')
plt.show()

# KNN Regressor
knn = KNeighborsRegressor(n_neighbors=3, weights = 'distance', algorithm = 'brute')
knn.fit(x_train,y_train)
y_pred = knn.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['KNN Regressor', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("KNN Regressor")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

params = {'criterion' : ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
          'splitter' : ['best', 'random'],
          'max_depth' : [i for i in range(1,5)],
          'max_features' : ['auto', 'sqrt', 'log2'],
          'random_state' : [i for i in range(0,10)]}
dtr = tree.DecisionTreeRegressor()
model = GridSearchCV(dtr, params, scoring = 'neg_mean_squared_error')
model.fit(x_train,y_train)
model.best_params_

# Decision Tree Regressor
dtr = tree.DecisionTreeRegressor(criterion='squared_error', max_depth=4, max_features='auto', random_state=0, splitter='best')
dtr = dtr.fit(x_train, y_train)
y_pred = dtr.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Decision Tree Regressor', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Decision Tree Regressor")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

params = {'kernel' :['linear', 'poly', 'rbf']}
svr = SVR()
model = GridSearchCV(svr, params, scoring = 'neg_mean_squared_error')
model.fit(x_train,y_train)
model.best_params_

# Support Vector Regressor
svr = SVR(kernel='linear')
svr.fit(x_train,y_train)
y_pred = svr.predict(x_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
adjusted_r2 = 1 - ((1 - r2) * (n - 1)) / (n - p - 1)

result_df.loc[len(result_df)] = ['Support Vector Regressor', round(r2,4), round(adjusted_r2,4), round(rmse,4), round(mae,4)]

print("Support Vector Regressor")
print("R2 Score: ", round(r2,4))
print("Adjusted R2 Score:", round(adjusted_r2,4))
print("RMSE: ", round(rmse,4))
print("MAE: ", round(mae,4))

result_df

plt.figure(figsize=(8,6))
plt.bar(x = result_df['Model'][4:], height = result_df['Adjusted R2'][4:])
plt.title("Comparison of Adjusted R2 Score for different Models")
plt.xlabel("Model")
plt.ylabel("Adjusted R2")
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(8,6))
plt.bar(x = result_df['Model'][4:], height = result_df['RMSE'][4:])
plt.title("Comparison of RMSE for different Models")
plt.xlabel("Model")
plt.ylabel("RMSE")
plt.xticks(rotation=45)
plt.show()

def plot_metric_comparison(model1_name, model2_name, metric, result_df):
    metric_scores = [
        result_df[result_df['Model'] == model1_name][metric].values[0],
        result_df[result_df['Model'] == model2_name][metric].values[0]
    ]
    models = [model1_name, model2_name]

    plt.figure(figsize=(5, 4))
    plt.bar(models, metric_scores, color=['blue', 'orange'])
    plt.xlabel('Models')
    plt.ylabel(metric)
    plt.title(f'Comparison of {model1_name} and {model2_name} ({metric} Score)')
    plt.ylim(0, max(metric_scores) * 1.1)
    plt.show()

plot_metric_comparison('Linear Regression_PCA', 'Linear Regression', 'Adjusted R2', result_df)

plot_metric_comparison('Linear Regression_PCA', 'Linear Regression', 'R2 Score', result_df)

plot_metric_comparison('Linear Regression_PCA', 'Linear Regression', 'RMSE', result_df)

plot_metric_comparison('Linear Regression_PCA', 'Linear Regression', 'MAE', result_df)

plot_metric_comparison('Support Vector Regressor_PCA', 'Support Vector Regressor', 'Adjusted R2', result_df)

