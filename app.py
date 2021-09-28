# Dependencies
# ----------------------------------
from flask import Flask, render_template, redirect, jsonify, request
from flask import send_from_directory
import pandas as pd
from sqlalchemy import create_engine, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, update, Table
from sqlalchemy.orm import Session
from datetime import datetime
from v_functions import predictModel,predictTwtModel, predictComModel, predictAdjModel
import tweet
from multiprocessing import Value
import os
from config import rds_connection_string
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import json
import numpy as np
import psycopg2
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

# initialize flask
app = Flask(__name__)

# Create database connection String
engine = create_engine(f'postgresql://{rds_connection_string}')

metadata = MetaData(engine)
tweet_data = Table('tweet_data', metadata, autoload=True, autoload_with=engine)
tweet_sentiment = Table('tweet_sentiment', metadata, autoload=True, autoload_with=engine)
filter_data = Table('filter_data', metadata, autoload=True, autoload_with=engine)
@app.route("/")
def home():
	return render_template("index.html")

@app.route("/voting")
def voting():
	return render_template("voting.html")

@app.route("/stats")
def statistics():
	return render_template("statistics.html")

@app.route("/load_tweet")
def load_tweet():

	tweet_dict = {}
	conn = engine.connect()
	session = Session(bind=engine)
	available_tweets = len(pd.read_sql_query('select * from tweet_data WHERE tweet_data.holder = 1', con=conn))
	# session.close()
	if available_tweets == 0:
		tweet.api_call()
	df = pd.read_sql_query('select * from tweet_data WHERE tweet_data.holder = 1', con=conn)
	df = df.iloc[0]
	predicted_sentiments_adj = 42
	df_ver = pd.read_sql_query('select version from stats_data ORDER BY version DESC LIMIT 1', con=conn)
	# version = str(df_ver['version'].max()) + ".h5"
	stats_len = len(df_ver)
	print("grab")
	if stats_len > 0:
		from v_functions import model_versions
		length, err_list = model_versions()
		print("len > 0")
		if length != 3:
			print("len != 3")
			err_string = "The version of your model(s) is not compatible.  The model(s) that need(s) correcting is/are"
			for i in err_list:
				err_string += " " + i
			help_string = ". Please git pull to update your repository in order to get the most up to date model(s)"
			tweet_dict = {
				"tweet":(err_string + help_string)
			}
		else:
			predicted_sentiments_adj = predictAdjModel(df)
			tweet_dict = {
			"id":df['id'],
			"tweet":df['tweet'],
			"joined_lemm":df['joined_lemm'],
			"batch":df['batch'],
			"predicted_sentiments_adj":predicted_sentiments_adj
			}
	else:
		tweet_dict = {
			"id":df['id'],
			"tweet":df['tweet'],
			"joined_lemm":df['joined_lemm'],
			"batch":df['batch'],
			"predicted_sentiments_adj":predicted_sentiments_adj
			}

	return json.dumps(tweet_dict, cls=NpEncoder)


@app.route("/positive_update", methods = ['POST'])
def positive_update():
	# Try to grab values, will catch if someone clicks on face before a tweet loads
	if os.path.isfile("Resources/models/deep_adjudicator_model_trained.h5"):
		df = pd.DataFrame()
		df['tweet'] = [request.form['tweet']]
		df['joined_lemm'] = [request.form['joined_lemm']]
		predicted_sentiments_adj = request.form.get('predicted_sentiments_adj', type=float)
		predicted_sentiments_rd = predictModel(df)
		predicted_sentiments_twt = predictTwtModel(df)
		predicted_sentiments_com = predictComModel(df)

		tweet_dict = {
			"id": request.form['id'],
			"tweet": request.form['tweet'],
			"joined_lemm": request.form['joined_lemm'],
			"sentiments": 1,
			"predicted_sentiments_rd":predicted_sentiments_rd,
			"predicted_sentiments_twt":predicted_sentiments_twt,
			"predicted_sentiments_com":predicted_sentiments_com,
			"Date": datetime.now(),
			"predicted_sentiments_adj":predicted_sentiments_adj

		}

		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == tweet_dict['id']).
			values(holder=0)
			)
		conn.execute(tweet_update)


		# Create connection to SQL database
		conn = engine.connect()
		with conn:
			conn.execute(insert(tweet_sentiment),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"sentiments": tweet_dict['sentiments'],
				"predicted_sentiments_rd":tweet_dict['predicted_sentiments_rd'],
				"Date":tweet_dict['Date'],
				"predicted_sentiments_twt":tweet_dict['predicted_sentiments_twt'],
				"predicted_sentiments_com":tweet_dict['predicted_sentiments_com'],
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":predicted_sentiments_adj

				}])
	else:
		df = pd.DataFrame()
		df['tweet'] = [request.form['tweet']]
		df['joined_lemm'] = [request.form['joined_lemm']]

		predicted_sentiments_rd = predictModel(df)


		tweet_dict = {
			"id": request.form['id'],
			"tweet": request.form['tweet'],
			"joined_lemm": request.form['joined_lemm'],
			"sentiments": 1,
			"predicted_sentiments_rd":predicted_sentiments_rd,
			"Date": datetime.now()
		}

		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == tweet_dict['id']).
			values(holder=0)
			)
		conn.execute(tweet_update)


		# Create connection to SQL database
		conn = engine.connect()
		with conn:
			conn.execute(insert(tweet_sentiment),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"sentiments": tweet_dict['sentiments'],
				"predicted_sentiments_rd":tweet_dict['predicted_sentiments_rd'],
				"Date":tweet_dict['Date'],
				"predicted_sentiments_twt":42,
				"predicted_sentiments_com":42,
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":42
				}])		
	return {}

@app.route("/negative_update", methods = ['POST'])
def negative_update():
	if os.path.isfile("Resources/models/deep_adjudicator_model_trained.h5"):
		df = pd.DataFrame()
		df['tweet'] = [request.form['tweet']]
		df['joined_lemm'] = [request.form['joined_lemm']]
		predicted_sentiments_adj = request.form.get('predicted_sentiments_adj', type=float)
		predicted_sentiments_rd = predictModel(df)
		predicted_sentiments_twt = predictTwtModel(df)
		predicted_sentiments_com = predictComModel(df)

		tweet_dict = {
			"id": request.form['id'],
			"tweet": request.form['tweet'],
			"joined_lemm": request.form['joined_lemm'],
			"sentiments": 0,
			"predicted_sentiments_rd":predicted_sentiments_rd,
			"predicted_sentiments_twt":predicted_sentiments_twt,
			"predicted_sentiments_com":predicted_sentiments_com,
			"Date": datetime.now(),
			"predicted_sentiments_adj":predicted_sentiments_adj
		}

		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == tweet_dict['id']).
			values(holder=0)
			)
		conn.execute(tweet_update)


		# Create connection to SQL database
		conn = engine.connect()
		with conn:
			conn.execute(insert(tweet_sentiment),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"sentiments": tweet_dict['sentiments'],
				"predicted_sentiments_rd":tweet_dict['predicted_sentiments_rd'],
				"Date":tweet_dict['Date'],
				"predicted_sentiments_twt":tweet_dict['predicted_sentiments_twt'],
				"predicted_sentiments_com":tweet_dict['predicted_sentiments_com'],
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":predicted_sentiments_adj
				}])
	else:
		df = pd.DataFrame()
		df['tweet'] = [request.form['tweet']]
		df['joined_lemm'] = [request.form['joined_lemm']]

		predicted_sentiments_rd = predictModel(df)


		tweet_dict = {
			"id": request.form['id'],
			"tweet": request.form['tweet'],
			"joined_lemm": request.form['joined_lemm'],
			"sentiments": 0,
			"predicted_sentiments_rd":predicted_sentiments_rd,
			"Date": datetime.now()
		}
		holder12 = request.form['id']
		print(type(tweet_dict['id']))
		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == holder12).
			values(holder=0)
			)
		conn.execute(tweet_update)

		# Create connection to SQL database
		conn = engine.connect()
		with conn:
			conn.execute(insert(tweet_sentiment),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"sentiments": tweet_dict['sentiments'],
				"predicted_sentiments_rd":tweet_dict['predicted_sentiments_rd'],
				"Date":tweet_dict['Date'],
				"predicted_sentiments_twt":42,
				"predicted_sentiments_com":42,
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":42
				}])
	return {}
@app.route("/neutral_update", methods = ['POST'])
def neutralupdate():
	if os.path.isfile("Resources/models/deep_adjudicator_model_trained.h5"):
		predicted_sentiments_adj = request.form.get('predicted_sentiments_adj', type=float)
		tweet_dict = {
		"id": request.form['id'],
		"tweet": request.form['tweet'],
		"joined_lemm": request.form['joined_lemm'],
		"Date": datetime.now(),
		"predicted_sentiments_adj":predicted_sentiments_adj,

			}

		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == tweet_dict['id']).
			values(holder=0)
			)
		conn.execute(tweet_update)

		conn = engine.connect()
		with conn:
			conn.execute(insert(filter_data),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"Date":tweet_dict['Date'],
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":predicted_sentiments_adj
				}])
	else:
		tweet_dict = {
		"id": request.form['id'],
		"tweet": request.form['tweet'],
		"joined_lemm": request.form['joined_lemm'],
		"Date": datetime.now(),
		"predicted_sentiments_adj":42,

			}

		conn = engine.connect()
		tweet_update = (
			update(tweet_data).
			where(tweet_data.c.id == tweet_dict['id']).
			values(holder=0)
			)
		conn.execute(tweet_update)

		conn = engine.connect()
		with conn:
			conn.execute(insert(filter_data),[{
				"id":request.form['id'],
				"tweet":tweet_dict['tweet'],
				"joined_lemm":tweet_dict['joined_lemm'],
				"Date":tweet_dict['Date'],
				"batch":request.form.get('batch', type=int),
				"predicted_sentiments_adj":42
				}])
	return {}
@app.route("/data")
def datacalled():
	conn = engine.connect()
	stats_df = pd.read_sql_query('select * from stats_data ORDER BY version DESC LIMIT 10', con=conn)
	steve = stats_df.columns
	columns_list = []
	for i in steve:
		columns_list.append(i)
	c_list_f = columns_list[1:19]
	stats_dict = {}
	c_len = len(c_list_f)
	versions = stats_df['version']
	v_len = len(versions)
	v_str = "version_"
	for i in range(v_len):
		temp_dict = {}
		vers = v_str + str(versions[i])
		for j in range(c_len):
			temp_dict[c_list_f[j]] = stats_df[c_list_f[j]][i]
		stats_dict[vers] = temp_dict
	return json.dumps(stats_dict, cls=NpEncoder, default=str)


@app.route("/perf_data")
def perfdatacalled():
	conn = engine.connect()
	performance_df = pd.read_sql_query('select * from performance_stats ORDER BY version DESC LIMIT 10', con=conn).fillna(0)
	stats_len = len(performance_df)
	steve = performance_df.columns
	version_str = "version"
	columns_list = []
	for i in steve:
		columns_list.append(i)
	c_list_f = columns_list[1:19]
	stats_dict = {}
	c_len = len(c_list_f)
	versions = performance_df['version']
	v_len = len(versions)
	v_str = "version_"
	for i in range(v_len):
		temp_dict = {}
		vers = v_str + str(versions[i])
		for j in range(c_len):
			temp_dict[c_list_f[j]] = performance_df[c_list_f[j]][i]
		stats_dict[vers] = temp_dict     
        
	return json.dumps(stats_dict, cls=NpEncoder, default=str)

if __name__ == "__main__":
	app.run(debug=True)
