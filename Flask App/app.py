# -*- coding: utf-8 -*-
import sys
sys.path.append(r'C:/Users/veerg/OneDrive/Documents/Premier League Predictor')
import pandas as pd
from flask import Flask, render_template
from constants import *

df_to_show = pd.read_excel(betting_predictions)

df_to_show  = df_to_show.drop(df_to_show.columns[0], axis = 1)

app = Flask(__name__)

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/table')
def display_table():
    table_html = df_to_show.to_html(classes='dataframe table table-striped')
    return render_template('table.html', table_html=table_html)

if __name__ == "__main__":
    app.run(debug=True)


    



