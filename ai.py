import pandas as pd
import math
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as keras
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

print("making ai rn")
# global variables we could want to change
sequence_length = 6  # time index (seasons)



# somehow we get data
# data; 4 columns, speciesName, monthlySightings, monthIndex, className
data = pd.read_csv("marine_species_data.csv")

# fitting the species data to be normalized 
total_sightings_per_month = data.groupby('monthIndex')['monthlySightings'].transform('sum')
data['monthlySightings'] = data['monthlySightings']/total_sightings_per_month

# getting the month indexes we want via the desired starting years

training_start_year = 1980 # jan 1980
training_end_year = 2015 # dec 2015
training_start_month_index = 0
training_end_month_index = (training_end_year - training_start_year)*12 - 1

validation_start_year = 2016 # jan 2016
validation_end_year = 2020 # dec 2020
validation_start_month_index = training_end_month_index + 1
validation_end_month_index = (validation_end_year - validation_start_year)*12 + training_end_month_index

test_start_year = 2021 # jan 2021
test_end_year = 2025 # jan 2025
test_start_month_index = validation_end_month_index + 1
test_end_month_index = (test_end_year - test_start_year)*12 + validation_end_month_index

# splitting up the test data 
## finding the csv index where each section ends 
datas_index_training_end_month_index = 0
datas_index_validation_end_month_index = 0
datas_index_test_end_month_index = 0

cont = True
i = 0


def find_monthIndex(data, start_monthIndex, end_monthIndex):
    i = start_monthIndex
    while (True): 
        if data.iloc[i,2] == end_monthIndex + 1:
            return i - 1
        i += 1

training_end = find_monthIndex(data, training_start_month_index, training_end_month_index)
validation_end = find_monthIndex(data, validation_start_month_index, validation_end_month_index)
test_end = find_monthIndex(data, test_start_month_index, test_end_month_index)

print(training_end)
print(validation_end)
print(test_end)

            
def get_season(monthIndex):
    monthIndex = monthIndex
    if monthIndex % 12 in [0, 1, 11]: # Dec, Jan, Feb (Winter if starting from Jan as 0, Dec as 11)
        return 0 + 4*math.floor(monthIndex/12)
    elif monthIndex % 12 in [2, 3, 4]: # Mar, Apr, May
        return 1 + 4*math.floor(monthIndex/12)
    elif monthIndex % 12 in [5, 6, 7]: # Jun, Jul, Aug
        return 2 + 4*math.floor(monthIndex/12)
    elif monthIndex % 12 in [8, 9, 10]: # Sep, Oct, Nov
        return 3 + 4*math.floor(monthIndex/12)


def months_to_seasons(data):
    data['seasonIndex'] = data['monthIndex'].apply(get_season)
    seasonal_sightings = data.groupby(['seasonIndex', 'speciesName'])['monthlySightings'].sum().reset_index() # Calculate seasonal sightings

    # Normalize to total sightings per seasonIndex
    total_sightings_per_season = seasonal_sightings.groupby('seasonIndex')['monthlySightings'].transform('sum') # Calculate total per season
    seasonal_sightings['normalizedSightings'] = seasonal_sightings['monthlySightings'] / total_sightings_per_season # Normalize

    seasonal_sightings.rename(columns={'normalizedSightings': 'Sightings'}, inplace=True)
    return seasonal_sightings[['Sightings', 'seasonIndex', 'speciesName']] 

    

data = months_to_seasons(data) 
data.to_csv('test_data.csv', index = False)
training_data = data.iloc[0: round(training_end/4)]
validation_data = data.iloc[round(training_end/4 + 0.25): round(validation_end/4)]
test_data = data.iloc[round(validation_end/4 + 0.25): round(test_end/4)]

# shaping the data

train_sightings = training_data['Sightings'].values.reshape(-1, 1)
validation_sightings = validation_data['Sightings'].values.reshape(-1, 1)
test_sightings = test_data['Sightings'].values.reshape(-1, 1)
all_sightings = data['Sightings'].values.reshape(-1, 1)

scaler = MinMaxScaler(feature_range=(0, 1))
scaler = scaler.fit(all_sightings) 
train_sightings_scaled = scaler.transform(train_sightings)
validation_sightings_scaled = scaler.transform(validation_sightings)
test_sightings_scaled = scaler.transform(test_sightings)

#  function for creating sequences from the data and the sequence length for RNN data

def create_sequences(data, seq_length):

    X = []
    y = []

    for i in range(len(data) - seq_length):

        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    
    return np.array(X), np.array(y) 

X_train, y_train = create_sequences(train_sightings_scaled, sequence_length)
X_validation, y_validation = create_sequences(validation_sightings_scaled, sequence_length)
X_test, y_test = create_sequences(test_sightings_scaled, sequence_length)


##############################################
##############################################
##############################################
##############################################

# reshape input to be [samples, time steps, features] or LSTM to work

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_validation = np.reshape(X_validation, (X_validation.shape[0], X_validation.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))



# 4. Negative Binomial Loss Function
def negative_binomial_nll(y_true, y_pred):
    """
    Negative Binomial Negative Log-Likelihood loss function.
    y_pred should be [mu, alpha] where mu is the mean and alpha is the dispersion parameter.
    """
    mu = y_pred[:, 0] # Predicted mean
    alpha = y_pred[:, 1] # Predicted dispersion
    y_true = tf.squeeze(y_true) # Ensure y_true is 1D

    # Clip alpha to prevent numerical instability, and ensure it's positive
    alpha = tf.clip_by_value(alpha, keras.epsilon(), float('inf')) # Ensure alpha > 0
    mu = tf.clip_by_value(mu, keras.epsilon(), float('inf'))      # Ensure mu > 0


    log_likelihood = tf.math.lgamma(y_true + alpha) - tf.math.lgamma(alpha) - tf.math.lgamma(y_true + 1) + \
                     alpha * tf.math.log(alpha) - alpha * tf.math.log(alpha + mu) + \
                     y_true * tf.math.log(mu) - y_true * tf.math.log(alpha + mu)

    return -keras.mean(log_likelihood) # Negative log-likelihood, we want to minimize this


# lstm
model = Sequential()
# 1st lstm layer 
model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences = True)) # Single LSTM layer with 50 units
model.add(Dropout(0.2))
# 2nd
# model.add(LSTM(50, return_sequences = True))
# model.add(Dropout(0.2))
# 3rd
model.add(LSTM(100))
model.add(Dense(2, activation='exponential')) # Output layer with 2 neurons (mu, alpha), exponential activation to ensure positive outputs

# 6. Compile Model
optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss=negative_binomial_nll) # Use custom NLL loss


# 7. Model Training
epochs = 100 # Adjust as needed
batch_size = 8 # Adjust as needed

history = model.fit(X_train, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_data=(X_validation, y_validation),
                    shuffle=False) # Shuffle False for time series


predictions_scaled = model.predict(X_test)  # Predict mu and alpha (scaled domain if targets were scaled)

# Extract predicted mean (mu) - first output neuron
predicted_mu_scaled = predictions_scaled[:, 0].reshape(-1, 1)

# Inverse transform the scaled predictions to original scale
predicted_sightings = scaler.inverse_transform(predicted_mu_scaled)
actual_sightings = scaler.inverse_transform(y_test)  # Inverse transform actual test values for comparison

from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(actual_sightings, predicted_sightings)
rmse = np.sqrt(mean_squared_error(actual_sightings, predicted_sightings))

print(f'Test Mean Absolute Error (MAE): {mae:.2f}')
print(f'Test Root Mean Squared Error (RMSE): {rmse:.2f}')

## testing prediction
species_name = 'Plagioecia patina'
species_data = data[data['speciesName'] == species_name]
start_index = (2021 - 1980)*4 # winter 2020-2021
amount_of_predictions = 100

data_before_date = species_data[species_data['seasonIndex'] < start_index] 

predicted = []
last_seq_data = data_before_date.tail(sequence_length)['Sightings'].values.reshape(-1, 1)
last_seq_scaled = scaler.transform(last_seq_data)


for i in range(amount_of_predictions):
    
    X_predict = np.reshape(last_seq_scaled, (1, sequence_length, 1))
    predicted_scaled = model.predict(X_predict)
    predicted_mu_scaled = predicted_scaled[:, 0].reshape(-1, 1)
    predicted_inverse_transformed =  scaler.inverse_transform(predicted_mu_scaled)
    predicted.append(scaler.inverse_transform(predicted_mu_scaled))
    last_seq_scaled = last_seq_scaled[1:]
    last_seq_scaled = np.vstack([last_seq_scaled, predicted_inverse_transformed])
    #last_seq_scaled = np.vstack([predicted_inverse_transformed, last_seq_scaled])

actual = species_data[species_data['seasonIndex'] == start_index]['Sightings'].values
plt.figure(figsize=(10, 6))

# plot training data
training_data_plagioecia = species_data[species_data['seasonIndex'] < start_index]  
plt.plot(training_data_plagioecia['seasonIndex'], training_data_plagioecia['Sightings'], label='Training Data', alpha=0.7)

# plot actual value
if actual.size > 0:
    plt.scatter(start_index, actual, color='green', label='Actual', s=100, zorder=2)  

# plot the prediction
for i in range(amount_of_predictions):
    plt.scatter(start_index + i, predicted[i], color='red', label='Predicted', s=100, zorder=2)  

plt.xlabel('Season Index') 
plt.ylabel('Normalized Sightings')
plt.title(species_name +' Sightings Prediction')
plt.legend()
plt.grid(True)
plt.show()
