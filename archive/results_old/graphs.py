import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.express as px
import pdb

# df = px.data.iris()


dataFiles = ["scenFullNoNo.csv"]
data = pd.read_csv(dataFiles[0])

fig = px.scatter_3d(data, x='Time window [min.]', y='Solution time [sec.]', z='Cost [EURO]',
                    color = 'totalDelay', size = 'totalCancel', symbol = 'species')
fig.show()

