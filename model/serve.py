from flask import Flask, request, jsonify
from model.infer_siamese import load_templates, predict_symbol
import os

app = Flask(__name__)

# Charger les templates au démarrage
templates = load_templates()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'drawing_data' not in data:
            return jsonify({'error': 'No drawing data provided'}), 400
        
        drawing_data = data['drawing_data']
        prediction = predict_symbol(drawing_data, templates)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 