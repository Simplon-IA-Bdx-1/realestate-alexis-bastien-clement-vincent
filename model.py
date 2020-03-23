import pandas as pd
import seaborn as sns
import numpy as np
from math import sqrt
import re
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error , mean_absolute_error
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge, HuberRegressor, LinearRegression
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler,MaxAbsScaler,StandardScaler,RobustScaler,Normalizer

import mlflow
import mlflow.sklearn
import mlflow.xgboost

import logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

def choose_model(df):

    df = prepare_dataset(df)
    df_list,n_estimators_list,contaminations_list = isolation_forest(df)
    log_active_list = ['Yes','No']
    
    best_mape = float("inf")
    best_model = None
    best_scaler = None

    for dataframe,n_estimators,contamination in zip(df_list,n_estimators_list,contaminations_list):

        '''
        log price
        '''
        for log_active in log_active_list:

            df,log_price_set = log_price(log_active,dataframe)

            '''
            Split Train/Val
            '''
            y_train_full = df['price'].values
            X_train_full = df.drop('price', axis=1).values
            X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42)

            '''
            Scaler
            '''
            # scaler = False

            scalers = [
                MinMaxScaler(),
                MaxAbsScaler(),
                StandardScaler(),
                RobustScaler(),
                Normalizer()
            ]

            for scaler in scalers:
                X_train_scale = scaler.fit_transform(X_train)
                X_val_scale = scaler.transform(X_val)

                '''
                Entrainement & Prédiction Model sans Hyperparametres
                '''
                mlflow.set_experiment("choose_best_model")

                models = [
                    xgb.XGBRegressor(objective ='reg:squarederror'),
                    Ridge(),
                    KNeighborsRegressor()
                ]

                for model in models:

                    model.fit(X_train_scale,y_train)
                    predict = model.predict(X_val_scale)
                    model_name = type(model).__name__
                    hp_tuning = model_tuning(df)
                    mae , mape = metrics(log_price_set,y_val,predict)


                    if mape < best_mape:
                        best_mape = mape
                        best_model = model
                        best_scaler = scaler
                    

                    with mlflow.start_run():
                        mlflow.log_param("iF__n_estimators",n_estimators)
                        mlflow.log_param("iF__contamination",contamination)
                        # mlflow.log_metric("r2",r2_score)
                        mlflow.log_metric("mae",mae)
                        mlflow.log_metric("mape",mape)
                        mlflow.set_tag("model",model_name)
                        mlflow.set_tag("log_price",log_price_set)
                        mlflow.set_tag("scaler",scaler)
                        mlflow.set_tag("hp_tuning",hp_tuning)
                        # mlflow.xgboost.log_model(model,"model")
                        mlflow.end_run()

    print(f'Best MAPE : {best_mape} %')
    print(f'Best Model : {best_model}')
    print(f'Best Scaler : {best_scaler}')
    pickle.dump(best_model, open('realestate_model.pickle', 'wb'))
    pickle.dump(best_scaler, open('best_scaler.pickle', 'wb'))


def prepare_dataset(df):

    '''
    Chargement du dataset
    Remove de la colonne id 
    dummies des variables qualitatives ( arrondissements)
    enregistre en pickle les arrondissements dans le bon ordre
    '''

    list_localisation = []
    list_district = []

    df['district'] = df['district'].astype('str')
    df_id = df['id']
    df = df.drop('id', axis=1)
    qual = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=qual, drop_first=True)

    for column in df.columns.values:
        localisation = re.search("^district_",column)
        if(localisation):
            list_localisation.append(column)

    for localisation in list_localisation:
        district = localisation.replace("district_","")
        list_district.append(district)

    pickle.dump(list_district, open('district_values.pickle', 'wb'))

    return df

def isolation_forest(df):
    '''
    Isolation Forrest pour remove les outliers
    Retourne une list de dataframe sans certains outliers séléctionnés en fonction de n_estimators & contamination
    Retourne la liste des n_estimators et contamination testé à chaque tour de boucle
    '''
    df_list = []
    selected_n_estimators = []
    selected_contamination = []
    n_estimators_list = [50,100,150,200,250,300]
    contaminations_list = [0.05,0.1,0.15,0.20,0.25]

    for n_estimators in n_estimators_list:
        for contamination in contaminations_list:
            iso_forest = IsolationForest(n_estimators = n_estimators, contamination = contamination, random_state=42)
            iso_forest = iso_forest.fit(df)
            isoF_outliers_values = df[iso_forest.predict(df) == -1]
            new_df = df.drop(isoF_outliers_values.index.values.tolist())
            df_list.append(new_df)
            selected_n_estimators.append(n_estimators)
            selected_contamination.append(contamination)

    return df_list,selected_n_estimators,selected_contamination

def model_tuning(df):

    hp_tuning = False
    return hp_tuning


def log_price(log_active,dataframe):

    if log_active == "Yes":
        df_log = dataframe.copy()
        df_log['price'] = np.log(df_log['price'])
        df = df_log
        log_price_set = True
    else:
        df = dataframe
        log_price_set = False

    return df,log_price_set

def metrics(log_price,true,predict):

    if log_price:
        mae = round(mean_absolute_error(np.exp(true),np.exp(predict)),2)
        mape = round(np.mean(np.abs((np.exp(true) - np.exp(predict)) / np.exp(true))) * 100,2)
    else:
        mae = round(mean_absolute_error(true,predict))
        mape = round(np.mean(np.abs((true - predict) / true)) * 100,2)

    return mae,mape

if __name__ == "__main__":

    df= pd.read_csv("logic_immo.csv")
    choose_model(df)






