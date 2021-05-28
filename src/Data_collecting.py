import pandas as pd
import subprocess 
import os
from datetime import datetime
from datetime import timedelta
import numpy as np

import Display as Disp # local import
import IHM # local import


#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
#                        This script collects received data
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#


class recup_data(object):

	def __init__(self, path_zip, date_d, date_f, Zip = True):

		self.path_zip = path_zip # data compressed directory
		self.folder_zipped = Zip 
		self.result_folder = '../res' # decompress the folder in this directory
		self.path = self.result_folder + '/Store_data' # where to find the data
		self.ihm_path = '../IHM'

		self.date_d = date_d
		self.date_f = date_f

		self.gps = {}
		self.autopilot = {}
		self.drix_status = {}
		self.gpu_state = {}
		self.iridium_status = {}
		self.phins = {}
		self.rc_command = {}
		self.telemetry = {}
		self.trimmer_status = {}
		self.diagnostics = {}

		self.data = {'gps' : self.gps, 'autopilot' : self.autopilot, 'drix_status' : self.drix_status, 'gpu_state' : self.gpu_state, 'iridium' : self.iridium_status, 'phins' : self.phins, 
						'rc_command' : self.rc_command, 'telemetry' : self.telemetry, 'trimmer_status' : self.trimmer_status, 'diagnostics' : self.diagnostics}

		print(" ")
		print("Recovering data")

		self.collect_data() # Recovering data
		self.msg_gps = self.MSG_gps() # Infos Recovering 
		self.msg_phins =  self.MSG_phins()

		print(' ')
		print("Saving plots")
		self.Save_plots() # Creation and saving of the graphs


	# - - - - - - - - - - - - - - - - - - - - - - - - 


	def collect_data(self):

		# = = = = = = = = = = = = = = = = 
		#         Data Recovery  
		# = = = = = = = = = = = = = = = =

		if self.folder_zipped:
			subprocess.run(["tar", "-xf", self.path_zip, '-C',self.result_folder])


		files = os.listdir(self.path)

		for f in files:

			path = self.path + '/' + f
			list_csv = os.listdir(path)
			# print(path)

			
			var = self.data[f]
			for name in list_csv:
				l = name.split('.')
				var[l[0]] = pd.read_csv(path + '/'+ name, na_filter=False)


		# = = = = = = = = = = = = = = = = 
		#       Data decompression  
		# = = = = = = = = = = = = = = = =

		# ~ ~ gps ~ ~

		self.rebuild_gps_data()


		# ~ ~ All others ~ ~

		for key in list(self.data.keys())[1:]: # in order to not consider self.gps  

			for sub_key in self.data[key]:

				self.data[key][sub_key] = self.rebuild_data(self.data[key][sub_key], sub_key)


	# - - - - - - - - - - - - - - - - - - - - - - - -  


	def rebuild_gps_data(self):

		self.encode_action = {'IdleBoot' : 0,'Idle' : 1,'goto' : 2,'follow_me' : 3,'box-in': 4,"path_following" : 5,"dds" : 6,
    	"gaps" : 7,"backseat" : 8,"control_calibration" : 9,"auv_following": 10,"hovering": 11,"auto_survey": 12}


		# ~ ~ ~ ~ gps ~ ~ ~ ~

		df0 = self.gps['gps']
		t0 = datetime.fromtimestamp(df0['t'][0])

		self.date_ini = t0

		# - - - - 

		list_t = [t0]

		for k in range(1,len(df0['l_lat'])):
			dt = int(df0['t'][k])
			time_delta = timedelta(hours = dt // 3600, minutes = (dt % 3600) // 60, seconds = dt % 60)
			list_t.append(list_t[-1] +  time_delta)

		df0 = df0.assign(Time=list_t)

		# - - - - 

		df0['fix_quality'] = self.lengthen_data(df0['fix_quality'])

		# - - - - 

		df0['l_diff'] = self.lengthen_data(df0['l_diff'])	

		l_diff = [float(x) for x in df0['l_diff']]
		list_dist = [np.round(np.sum(l_diff[:k]),3) for k in range(len(l_diff))]

		df0 = df0.assign(list_dist=list_dist)

		# - - - - 

		df0['action_type'] = self.lengthen_data(df0['action_type'])

		l = list(self.encode_action.keys())
		df0 = df0.assign(action_type_str=[l[int(float(k))] for k in df0['action_type']])

		# - - - - 

		list_t = [k.strftime('%H:%M') for k in df0['Time']]
		df0 = df0.assign(time = list_t)

		# - - - - 

		self.gps['gps'] = df0


		# ~ ~ ~ ~ speed ~ ~ ~ ~

		df1 = self.gps['speed']
		list_t1 = [datetime.fromtimestamp(k) for k in df1['t']]
		df1 = df1.assign(Time=list_t1)
		df1 = df1.assign(action_type_str=[l[int(float(k))] for k in df1['action_type']])

		# - - - - 

		list_dt = [df1['Time'][k+1] - df1['Time'][k] for k in range(len(df1['Time'])-1)]

		v = df1['y_speed'][len(df1['Time'])-1] # in m/s
		d = df1['y_dist'][len(df1['Time'])-1] # in kms
		d = d*1000 # m
		t = np.round(d/v) # t

		list_dt.append(timedelta(seconds=t))

		df1 = df1.assign(list_dt=list_dt)

		# - - - - 

		list_t = [k.strftime('%H:%M') for k in df1['Time']]
		list_index = [x for x in range(len(list_t))]
		list_knots = [np.round(x*1.9438,2) for x in df1['y_speed']]

		df1 = df1.assign(time = list_t)
		df1 = df1.assign(list_index = list_index)
		df1 = df1.assign(list_knots = list_knots)

		# - - - - 

		self.gps['speed'] = df1

		# ~ ~ ~ ~ dist ~ ~ ~ ~

		df2 = self.gps['dist']
		df2 = self.add_time(df2)

		# - - - - 

		list_t = [k.strftime('%H:%M') for k in df2['Time']]
		df2 = df2.assign(time = list_t)

		self.gps['dist'] = df2


		# ~ ~ ~ ~ Pie Chart ~ ~ ~ ~

		list_action_type = df1['action_type'].unique()
		L_name = df1['action_type_str'].unique()
		L_dist = []
		L_speed = []
		list_dt = []

		for k in list_action_type:
			df = df1[df1['action_type'] == k]
			L_dist.append(np.round(np.sum(df["y_dist"]),1))
			L_speed.append(np.round(np.mean(df["y_speed"]),1))
			list_dt.append(np.sum(df["list_dt"]))

		list_dt_str = [(str(x).split(" ")[-1]).split('.')[0] for x in list_dt]

		df = pd.DataFrame(list(zip(L_name, L_dist, L_speed, list_dt, list_dt_str)), columns =['Name', 'L_dist', 'L_speed', 'list_dt', 'list_dt_str'])

		self.gps['pie_chart'] = df

	# - - - - - - - - - - - - - - - - - - - - - - - - 


	def rebuild_data(self, df, key):

		col = df.columns.tolist()
		
		# print(key)
		df = self.add_time(df)


		if len(col) > 2:

			if 'y_min' in col and 'y_max' in col: # it's a sawtooth curve
				y_mean = [(df['y_max'][0] + df['y_min'][0])/2]

				for k in range(1,len(df['y_max'])):
					y_mean.append((df['y_max'][k] + df['y_min'][k])/2)

				df = df.assign(y_mean=y_mean)

		return(df)


	# - - - - - - - - - - - - - - - - - - - - - - - - 

	def MSG_gps(self):

		if self.gps['gps'] is not None:

			N = len(self.gps['gps'])
			G_dist = self.gps['gps']['list_dist'][N - 1] # in kms
			Dt = (self.gps['gps']["Time"][N-1] - self.gps['gps']['Time'][0]).total_seconds() # in s

			if Dt != 0:
				G_speed = (G_dist*1000)/Dt # in m/s
				G_knots = G_speed*1.9438 # in knots/s

			else:
				G_speed = 0 # in m/s
				G_knots = 0 # in knots/s


			if "path_following" in self.gps["pie_chart"]['Name'].tolist():
				path_following_dist = self.gps["pie_chart"][self.gps["pie_chart"]['Name'] == 'path_following']['L_dist'].item()
				path_following_speed = self.gps["pie_chart"][self.gps["pie_chart"]['Name'] == 'path_following']['L_speed'].item()
				path_following_dt = self.gps["pie_chart"][self.gps["pie_chart"]['Name'] == 'path_following']['list_dt_str'].item()

			else: 
				path_following_dist = 0
				path_following_speed = 0
				path_following_dt = 0


			return({"global_dist":np.round(G_dist,1),"global_speed":np.round(G_speed,1),"global_knots":np.round(G_knots,1), "path_following_dist" : path_following_dist, "path_following_speed" : path_following_speed, 'path_following_dt' : path_following_dt})

	# - - - - - - 

	def MSG_phins(self):

		if self.phins:

			p_min = np.round(np.min(self.phins['pitchDeg']['y_min']),1)
			p_mean = np.round(np.mean(self.phins['pitchDeg']['y_mean']),1)
			p_max = np.round(np.max(self.phins['pitchDeg']['y_max']),1)

			# - - -

			r_min = np.round(np.min(self.phins['rollDeg']['y_min']),1)
			r_mean = np.round(np.mean(self.phins['rollDeg']['y_mean']),1)
			r_max = np.round(np.max(self.phins['rollDeg']['y_max']),1)
		
			return({"pitch_min" : p_min, "pitch_mean" : p_mean, "pitch_max" : p_max, "roll_min" : r_min,"roll_mean" : r_mean, "roll_max" : r_max})


	# - - - - - - - - - - - - - - - - - - - - - - - - 

	def Save_plots(self):

		Disp.plot_gps(self)
		Disp.plot_drix_status(self)
		Disp.plot_phins(self)
		Disp.plot_telemetry(self)
		Disp.plot_gpu_state(self)
		Disp.plot_trimmer_status(self)
		Disp.plot_iridium_status(self)
		Disp.plot_autopilot(self)
		Disp.plot_rc_command(self)
		Disp.plot_diagnostics(self)

		return()

	# - - - - - - - - Tools Functions - - - - - - - -


	def lengthen_data(self, list_msg): # (4, None, None, 5) -> (4, 4, 4, 5)

		list_x = [list_msg[0]]

		for k in list_msg[1:]:
			if not k:
				list_x.append(list_x[-1])
			else:
				list_x.append(k)

		return(list_x)


	# - - - - - - - - 


	def add_time(self, df):

		time_ini = self.date_ini.strftime('%Y:%m-') 

		l_n = [len(df[k]) for k in df.columns.tolist()]
		N = np.max(l_n)

		list_t_cleaned = [x for x in df['t'] if str(x) != '']


		if len(list_t_cleaned) == 1:
			date0 = datetime.strptime(time_ini + list_t_cleaned[0], '%Y:%m-' + '%d:%H:%M:%S')
			df = df.assign(Time=[date0])


		if len(list_t_cleaned) == 2:

			if len(df['t'][1].split(':')) == 1:

				date0 = datetime.strptime(time_ini + list_t_cleaned[0], '%Y:%m-' + '%d:%H:%M:%S')
				list_t = [date0]

				dt = int(list_t_cleaned[1])
				time_delta = timedelta(hours = dt // 3600, minutes = (dt % 3600) // 60, seconds = dt % 60)

				for k in range(1,N):
					list_t.append(list_t[-1] +  time_delta)

				df = df.assign(Time=list_t)


			else:
				date0 = datetime.strptime(time_ini + list_t_cleaned[0], '%Y:%m-' + '%d:%H:%M:%S')
				date1 = datetime.strptime(time_ini + list_t_cleaned[1], '%Y:%m-' + '%d:%H:%M:%S')

				df = df.assign(Time=[date0,date1])

		if len(list_t_cleaned) > 2:

			if len(df['t'][2].split(':')) > 1:
			# if len(list_t_cleaned) == N:
				list_t = []
				for k in list_t_cleaned:
					list_t.append(datetime.strptime(time_ini + k, '%Y:%m-' + '%d:%H:%M:%S'))


			else:
				date0 = datetime.strptime(time_ini + list_t_cleaned[0], '%Y:%m-' + '%d:%H:%M:%S')
				list_t = [date0]

				dt = int(list_t_cleaned[1])
				time_delta = timedelta(hours = dt // 3600, minutes = (dt % 3600) // 60, seconds = dt % 60)

				for k in range(1,N):

					if not df['t'][k]:
						list_t.append(list_t[-1] +  time_delta)

					else:
						dt = int(df['t'][k])
						time_delta = timedelta(hours = dt // 3600, minutes = (dt % 3600) // 60, seconds = dt % 60)
						list_t.append(list_t[-1] +  time_delta)

			
			df = df.assign(Time=list_t)

		return(df)





if __name__ == '__main__':

	date_d = "01-02-2021-09-00-00"
	date_f = "01-02-2021-15-00-00"

	path_zip = '../../data.tar.xz'

	Data = recup_data(path_zip, date_d, date_f)

	IHM.generate_ihm3000(Data)

	print("Done")



# embedable_chart = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

# self.gps_encoder = ['dist', 'gps', 'speed']
# self.autopilot_encoder = ['ActiveSpeed', 'Delta', 'Regime', 'Speed', 'speed_autopilot', 'yawRate']
# self.drix_status_encoder = ['emergency_mode', 'drix_mode', 'reboot_requested', 'drix_clutch', 'remoteControlLost', 'gasolineLevel_percent', 'keel_state', 'rudderAngle_deg', 'thruster_RPM', 'shutdown_requested']
# self.gpu_state_encoder = ['total_mem_GB', 'power_consumption_W', 'gpu_utilization_percent', 'mem_utilization_percent', 'temperature_deg_c']
# self.iridium_encoder = ['is_iridium_link_ok', 'mt_length', 'cmd_queue', 'mt_status_code', 'signal_strength', 'last_mo_msg_sequence_number', 'gss_queued_msgs', 'failed_transaction_percent', 'mo_status_code', 'mt_msg_sequence_number', 'registration_status']
# self.phins_encoder = ['phins']
# self.rc_command_encoder = ['reception_mode']
# self.telemetry_encoder = ['engineon_hours_h', 'current_backup_battery_A', 'is_fans_on', 'is_oil_pressure_alarm_on', 'electronics_water_ingress', 'consumed_current_backup_battery_Ah', 'is_foghorn_on', 'backup_battery_voltage_V', 'is_water_in_fuel_on', 'electronics_fire_on_board', 'engine_battery_voltage_V', 'engine_water_ingress', 'percent_main_battery', 'time_left_main_battery_mins', 'is_navigation_lights_on', 
# 'engine_temperature_deg', 'percent_backup_battery', 'main_battery_voltage_V', 'time_left_backup_battery_mins', 'is_drix_started', 'electronics_temperature_deg', 'electronics_hygrometry_percent', 'current_main_battery_A', 'engine_hygrometry_percent', 'engine_water_temperature_deg', 'consumed_current_main_battery_Ah', 'engine_fire_on_board', 'is_water_temperature_alarm_on', 'oil_pressure_Bar']
# self.trimmer_status_encoder = ['power_consumption_A', 'relative_humidity_percent', 'motor_temperature_degC', 'pcb_temperature_degC']
# self.diagnostics_encoder = []

# self.gps = dict(zip(self.gps_encoder, len(self.gps_encoder)*[None]))
# # self.autopilot = dict(zip(self.autopilot_encoder, len(self.autopilot_encoder)*[None]))
# self.autopilot = {}
# self.drix_status = dict(zip(self.drix_status_encoder, len(self.drix_status_encoder)*[None]))
# self.gpu_state = dict(zip(self.gpu_state_encoder, len(self.gpu_state_encoder)*[None]))
# self.iridium = dict(zip(self.iridium_encoder, len(self.iridium_encoder)*[None]))
# self.phins = dict(zip(self.phins_encoder, len(self.phins_encoder)*[None]))
# self.rc_command = dict(zip(self.rc_command_encoder, len(self.rc_command_encoder)*[None]))
# self.telemetry = dict(zip(self.telemetry_encoder, len(self.telemetry_encoder)*[None]))
# self.trimmer_status = dict(zip(self.trimmer_status_encoder, len(self.trimmer_status_encoder)*[None]))
# self.diagnostics = {}