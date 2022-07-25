# from crypt import methods
from lib2to3.pgen2.token import STRING
from re import S
from turtle import color, width
from colorama import Style
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio import start_server, config, platform
from flask import Flask, render_template, request

import pandas as pd
import numpy as np
import datetime
import numpy_financial
import matplotlib.pyplot as plt



app = Flask(__name__)
@app.route("/")

@app.route("/home")
def home():

    return render_template("base.html")

@app.route("/result", methods=['POST'])
def result():
    output = request.form.to_dict()
    montant = output["montant"] 
    duree = output["duree"]
    
    interet = output["interet"]
    assurance = output["assurance"]
    
    
    # fonction calculeMensualité
    
    C = float(montant)
    T = str(interet)
    T = T.replace(",",".")
    T = float(T)
    N2 = int(duree)
    N = N2*12
    ASSU = str(assurance)
    ASSU = ASSU.replace(",",".")
    ASSU = float(ASSU)
    t = (T / 12) 
    q = 1 + t / 100 # calcul du coefficient multiplicateur associé à une hausse de t%
    M = (q**N * (C) * (1 - q) / (1 - q**N)) + C*((ASSU/100)/12)
    M= "{0:.3f}".format(M)
    
    
    
    # I = N * M - C # calcul des intérêts versés
    # #put_text(f"Votre mensulaité sera de {M} euros")
    # #put_text(f"Le montant total des intérêts versés sera de {I} euros")
    T2 = T*1/100
    rng = pd.date_range("01-01-2021", periods=N, freq='MS')
    rng.name = "Date"
    df = pd.DataFrame(index=rng, columns=['Mensualité', 'Capital Amorti', 'Intérêts', 'Capital restant dû'], dtype='float')
    df.reset_index(inplace=True)
    df.index += 1
    df.index.name = "Periode (Mois)"

    df["Mensualité"] = -1 * numpy_financial.pmt(T2/12, N, C)+ C*((ASSU/100)/12)
    df["Capital Amorti"] = -1 * numpy_financial.ppmt(T2/12,df.index,N, C)
    df["Intérêts"] = -1 * numpy_financial.ipmt(T2/12,df.index, N, C) 
    df = df.round(2)

    df["Capital restant dû"] = 0
    df.loc[1, "Capital restant dû"] = C - df.loc[1, "Capital Amorti"]

    for period in range(2, len(df)+1):
        previous_balance = df.loc[period-1, "Capital restant dû"]
        principal_paid = df.loc[period, "Capital Amorti"]
        
        if previous_balance == 0:
            df.loc[period, ["Mensualité", 'Capital Amorti', "Intérêts", "Capital restant dû"]] == 0
            continue
        elif principal_paid <= previous_balance:
            df.loc[period, "Capital restant dû"] = previous_balance - principal_paid
    
    df["Date"] = pd.to_datetime(df["Date"],format='%d-%m-%Y')

    put_collapse('Voir le tableau', [put_html(df.to_html(border = 0))])
       
  
    
    # d=df.plot.bar().get_figure()
    # d.savefig('picture')
    
    # ______________________test
        # my_pic=df.plot.bar(title='Résultat de votre simulation',logy=True).get_figure()

  
    my_pic=df.plot.bar(title='Résultat de votre simulation',grid=True).get_figure()

    my_pic.savefig('static\\images\\picture.jpg')  
    
    
    
    
    
    
    
    
    
    
    
    return render_template("base.html", montant = montant,duree = duree,interet=interet,assurance=assurance,M=M,df=my_pic) 


    







if __name__ == '__main__':
    app.run(debug=True)
    #platform.start_server(main, port=8080, debug=True,remote_access=True,reconnect_timeout = True) 
    # platform.flask.start_server(main,port=8000, debug=True,remote_access=True,session_expire_seconds=None)