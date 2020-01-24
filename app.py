import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle

app = Flask(__name__)
model = pickle.load(open('realestate_model.pickle', 'rb'))


@app.route('/', methods=['GET'])
def dropdown():
    cities = pickle.load(open('cities_name.pickle', 'rb'))

    return render_template('index.html', cities=cities)

@app.route('/predict',methods=['POST'])
def predict():

    # Load cities
    cities = pickle.load(open('cities_name.pickle', 'rb'))

    # Get form answers of the user
    int_features = [x for x in request.form.values()]

    # Delete last item of the list which is not a number
    int_features.pop()

    # resultat de la ville choisie dans le formulaire 
    city_selected = request.form['cities']
    len_array = len(cities) + 1

    # Get index of the city in the cities list
    index_city = cities.index(f'{city_selected}')

    # Create a list of len = number of cities
    list_city = [0 for i in range(1, len_array)]

    # city selected = 1
    list_city[index_city] = 1

    # add city list values to int_features
    int_features.extend(list_city)
    final_features = [np.array(int_features)]

    # Predict with loaded model
    prediction = np.exp(model.predict(final_features))

    # Format of the output prediction
    output = int(prediction[0])

    return render_template('index.html', prediction_text='Le prix du bien devrait etre de {} euros'.format(output))


if __name__ == "__main__":
    app.run(debug=True)