import random
import pandas as pd
from bokeh.driving import count
from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure, show
from bokeh.models import DatetimeTickFormatter
from bokeh.models.widgets import Div
from bokeh.layouts import column,row
import time
from datetime import datetime
from confluent_kafka import Consumer


UPDATE_INTERVAL = 1
ROLLOVER = 10 # Number of displayed data points

source = ColumnDataSource({"x": [], "y": []})
consumer = Consumer({'bootstrap.servers': 'url_kafka', 'security.protocol': 'SASL_SSL', 'sasl.mechanisms': 'PLAIN', 'sasl.username': 'username_kafka', 'sasl.password': 'password_kafka', 'group.id': 'python_example_group_1', 'auto.offset.reset': 'earliest'})
# Set up a callback to handle the '--reset' flag.

# Subscribe to topic
consumer.subscribe(['singgih-data-clean'])
div = Div(
    text='',
    width=120,
    height=35
)



@count()
def update(x):
    msg_value=None
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            print("Waiting...")
            return
        elif msg.error():
            print("ERROR: %s".format(msg.error()))
            return
        else:
            print("Topic {}, Event msg = {}".format(msg.topic(), msg.value().decode('utf-8')))
            msg_value=msg
            break

    values=eval(msg_value.value().decode("utf-8"))
    x=pd.to_datetime(values["measurement_timestamp"])
   
    print(x)

    div.text = "TimeStamp: "+str(x)


    y = values['water_temperature']
    print(y)
    
    source.stream({"x": [x], "y": [y]},ROLLOVER)

p = figure(title="Water Temperature Sensor Data",x_axis_type = "datetime",width=1000)
p.line("x", "y", source=source)

p.xaxis.formatter=DatetimeTickFormatter(hourmin = ['%H:%M'])
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Value'
p.title.align = "right"
p.title.text_color = "orange"
p.title.text_font_size = "25px"

doc = curdoc()
#doc.add_root(p)

doc.add_root(
    row(children=[div,p])
)
doc.add_periodic_callback(update, UPDATE_INTERVAL)