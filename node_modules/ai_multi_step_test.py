import pandas as pd
import math
import numpy as np
import tensorflow as tf
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as keras
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from sklearn.metrics import mean_absolute_error, mean_squared_error



# global variables we could want to change
sequence_length = 12  # time index (seasons)

n_steps = 6  # Example: predict 3 seasons ahead

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
def create_lags(data, lags):
    """Creates lagged features for the 'Sightings' column."""
    for lag in lags:
        data[f'Sightings_lag_{lag}'] = data['Sightings'].shift(lag).fillna(0)  # Fill NaN with 0
    return data

lags_to_include = [1, 2, 3, 4, 8, 12] # Example lags (e.g., previous 1, 2, 3, 4, 8, and 12 seasons)
data = create_lags(data, lags_to_include)


def create_multi_step_sequences(data, seq_length, n_steps, lags):
    num_features = 1 + len(lags) # 1 for original 'Sightings', rest for lags
    X = []
    y = []
    for i in range(len(data) - seq_length - n_steps + 1):
        X.append(data[i : (i + seq_length), :num_features]) # Include all features
        y.append(data[i + seq_length : i + seq_length + n_steps, 0]) # Predict the original 'Sightings'
    return np.array(X), np.array(y)

X_train, y_train = create_multi_step_sequences(train_sightings_scaled, sequence_length, n_steps, lags_to_include)
X_validation, y_validation = create_multi_step_sequences(validation_sightings_scaled, sequence_length, n_steps, lags_to_include)
X_test, y_test = create_multi_step_sequences(test_sightings_scaled, sequence_length, n_steps, lags_to_include)

# Reshape input (now includes lagged features):
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2])) # Add the number of features dimension here
X_validation = np.reshape(X_validation, (X_validation.shape[0], X_validation.shape[1], X_validation.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], X_test.shape[2]))
##############################################
##############################################
##############################################
##############################################

# reshape input to be [samples, time steps, features] or LSTM to work

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_validation = np.reshape(X_validation, (X_validation.shape[0], X_validation.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))


def negative_binomial_nll_multi_step(y_true, y_pred):
    n_steps = y_true.shape[1]  # Get n_steps from y_true
    losses = []
    for i in range(n_steps):
        mu = y_pred[:, i*2]  # Predicted mean for step i
        alpha = y_pred[:, i*2 + 1]  # Predicted dispersion for step i
        y_true_step = y_true[:, i]  # True value for step i

        epsilon = keras.epsilon() # From tensorflow.keras
        alpha = tf.clip_by_value(alpha, epsilon, 100.0)  # Clip alpha
        mu = tf.clip_by_value(mu, epsilon, 1e6) # Clip mu (adjust upper bound as needed)

        log_likelihood = tf.math.lgamma(y_true_step + alpha) - tf.math.lgamma(alpha) - tf.math.lgamma(y_true_step + 1) + \
            alpha * tf.math.log(alpha) - alpha * tf.math.log(alpha + mu) + \
            y_true_step * tf.math.log(mu) - y_true_step * tf.math.log(alpha + mu)

        losses.append(-keras.mean(log_likelihood))
    return tf.reduce_mean(losses)  # Average the losses across all steps


# lstm
model = Sequential()
# 1st lstm layer 
model.add(LSTM(200, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences = True)) # Single LSTM layer with 50 units
model.add(Dropout(0.2))
# 2nd
model.add(LSTM(200, return_sequences = True))
model.add(Dropout(0.2))
# 3rd
model.add(LSTM(200))
model.add(Dense(2 * n_steps, activation='softplus')) # Output layer with 2 neurons (mu, alpha), exponential activation to ensure positive outputs

# 6. Compile Model
optimizer = Adam(learning_rate=0.001, clipnorm=1.0) # Example: clip gradients with L2 norm
model.compile(optimizer=optimizer, loss=negative_binomial_nll_multi_step)



def train(epochs, batch_size):
    history = model.fit(X_train, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_data=(X_validation, y_validation),
                    shuffle=False) # Shuffle False for time series

    predictions_scaled = model.predict(X_test)  # Shape: (samples, n_steps * 2)

    # Reshape predictions to (samples, n_steps, 2) to extract mu and alpha
    predictions_scaled = predictions_scaled.reshape(predictions_scaled.shape[0], n_steps, 2)

    predicted_mu_scaled = predictions_scaled[:, :, 0] # Extract mu for all steps. Shape: (samples, n_steps)

    predicted_sightings = scaler.inverse_transform(predicted_mu_scaled.reshape(-1, 1)).reshape(predicted_mu_scaled.shape) # Inverse transform. Shape: (samples, n_steps)

    y_test_reshaped = y_test.reshape(-1, 1)  # Reshape to (samples * n_steps, 1)

    actual_sightings = scaler.inverse_transform(y_test_reshaped).reshape(y_test.shape) # Reshape back to (samples, n_steps)
    actual_sightings_flat = actual_sightings.flatten()
    predicted_sightings_flat = predicted_sightings.flatten()

    mae = mean_absolute_error(actual_sightings_flat, predicted_sightings_flat)

    print(f"Mean Absolute Error: {mae}")




## testing prediction
def prediction_plotting(n_steps, amount_of_predictions):
    species_name = 'Disporella hispida'
    species_data = data[data['speciesName'] == species_name]
    start_index = (2021 - 1980) * 4  # Winter 2020-2021

    num_prediction_sets = amount_of_predictions // n_steps # How many sets of multi-step predictions

    predicted = []
    last_seq_data = species_data[species_data['seasonIndex'] < start_index].tail(sequence_length)['Sightings'].values.reshape(-1, 1) # Ensure we start with enough data points
    last_seq_scaled = scaler.transform(last_seq_data)

    for i in range(num_prediction_sets):
        X_predict = np.reshape(last_seq_scaled, (1, sequence_length, 1))
        predicted_scaled = model.predict(X_predict)
        predicted_mu_scaled = predicted_scaled[:, :n_steps].reshape(-1, n_steps) # Extract mu for n_steps
        predicted_inverse_transformed = scaler.inverse_transform(predicted_mu_scaled)
        predicted.extend(predicted_inverse_transformed[:, 0].tolist())  # Append ONLY the first prediction
        last_seq_scaled = np.vstack([last_seq_scaled[1:], predicted_inverse_transformed[:, 0].reshape(-1, 1)]) # Use the first prediction only

    actual = species_data[species_data['seasonIndex'].between(start_index, start_index + amount_of_predictions - 1)]['Sightings'].values # Get all the actual values for the prediction range

    plt.figure(figsize=(10, 6))

    # Plot training data
    training_data_plagioecia = species_data[species_data['seasonIndex'] < start_index]
    plt.plot(training_data_plagioecia['seasonIndex'], training_data_plagioecia['Sightings'], label='Training Data', alpha=0.7)

    # Plot actual values
    plt.plot(range(start_index, start_index + len(actual)), actual, color='green', label='Actual')  # Use markers for actual values

    # Plot predicted values
    predicted_indices = range(start_index, start_index + len(predicted))
    plt.plot(predicted_indices, predicted, color='red', label='Predicted')  # Use markers for predictions

    plt.xlabel('Season Index')
    plt.ylabel('Normalized Sightings')
    plt.title(species_name + ' Sightings Prediction')
    plt.legend()
    plt.grid(True)
    plt.show()



while True:
    command = input("Enter command ('save', 'load', 'run', 'train', 'quit'): ").lower()

    if command == 'save':
        model.save('animal_model.keras')
        print(f"Weight file saved")

    elif command == 'load':
        if os.path.exists('animal_model.keras'):
            model = tf.keras.models.load_model('animal_model.keras')
            print(f"Weights loaded")
        else:
            print(f"Weights file not found")

    elif command == 'run':
        nsteps_input = int(input("Enter number of steps"))
        prediction_amount = int(input("Enter number of future steps to predict"))
        prediction_plotting(nsteps_input, prediction_amount)

    elif command == 'train':
        epochs = int(input("Enter number of epochs: "))  # Get epochs from user
        batch_size = int(input("Enter batch size: ")) # Get batch size from user

        train(epochs, batch_size)
        print("Model trained.")

    elif command == 'quit':
        break

    else:
        print("Invalid command.")