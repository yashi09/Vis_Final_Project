from flask import Flask, render_template, url_for
import json
from flask import request
from flask import jsonify
import pandas as pd
from sklearn.preprocessing import scale
from sklearn.cluster import KMeans
import numpy as np
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from collections import OrderedDict

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def defaultroute():
    if request.method == 'POST':
        if request.form['request'] == 'PCPPlot':
            data = {'PCPPlotData': json.dumps(PCPPlotData.to_dict(orient="records"))}
            return jsonify(data)
    else:
        return render_template('index.html')

if __name__ == '__main__':
  df = pd.read_csv('RDC_Inventory_Core_Metrics_State_History.csv')
  df = df.iloc[0:2000,2:]
  df = df.dropna()
  columns = df.columns
  df = df._get_numeric_data()
  x = df.values
  x = scale(x)
  print("----", x)
  """
  mds = MDS(dissimilarity='euclidean')
  mds = mds.fit_transform(x)
  MDSPlotData = pd.DataFrame(mds,columns=["MDS_1","MDS_2"])"""
  distortions = []
  for k in range(1,11):
    kmeanModel = KMeans(n_clusters=k)
    kmeanModel.fit(x)
    distortions.append(kmeanModel.inertia_)
    
  optimal_k = 5
  prev_diff = 0
  for k in range(1,10):
    if prev_diff == 0:
      prev_diff = distortions[k-1] - distortions[k]
    else:
      if((prev_diff-(distortions[k-1] - distortions[k]))/(distortions[k-1] - distortions[k]) ) > 1:
        optimal_k = k
        break
      prev_diff = distortions[k-1] - distortions[k]
      
  kmeanModel = KMeans(n_clusters=optimal_k)
  kmeanModel.fit(x)
  pca_scatter = PCA(n_components = 21)
  pca_scatter.fit_transform(x)
  sum_of_squares = OrderedDict()
  k = 0
  for l in pca_scatter.components_:
      sum_of_squares[k] = sum(map(lambda i : i * i, l))
      k += 1
        
  sorted_dict = dict(sorted(sum_of_squares.items(), key=lambda item: item[1]))
  max_pca = list(sorted_dict)
  column_names = []
  column_names.append(columns[max_pca[-1]])
  column_names.append(columns[max_pca[-2]])
  column_names.append(columns[max_pca[-3]])
  column_names.append(columns[max_pca[-4]])
  PCPPlotData = df[column_names]
  kmeanModel = KMeans(n_clusters=optimal_k)
  kmeanModel.fit(df)
  PCPPlotData["K_Means"] = kmeanModel.predict(df)



app.run(debug=True)
