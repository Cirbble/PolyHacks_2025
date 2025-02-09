import pandas as pd
import numpy as np
import tensorflow as tf
import os
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from tensorflow.keras import backend as keras

# Global variables
sequence_length = 12
model = None
scaler = None
data = None

# Define the custom loss function before loading the model
@tf.keras.utils.register_keras_serializable(package='Custom', name='negative_binomial_nll_multi_step')
def negative_binomial_nll_multi_step(y_true, y_pred):
    """Custom negative binomial loss function for multi-step predictions"""
    n_steps = y_true.shape[1]
    losses = []
    for i in range(n_steps):
        mu = y_pred[:, i*2]
        alpha = y_pred[:, i*2 + 1]
        y_true_step = y_true[:, i]

        epsilon = keras.epsilon()
        alpha = tf.clip_by_value(alpha, epsilon, 100.0)
        mu = tf.clip_by_value(mu, epsilon, 1e6)

        log_likelihood = tf.math.lgamma(y_true_step + alpha) - tf.math.lgamma(alpha) - tf.math.lgamma(y_true_step + 1) + \
            alpha * tf.math.log(alpha) - alpha * tf.math.log(alpha + mu) + \
            y_true_step * tf.math.log(mu) - y_true_step * tf.math.log(alpha + mu)

        losses.append(-keras.mean(log_likelihood))
    return tf.reduce_mean(losses)

def initialize_model():
    global model, scaler, data
    
    print("Initializing AI model...")
    
    try:
        # Load your data
        data = pd.read_csv("marine_species_data.csv")
        
        # Convert months to seasons and calculate seasonal sightings
        data['seasonIndex'] = (data['monthIndex'] // 3)
        data = data.groupby(['seasonIndex', 'speciesName'])['monthlySightings'].sum().reset_index()
        
        # Initialize scaler
        scaler = MinMaxScaler()
        all_sightings = data['monthlySightings'].values.reshape(-1, 1)
        scaler.fit(all_sightings)
        
        # Load the pre-trained model with custom objects
        if os.path.exists('animal_model.keras'):
            custom_objects = {
                'negative_binomial_nll_multi_step': negative_binomial_nll_multi_step,
                'Custom>negative_binomial_nll_multi_step': negative_binomial_nll_multi_step
            }
            model = tf.keras.models.load_model('animal_model.keras', 
                custom_objects=custom_objects)
            print("Model loaded successfully")
        else:
            raise Exception("Model file 'animal_model.keras' not found!")
            
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        raise e

def prediction_plotting(n_steps, amount_of_predictions, species_name='Disporella hispida'):
    """
    Generate predictions for a species
    
    Args:
        n_steps (int): Number of steps per prediction
        amount_of_predictions (int): Total number of predictions to make
        species_name (str): Name of the species to predict
    """
    try:
        species_data = data[data['speciesName'] == species_name].copy()
        start_index = (2021 - 1980) * 4  # Winter 2020-2021

        
        predicted = []
        last_seq_data = species_data[species_data['seasonIndex'] < start_index].tail(sequence_length)['monthlySightings'].values.reshape(-1, 1)
        last_seq_scaled = scaler.transform(last_seq_data)

        # Make predictions one at a time
        for i in range(amount_of_predictions):
            X_predict = np.reshape(last_seq_scaled, (1, sequence_length, 1))
            predicted_scaled = model.predict(X_predict, verbose=0)
            # Take only the first prediction (mu) for each step
            predicted_value = predicted_scaled[0, 0]  # Get first prediction
            predicted_value_reshaped = np.array([[predicted_value]])
            predicted_inverse = scaler.inverse_transform(predicted_value_reshaped)[0, 0]
            predicted.append(predicted_inverse)
            
            # Update the sequence for next prediction
            last_seq_scaled = np.vstack([last_seq_scaled[1:], [[predicted_value]]])

        actual = species_data[species_data['seasonIndex'].between(
            start_index, 
            start_index + amount_of_predictions - 1
        )]['monthlySightings'].values

        # Clear any existing plots
        plt.clf()
        plt.figure(figsize=(10, 6))
        
        # Plot training data
        training_data = species_data[species_data['seasonIndex'] < start_index]
        plt.plot(training_data['seasonIndex'], training_data['monthlySightings'], 
                label='Historical Data', alpha=0.7)
        
        # Plot actual values if they exist
        if len(actual) > 0:
            plt.plot(range(start_index, start_index + len(actual)), actual, 
                    color='green', label='Actual', marker='o')
        
        # Plot predicted values
        predicted_indices = range(start_index, start_index + len(predicted))
        plt.plot(predicted_indices, predicted, color='red', 
                label='Predicted', linestyle='--', marker='x')
        
        plt.xlabel('Season Index')
        plt.ylabel('Sightings')
        plt.title(f'{species_name} Sightings Prediction')
        plt.legend()
        plt.grid(True)
        
    except Exception as e:
        print(f"Error in prediction_plotting: {str(e)}")
        raise e

# Initialize the model when the module is imported
initialize_model()