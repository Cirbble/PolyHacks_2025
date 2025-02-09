from flask import Flask, request, jsonify
from flask_cors import CORS
import ai_multi_step_test as ai
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received data:", data)
        n_steps = int(data['n_steps'])
        prediction_amount = int(data['prediction_amount'])
        species_name = data['species_name']
        
        # Clear any existing plots
        plt.close('all')
        
        # Call prediction function with all parameters
        ai.prediction_plotting(n_steps, prediction_amount, species_name)
        
        # Convert plot to base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close('all')
        
        return jsonify({
            'success': True,
            'plot': plot_url
        })
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        plt.close('all')  # Clean up plots even on error
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000) 