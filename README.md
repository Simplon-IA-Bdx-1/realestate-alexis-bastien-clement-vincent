# Realestate
[![Generic badge](https://img.shields.io/badge/Project-MachineLearning-<COLOR>.svg)](https://shields.io/)

Realestate is a End-to-End Machine Learning Project which the goal is to predict sales prices for real estate.
<br>
## Installation
### Requirements

[![Anaconda 3.8.1](https://anaconda.org/anaconda/anaconda/badges/platforms.svg)]()


[![Anaconda 3.8.1](https://anaconda.org/anaconda/anaconda/badges/version.svg)](https://www.anaconda.com/distribution/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/)





### Download the code

```
git clone https://github.com/Simplon-IA-Bdx-1/realestate-alexis-bastien-clement-vincent.git
```


### Environment Setup
Windows

```
conda env create -f environment-win.yml
```
Mac

```
conda env create -f environment-mac.yml
```

### Acivate environment

```
conda activate realestate
```

<br>

## How it works
1. The scraper.py will collect data from the website logic-immo.com and export scraped data to a csv with four features id, surface, rooms, price.
2. The model.py will search best parameters and choose the best model to make the prediction. Every log is available on mlflow with `mlflow ui`


![](https://media.discordapp.net/attachments/666995712613023744/691584605601398814/mlflow.PNG?width=1440&height=401) 
<br><br>
3. The app.py will deploy the model with Flask on the port 5000, you can choose to use the web interface to make your prediction or via curl in your terminal

<br>

## Tests
To run python scripts you have to make your conda environment is activated
<br>

### Scraper

```
scrapy runspider scraper.py
```


[![asciicast](https://asciinema.org/a/ZT0DKHv4S7tS3cKes0Cszs1xQ.svg)](https://asciinema.org/a/ZT0DKHv4S7tS3cKes0Cszs1xQ)
### Model
```
python model.py
```
### Deployment
```
python app.py
```
##### Web Interface
Open your browser and paste the following url
```
https://localhost:5000
```
<br>

![](https://media.discordapp.net/attachments/666995712613023744/692408442211795094/realestate-web.png)

##### curl
Open a new terminal and make your request like the following example

![](https://cdn.discordapp.com/attachments/638735265262862376/690108402004787214/API_Realestate.png)
<br>

## Team

* **V. Lagache** <a href="http://github.com/vlagache" target="_blank">`github.com/vlagache`</a>
* **C. Gombeaud** <a href="https://github.com/ClementGombeaud" target="_blank">`github.com/ClementGombeaud`</a>
* **B. Roques** <a href="http://github.com/broques" target="_blank">`github.com/broques91`</a>
* **A. Dubois** <a href="https://github.com/AlexisDub" target="_blank">`github.com/AlexisDub`</a>

<br>

## Feedback

[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/broques91)

<br>

## License

[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 © <a href="https://simplon.co/" target="_blank">Simplon</a>.
