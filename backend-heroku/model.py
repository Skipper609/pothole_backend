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
import time
import ast


def predictPotholes(raw):
	# data as : timestamp,accx,accy,accz,gyrx,gyry,gyrz,longitude,latitude,speed
	# print("Raw data : \n")
	# print(raw)

	start = time.time()

	df = pd.DataFrame(columns=['timestamp', 'accx', 'accy', 'accz','gyrx', 'gyry', 'gyrz', 'latitude', 'longitude', 'speed'])

	# ast.literal_eval(raw)
	# print(ast)

	for r in raw:
		data = str(r).split(',')
		for j in range(len(data)):
			data[j] = float(data[j])
		df2 = pd.DataFrame(pd.DataFrame([data], columns=['timestamp', 'accx', 'accy', 'accz',
														 'gyrx', 'gyry', 'gyrz', 'latitude', 'longitude', 'speed']))
		df = df.append(df2)

		# for temp in ast:
		# 	data = str(raw.get(temp)).split(',')
		# 	for j in range(len(data)):
		# 		data[j] = float(data[j])
		# 	df2 = pd.DataFrame(pd.DataFrame([data], columns = ['timestamp', 'accx', 'accy', 'accz',
		# 		'gyrx', 'gyry', 'gyrz', 'latitude', 'longitude', 'speed'] ))
		# 	df = df.append(df2)
		# 	i = i + 1

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

		#adding max-min
		# mm_x = max_ax - min_ax
		# mm_y = max_ay - min_ay
		# mm_z = max_az - min_az


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

	#loading the model

	model_nn = load_model('model_nn_corrected')

	y_pred = model_nn.predict(x)
	y_p = [np.where(i == max(i)) for i in y_pred]
	# y_rec = [i[0][0] for i in y_p]
	pred = pd.DataFrame(y_p)

	loc = df_main[pred == 1]

	# return y_pred

	print('predictions: ', y_pred)



d = ["152282715954,-0.359523,-0.963649,9.872052,-0.0027938844,-0.009959412,-0.0050170897,12.92829731,77.62135371,0.0",
"152282715975,-0.5063217,-1.085083,9.581564,0.0067352294,0.031082153,0.0073196413,12.92829731,77.62135371,0.0",
"152282715996,-0.68674165,-0.9702301,9.76593,0.002949524,0.014346314,0.003413391,12.92829731,77.62135371,0.0",
"152282716018,-0.59402007,-1.0618728,9.67285,-4.6844484E-4,-0.029862976,3.5858154E-4,12.92829731,77.62135371,0.0",
"152282716039,-0.51134646,-0.86937106,9.524257,2.6245118E-4,-0.0020248413,-0.007220459,12.92829731,77.62135371,0.0",
"152282716060,-0.33332062,-0.50075835,9.929959,0.0286026,-0.052467346,-0.1149704,12.92829731,77.62135371,0.0",
"152282716081,-0.18149567,-0.6912262,10.0247135,-0.002053833,-0.09889221,-0.17092285,12.92829731,77.62135371,0.0",
"152282716102,-0.55740815,-1.0591233,9.730397,-0.006452942,-0.051246643,-0.1221756,12.92829731,77.62135371,0.0",
"152282716124,-0.58995056,-0.7199402,9.823842,0.0012405396,-0.04073944,0.015013123,12.92829731,77.62135371,0.0",
"152282716145,0.12048034,-0.52588195,9.914286,0.00868988,0.014959717,0.029057313,12.92829731,77.62135371,0.0",
"152282715954,-0.359523,-0.963649,9.872052,-0.0027938844,-0.009959412,-0.0050170897,12.92829731,77.62135371,0.0",
"152282715975,-0.5063217,-1.085083,9.581564,0.0067352294,0.031082153,0.0073196413,12.92829731,77.62135371,0.0",
"152282715996,-0.68674165,-0.9702301,9.76593,0.002949524,0.014346314,0.003413391,12.92829731,77.62135371,0.0",
"152282716018,-0.59402007,-1.0618728,9.67285,-4.6844484E-4,-0.029862976,3.5858154E-4,12.92829731,77.62135371,0.0",
"152282716039,-0.51134646,-0.86937106,9.524257,2.6245118E-4,-0.0020248413,-0.007220459,12.92829731,77.62135371,0.0",
"152282716060,-0.33332062,-0.50075835,9.929959,0.0286026,-0.052467346,-0.1149704,12.92829731,77.62135371,0.0",
"152282716081,-0.18149567,-0.6912262,10.0247135,-0.002053833,-0.09889221,-0.17092285,12.92829731,77.62135371,0.0",
"152282716102,-0.55740815,-1.0591233,9.730397,-0.006452942,-0.051246643,-0.1221756,12.92829731,77.62135371,0.0",
"152282716124,-0.58995056,-0.7199402,9.823842,0.0012405396,-0.04073944,0.015013123,12.92829731,77.62135371,0.0",
"152282716145,0.12048034,-0.52588195,9.914286,0.00868988,0.014959717,0.029057313,12.92829731,77.62135371,0.0"]
predictPotholes(d)
