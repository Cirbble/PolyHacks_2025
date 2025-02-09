from flask import Flask, request, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import base64
import io
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        species_name = data['species_name']
        n_steps = data['n_steps']
        prediction_amount = data['prediction_amount']

        # Read the CSV data
        df = pd.read_csv('custom_order.csv')
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['monthlyIndex'], df['monthlySightings'], label='Historical Data')
        plt.xlabel('Month Index')
        plt.ylabel('Number of Sightings')
        plt.title(f'Species Sightings Over Time: {species_name}')
        plt.legend()
        plt.grid(True)

        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({
            'success': True,
            'plot': plot_base64
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 