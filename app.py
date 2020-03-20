import numpy as np
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import reqparse, abort, Api, Resource
import pickle

app = Flask(__name__)
model = pickle.load(open('realestate_model.pickle', 'rb'))

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

    # Get requests of the user
    int_features = [x for x in request.json.values()]

    # Delete last item of the list which is the zip code
    int_features.pop()

    # Zip code requested by the user 
    city_selected = request.json['district']
    len_array = len(cities) + 1

    # Get index of the zip code in the zip code list
    index_city = cities.index(f'{city_selected}')

    # Create a list of len = number of zip code
    list_city = [0 for i in range(1, len_array)]

    # Zip code selected = 1
    list_city[index_city] = 1

    # Add zip code list values to int_features
    int_features.extend(list_city)
    final_features = [np.array(int_features)]

    # Predict with loaded model
    prediction = np.exp(model.predict(final_features))

    # Format of the output prediction
    pred_text = int(prediction[0])

    # Create JSON object
    output = {'predict price': pred_text}
    
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

    # Load zip codes
    cities = pickle.load(open('district_values.pickle', 'rb'))

    # Get form answers of the user
    int_features = [x for x in request.form.values()]

    # Delete last item of the list which is the zip code
    int_features.pop()

    # Result of the selected zip code in form
    city_selected = request.form['cities']
    len_array = len(cities) + 1

    # Get index of the zip code in the zip code list
    index_city = cities.index(f'{city_selected}')

    # Create a list of len = number of zip code
    list_city = [0 for i in range(1, len_array)]

    # Zip code selected = 1
    list_city[index_city] = 1

    # Add zip code list values to int_features
    int_features.extend(list_city)
    final_features = [np.array(int_features)]

    # Predict with loaded model
    prediction = np.exp(model.predict(final_features))

    # Format of the output prediction
    output = int(prediction[0])

    return render_template('index.html', prediction_text='{} euros'.format(output))


if __name__ == "__main__":
    app.run(debug=True)