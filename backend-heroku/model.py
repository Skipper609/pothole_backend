import pandas as pd
import numpy as np
import scipy.fftpack
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
import itertools
import pickle
import requests
import json
from datetime import datetime,timedelta
import ast
from pymongo import MongoClient
import threading
import re
import time
import bson
import warnings
from Geolocation import GeoLocation

client = ""
db =""
model_nn =""
REFRESH_TIME = 30 #in minutes
def initialize():
	global model_nn,client,db
	model_nn = load_model('model_nn_corrected.h5py')
	url="mongodb+srv://dbuser:dbuser@cluster0-cw2oj.mongodb.net/test?retryWrites=true&w=majority"
	client=MongoClient(url)
	db = client.Pothole_Details
	warnings.simplefilter("ignore")
	refreshPotholeInformation()


def storePoints(locationList):
	collection = db.Pothole_Holder
	for location in locationList:
		loc = {
			"longitude":location[1],
			"latitude":location[0],
			"time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		}
		collection.insert_one(loc)

def refreshPotholeInformation():
	pothole = db.Pothole_Information
	holding = db.Pothole_Holder
	nowTime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	start = time.perf_counter()

	points = holding.aggregate([
		{"$group" : {"_id":{"longitude" : "$longitude","latitude" : "$latitude"},"count":{"$sum":1},"time":{"$first": "$time"}}},
		{"$project" : {"longitude":"$_id.longitude","latitude":"$_id.latitude","count":1,"_id":0,"time":1}}
	])
	res = [i for i in points]
	
	for p in res:
		res = pothole.find({"latitude":p["latitude"],"longitude":p["longitude"]})
		res = [i for i in res]
		if len(res) > 0:
			pothole.update_one({"latitude":p["latitude"],"longitude":p["longitude"]},{
				"$set" :{"last report":p["time"]},
				"$push" : {"reports": {"time":nowTime,"count":p["count"]}},
				"$inc" : {"reportCount":p["count"]}
			})
		else:
			pothole.insert_one({
				"Time of First report" : p["time"],
				"longitude":p["longitude"],
				"latitude":p["latitude"],
				"reports":[{"time":nowTime,"count":p["count"]}],
				"reportCount":p["count"],
				"last report":p["time"]
			})
	holding.delete_many({})
	end = time.perf_counter()
	threading.Timer(REFRESH_TIME * 60 - (end - start), refreshPotholeInformation).start()

def getPotholes(latitude, longitude, radius,day):
	#Radius in KMs
	min,max = GeoLocation.from_degrees(latitude,longitude).bounding_locations(radius)
	pothole = db.Pothole_Information
	lastdate = datetime.now() - timedelta(day)
	lastdate = lastdate.__str__()
	res = pothole.find({
		"latitude":{"$gt":min.deg_lat,"$lt":max.deg_lat},
		"longitude":{"$gt":min.deg_lon,"$lt":max.deg_lon},
		"last report":{"$gt":lastdate}
	},
	{"_id":0,"reports":0,"Time of First report":0})
	r = [i for i in res]
	# print(r)
	return r


def predictPotholes(raw):


	df = pd.DataFrame(columns=['timestamp', 'accx', 'accy', 'accz','gyrx', 'gyry', 'gyrz', 'latitude', 'longitude', 'speed'])
	for r in raw:
		data = str(r).split(',')
		for j in range(len(data)):
			data[j] = float(data[j])
		df2 = pd.DataFrame(pd.DataFrame([data], columns=['timestamp', 'accx', 'accy', 'accz',
														 'gyrx', 'gyry', 'gyrz', 'latitude', 'longitude', 'speed']))
		df = df.append(df2)


		# run only once after insering all data to reset index
		df = df.reset_index(drop=True)

	df_main = pd.read_csv('./features.txt')

		# making features for new data
		# step size is 10 means aggregrating 10 data pts means 1 second data

	
	for i in range(0, len(df), 10):
		# step size is 10 means aggregrating 10 data pts means 1 second data
		if(i+9 >= len(df)):
			break
		dt = df[i:i+11]      # chunking the given dataframe into smaller dataframe containing 10 pts
		start = dt.timestamp[i]
		end = dt.timestamp[i+9]

		# time-domain features : mean , max , min , var , std dev, median , interquartile range,
		#                       mean of abs deviation , skewness < left : root mean sq error , entropy       
		# mean 
		a = dt.mean()      # will give an array of mean of columns of dt
		mean_ax = a[1]
		mean_ay = a[2]
		mean_az = a[3]

		mean_gx = a[4]
		mean_gy = a[5]
		mean_gz = a[6]

		# min
		a = dt.min()
		min_ax = a[1]
		min_ay = a[2]
		min_az = a[3]

		min_gx = a[4]
		min_gy = a[5]
		min_gz = a[6]

		# max
		a = dt.max()
		max_ax = a[1]
		max_ay = a[2]
		max_az = a[3]

		max_gx = a[4]
		max_gy = a[5]
		max_gz = a[6]

		# std dev
		a = dt.std()
		sd_ax = a[1]
		sd_ay = a[2]
		sd_az = a[3]

		sd_gx = a[4]
		sd_gy = a[5]
		sd_gz = a[6]

		# variance
		a = dt.var()
		var_ax = a[1]
		var_ay = a[2]
		var_az = a[3]

		var_gx = a[4]
		var_gy = a[5]
		var_gz = a[6]

		# median coln wise of acc data
		a = dt.median()
		med_ax = a[1]
		med_ay = a[2]
		med_az = a[3]

		med_gx = a[4]
		med_gy = a[5]
		med_gz = a[6]

		# entropy coln wise of acc data

		# interquantile ranges
		a = dt.quantile(.25)
		quant1_ax = a[1]
		quant1_ay = a[2]
		quant1_az = a[3]

		quant1_gx = a[4]
		quant1_gy = a[5]
		quant1_gz = a[6]

		a = dt.quantile(.5)
		quant2_ax = a[1]
		quant2_ay = a[2]
		quant2_az = a[3]

		quant2_gx = a[4]
		quant2_gy = a[5]
		quant2_gz = a[6]

		a = dt.quantile(.75)
		quant3_ax = a[1]
		quant3_ay = a[2]
		quant3_az = a[3]

		quant3_gx = a[4]
		quant3_gy = a[5]
		quant3_gz = a[6]


		# mean absolute deviation
		a = dt.mad()
		mad_ax = a[1]
		mad_ay = a[2]
		mad_az = a[3]

		mad_gx = a[4]
		mad_gy = a[5]
		mad_gz = a[6]

		# skewness 
		a = dt.skew()
		skew_ax = a[1]
		skew_ay = a[2]
		skew_az = a[3]

		skew_gx = a[4]
		skew_gy = a[5]
		skew_gz = a[6]


		# gradient based features : gradient with respect to timestamp

		#taking gradients
		arx = dt['accx']
		ary = dt['accy']
		arz = dt['accz']

		grx = dt['gyrx']
		gry = dt['gyry']
		grz = dt['gyrz']

		tm = dt['timestamp']
		adx = np.gradient(arx, tm).max()
		ady = np.gradient(ary, tm).max()
		adz = np.gradient(arz, tm).max()
		gdx = np.gradient(grx, tm).max()
		gdy = np.gradient(gry, tm).max()
		gdz = np.gradient(grz, tm).max()


		# frequency domain features : fft , spectral energy ,   

		#taking fourier transforms
		ft = scipy.fftpack.fft(dt)

		fft_ax = ft[1].max().imag
		fft_ay = ft[2].max().imag
		fft_az = ft[3].max().imag

		

		#getting spectral energy
		sp_ax = np.mean(np.square(ft[1].real) + np.square(ft[1].imag))
		sp_ay = np.mean(np.square(ft[2].real) + np.square(ft[2].imag))
		sp_az = np.mean(np.square(ft[3].real) + np.square(ft[3].imag))


		# adding latitude and longitude
		latitude = dt['latitude'][i+4]
		longitude = dt['longitude'][i+4]

		df_temp = pd.DataFrame([[start,end,mean_ax,mean_ay,mean_az,mean_gx,mean_gy,mean_gz,sd_ax,
								 sd_ay,sd_az,sd_gx,sd_gy,sd_gz,min_ax,min_ay,min_az,min_gx,min_gy,min_gz,
								 max_ax,max_ay,max_az,max_gx,max_gy,max_gz,var_ax,var_ay,var_az,var_gx,var_gy,
								 var_gz,med_ax,med_ay,med_az,med_gx,med_gy,med_gz,quant1_ax,quant1_ay,quant1_az
								 ,quant1_gx,quant1_gy,quant1_gz,quant2_ax,quant2_ay,quant2_az,quant2_gx,
								 quant2_gy,quant2_gz,quant3_ax,quant3_ay,quant3_az,quant3_gx,quant3_gy,
								 quant3_gz,mad_ax,mad_ay,mad_az,mad_gx,mad_gy,mad_gz,skew_ax,skew_ay,
								 skew_az,skew_gx,skew_gy,skew_gz,adx,ady,adz,gdx,gdy,gdz,fft_ax,fft_ay,fft_az,
								 sp_ax,sp_ay,sp_az, latitude, longitude]], 

							  columns = ('ts_start','ts_end','mean_ax','mean_ay','mean_az','mean_gx','mean_gy',
										 'mean_gz','sd_ax','sd_ay','sd_az','sd_gx','sd_gy','sd_gz','min_ax','min_ay'
										 ,'min_az',
										 'min_gx','min_gy','min_gz','max_ax','max_ay','max_az','max_gx','max_gy','max_gz',
										 'var_ax','var_ay','var_az','var_gx','var_gy','var_gz','med_ax','med_ay'
										 ,'med_az','med_gx',
										 'med_gy','med_gz','quant1_ax','quant1_ay','quant1_az','quant1_gx',
										 'quant1_gy',
										 'quant1_gz','quant2_ax','quant2_ay','quant2_az','quant2_gx','quant2_gy'
										 ,
										 'quant2_gz','quant3_ax','quant3_ay','quant3_az','quant3_gx','quant3_gy',
										 'quant3_gz',
										 'mad_ax','mad_ay','mad_az','mad_gx','mad_gy','mad_gz','skew_ax',
										 'skew_ay','skew_az',
										 'skew_gx','skew_gy','skew_gz','adx','ady','adz','gdx','gdy','gdz'
										 ,'fft_ax','fft_ay','fft_az',
										 'sp_ax','sp_ay','sp_az', 'latitude', 'longitude'))

		df_main = df_main.append(df_temp)


	# putting time stamps at the end
	cols = list(df_main.columns.values) #Make a list of all of the columns in the df
	cols.pop(cols.index('ts_start')) #Remove b from list
	cols.pop(cols.index('ts_end')) #Remove x from list
	cols.pop(cols.index('latitude')) # remove latitude
	cols.pop(cols.index('longitude')) # remove longitude
	df_main = df_main[cols+['ts_start','ts_end', 'latitude', 'longitude']]

	df_main['fft_ax'] = preprocessing.scale(df_main['fft_ax'])
	df_main['fft_ay'] = preprocessing.scale(df_main['fft_ay'])
	df_main['fft_az'] = preprocessing.scale(df_main['fft_az'])
	

	df_main['sp_ax'] = preprocessing.scale(df_main['sp_ax'])
	df_main['sp_ay'] = preprocessing.scale(df_main['sp_ay'])
	df_main['sp_az'] = preprocessing.scale(df_main['sp_az'])


	data = np.array(df_main)

	x = data[:,0:-4]

	# Data-preprocessing: Standardizing the data matrix 'x'
	standardized_data = StandardScaler().fit_transform(x)
	# coln std our feature matrix 
	x = standardized_data

	y_pred = model_nn.predict(x)
	y_p = [np.where(i == max(i)) for i in y_pred]
	y_rec = [i[0][0] for i in y_p]

	loc = np.array([df_main['latitude'],df_main['longitude']])
	
	# print(y_rec)
	# print(loc)
	
	# mapping the pothole details with location
	finalRes = []
	for i in range(len(y_rec)):
		if y_rec[i] == 1:
			finalRes.append([loc[0][i],loc[1][i]])
	
	# adding the location to holding table
	if len(finalRes) > 0:
		storePoints(finalRes)
	
	# return y_pred


# storePoints([[11,11],[12,12],[12,12]])
# refreshPotholeInformation()