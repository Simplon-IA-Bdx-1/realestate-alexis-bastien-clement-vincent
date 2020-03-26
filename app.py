import numpy as np
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import reqparse, abort, Api, Resource
from sklearn.preprocessing import MinMaxScaler,MaxAbsScaler,StandardScaler,RobustScaler,Normalizer
import pickle
import pandas as pd

app = Flask(__name__)
model = pickle.load(open('realestate_model.pickle', 'rb'))
scaler = pickle.load(open('best_scaler.pickle', 'rb'))

# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('query')

@app.route('/api', methods=['POST'])
def api_model():
    cities = pickle.load(open('district_values.pickle', 'rb'))

    if not request.json or not 'area' in request.json:
        abort(400)

    input = {
        'area': request.json['area'],
        'rooms': request.json['area'],
        'district': request.json['district'],
    }

   # Load zip codes & scaler
    cities = pickle.load(open('district_values.pickle', 'rb'))
    scaler = pickle.load(open('best_scaler.pickle', 'rb'))

    # Get form answers of the user
    int_features = [x for x in request.json.values()]
    

    # Delete last item of the list which is the zip code
    int_features.pop()
    dict_features = {
        'area':  [int(request.json['area'])],
        'rooms': [int(request.json['rooms'])]
    }

    city_selected = request.json['cities']
    dict_localisation = { i : [0] for i in cities }
    district_selected = request.json['cities']
    dict_localisation[district_selected] = 1
    dict_features.update(dict_localisation)
    df_pred = pd.DataFrame(dict_features)
    X_new = df_pred.values
    X_new_scale = scaler.transform(X_new)
    pred = model.predict(X_new_scale)
    price_pred = int(np.exp(pred[0]))
    output = price_pred
    
    return output

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def dropdown():
    cities = pickle.load(open('district_values.pickle', 'rb'))

    return render_template('index.html', cities=cities)

@app.route('/predict',methods=['POST'])
def predict():

    # Load zip codes & scaler
    cities = pickle.load(open('district_values.pickle', 'rb'))
    scaler = pickle.load(open('best_scaler.pickle', 'rb'))

    # Get form answers of the user
    int_features = [x for x in request.form.values()]
    

    # Delete last item of the list which is the zip code
    int_features.pop()
    dict_features = {
        'area':  [int(int_features[0])],
        'rooms': [int(int_features[1])]
    }

    city_selected = request.form['cities']
    dict_localisation = { i : [0] for i in cities }
    district_selected = request.form['cities']
    dict_localisation[district_selected] = 1
    dict_features.update(dict_localisation)
    df_pred = pd.DataFrame(dict_features)
    X_new = df_pred.values
    X_new_scale = scaler.transform(X_new)
    pred = model.predict(X_new_scale)
    price_pred = int(np.exp(pred[0]))
    output = price_pred

    return render_template('index.html', prediction_text='{} euros'.format(output))

if __name__ == "__main__":
    app.run(debug=True)