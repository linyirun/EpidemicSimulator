import pandas
import plotly as pt
import pandas as pd
import plotly.express as px


if __name__ == '__main__':
    data1 = [[1, 2, 3, 4, 5], [5, 4, 2, 1, 1], [7, 8, 6, 7, 8], [9, 4, 2, 1, 1], [9, 3, 2, 1, 1]]
    pandas1 = pandas.DataFrame(data1)
    pandas1.columns = ["Sequence", "Start", "End", "Coverage", 'Lols']
    fig = px.scatter(pandas1, x='Sequence', y='Start')
    fig.show()
