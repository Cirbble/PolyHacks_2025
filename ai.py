import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as keras
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

print("making ai rn")
# global variables we could want to change
sequence_length = 12 # months



# somehow we get data
# data; 4 columns, speciesName, monthlySightings, monthIndex, className
data = pd.read_csv("marine_species_data.csv")

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

training_data = data.iloc[0: training_end]
validation_data = data.iloc[training_end + 1: validation_end]
test_data = data.iloc[validation_end + 1: test_end]


# shaping the data

train_sightings = training_data['monthlySightings'].values.reshape(-1, 1)
validation_sightings = validation_data['monthlySightings'].values.reshape(-1, 1)
test_sightings = test_data['monthlySightings'].values.reshape(-1, 1)
all_sightings = data['monthlySightings'].values.reshape(-1, 1)

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


# 5. Build LSTM Model
model = Sequential()
model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2]))) # Single LSTM layer with 50 units
model.add(Dense(2, activation='exponential')) # Output layer with 2 neurons (mu, alpha), exponential activation to ensure positive outputs

# 6. Compile Model
optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss=negative_binomial_nll) # Use custom NLL loss


# 7. Model Training
epochs = 50 # Adjust as needed
batch_size = 32 # Adjust as needed

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


# 9. Evaluate Metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(actual_sightings, predicted_sightings)
rmse = np.sqrt(mean_squared_error(actual_sightings, predicted_sightings))

print(f'Test Mean Absolute Error (MAE): {mae:.2f}')
print(f'Test Root Mean Squared Error (RMSE): {rmse:.2f}')

plagioecia_data = data[data['speciesName'] == 'Plagioecia patina']

# 1. Get the 12 most recent data points *before* Jan 2021
jan_2021_index = (2021 - 1980) * 12  # Assuming data starts from Jan 1980

# Check if jan_2021_index exists for the species
if jan_2021_index not in plagioecia_data['monthIndex'].values:
    print("January 2021 data not found for Plagioecia patina.")
    exit()

# Filter data before Jan 2021
data_before_jan2021 = plagioecia_data[plagioecia_data['monthIndex'] < jan_2021_index]

# Get the last 12 entries (most recent)
if len(data_before_jan2021) < 12:
    print("Not enough data points to predict.")
    exit()

last_12_months_data = data_before_jan2021.tail(12)['monthlySightings'].values.reshape(-1, 1)


# 2. Scale the input data (same as before)
last_12_months_scaled = scaler.transform(last_12_months_data)

# 3. Reshape for LSTM (same as before)
X_predict = np.reshape(last_12_months_scaled, (1, sequence_length, 1))

# 4. Make the prediction (same as before)
predicted_jan_2021_scaled = model.predict(X_predict)

# 5. Extract mu and Inverse transform (same as before)
predicted_jan_2021_mu_scaled = predicted_jan_2021_scaled[:, 0].reshape(-1, 1)
predicted_jan_2021 = scaler.inverse_transform(predicted_jan_2021_mu_scaled)

print(f"Predicted Plagioecia patina sightings for January 2021: {predicted_jan_2021[0, 0]:.2f}")


actual_jan_2021 = plagioecia_data[plagioecia_data['monthIndex'] == jan_2021_index]['monthlySightings'].values

if actual_jan_2021 > -1:  # Check if data exists
    actual_jan_2021 = actual_jan_2021[0]  # Extract the value (it's in a NumPy array)
    print(f"Actual Plagioecia patina sightings for January 2021: {actual_jan_2021}")

    # Calculate and print the error
    error = abs(predicted_jan_2021[0, 0] - actual_jan_2021)
    percentage_error = (error / actual_jan_2021) * 100 if actual_jan_2021 !=0 else float('inf') # Avoid division by zero
    print(f"Absolute Error: {error:.2f}")
    print(f"Percentage Error: {percentage_error:.2f}%")
else:
    print("No actual data found for January 2021 for Plagioecia patina.")

# --- Plotting with Actual Value ---
plt.figure(figsize=(10, 6))

# Plot the training data (for context) - Optional
training_data_plagioecia = plagioecia_data[plagioecia_data['monthIndex'] < jan_2021_index - 12]  # Training data
plt.plot(training_data_plagioecia['monthIndex'], training_data_plagioecia['monthlySightings'], label='Training Data', alpha=0.7)

# Plot the actual value for Jan 2021 (if it exists)
if actual_jan_2021 > -1:
    plt.scatter(jan_2021_index, actual_jan_2021, color='green', label='Actual Jan 2021', s=100, zorder=2)  # Larger marker

# Plot the prediction
plt.scatter(jan_2021_index, predicted_jan_2021, color='red', label='Predicted Jan 2021', s=100, zorder=2)  # Larger marker

plt.xlabel('Month Index')  # X-axis is now month index
plt.ylabel('Monthly Sightings')
plt.title('Plagioecia patina Sightings Prediction')
plt.legend()
plt.grid(True)
plt.show()
