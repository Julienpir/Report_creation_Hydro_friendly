import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3
from plotly.subplots import make_subplots
from sklearn import preprocessing
from mpld3 import plugins
from mpld3 import utils
from mpld3.utils import get_id
import collections.abc
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly

import IHM # local import

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
#					This script handles all the data graph function
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#


# = = = = = = = = = = = = = = = = = =  /gps  = = = = = = = = = = = = = = = = = = = = = = = =

def plot_gps(Data):

	dic_color = {'IdleBoot' : 'blue','Idle' : 'cyan','goto' : 'magenta','follow_me' : "#636efa",'box-in': "#00cc96","path_following" : "#66AA00","dds" : "darkred",
	"gaps" : "turquoise","backseat" : "blueviolet","control_calibration" : "teal","auv_following": "seagreen","hovering": "sienna","auto_survey": "grey"}

	# - - - - - GNSS position graph - - - - - -

	df1 = Data.gps['gps']
	
	list_hover_data1 =['time','action_type_str','list_dist_mship','list_dist','fix_quality']
	title1 = "Gnss positions"

	fig1 = px.scatter(df1, x='l_long', y='l_lat', hover_data = list_hover_data1, color = "action_type_str", title = title1, color_discrete_map=dic_color, labels={
	                      "l_long": "Longitude (rad)",
	                      "l_lat": "Latitude (rad)",
	                      "fix_quality": "GPS quality",
	                      "action_type_str" : "action type",
	                      "list_dist_mship" : "Dist Drix/ship",
	                      'list_dist' : 'Travelled distance',
	                      'time' : 'Time' ,
	                      "color": 'Mission type'})
	fig1.update_yaxes(scaleanchor = "x",scaleratio = 1)

	
	# - - - - - Distance travelled graph - - - - - -

	df2 = Data.gps['dist']
	
	title2 = 'Distance evolution'

	fig2 = px.line(df2, x="Time", y="y", title= title2, labels={"y": "Travelled distance (km)", 'time' : 'Time'})
	fig2.update_layout(hovermode="y")


	# - - - - - Speed Bar chart - - - - - -

	df3 = Data.gps['speed']
	
	title3 = 'Speed history'

	fig3 = px.bar(df3, y='y_speed', x='list_index',hover_data =['action_type_str','list_knots'], color = 'action_type_str', color_discrete_map=dic_color, title = title3,
		labels={     "y_speed": "Drix speed (m/s)",
					 "list_knots": "Drix speed (knot)",
                     "action_type_str" : "Action type",
                     'list_index' : 'Time'})

	fig3.update_layout(xaxis = dict(tickmode = 'array', tickvals = df3['list_index'],ticktext = df3['time']))




	# - - - - - Mission Distance Bar graph - - - - - -
	
	title4 = 'Mission Distance history'

	fig4 = px.bar(df3, y='y_dist', x='list_index',hover_data =['action_type_str','y_speed'], color = 'action_type_str', color_discrete_map=dic_color, title = title4,
		labels={     "y_dist": "Mission distance (kms)",
					 "y_speed": "Drix speed (m/s)",
                     "action_type_str" : "Action type",
                     'list_index' : 'Time'})

	fig4.update_layout(xaxis = dict(tickmode = 'array', tickvals = df3['list_index'],ticktext = df3['time']))


	# - - - - - Distance Pie chart - - - - - -

	title5 = "Mission distance"

	df4 = Data.gps['pie_chart']

	fig5 = px.pie(df4, values= 'L_dist', names= 'Name', color = 'Name', color_discrete_map=dic_color, title = title5,labels={"L_dist": "Mission distance (kms)",
                     "Name" : "Action type"})

	plotly.offline.plot(fig5, filename= Data.ihm_path + '/gps/pie3000.html', auto_open=False)



	# - - - - - Global Plot - - - - - -

	Fig = make_subplots(rows=4, cols=1,shared_xaxes=False, subplot_titles = [title1,title2,title3,title4], row_width=[0.8, 0.8, 0.8,1.5])

	for f in fig1["data"]:
		Fig.add_trace(f,row=1, col=1)

	for f in fig2["data"]:
		Fig.add_trace(f,row=2, col=1)

	for f in fig3["data"]:
		Fig.add_trace(f,row=3, col=1)

	for f in fig4["data"]:
		Fig.add_trace(f,row=4, col=1)

	# - - - - - 

	names = set()
	Fig.for_each_trace(
    lambda trace:
        trace.update(showlegend=False)
        if (trace.name in names) else names.add(trace.name))


	# - - - - - 

	Fig.update_layout(height=1400, width=1400, title_text="GPS Data")
	Fig.update_layout(legend_traceorder="reversed")
	Fig.update_layout(showlegend=True)
	Fig.layout.legend.itemsizing = 'constant'

	# - - - 

	Fig.update_layout(yaxis1 = dict(title="Latitude (rad)"))
	Fig.update_layout(xaxis1 = dict(title="Longitude (rad)"))

	Fig.update_layout(yaxis2 = dict(title="Travelled distance (km)"))
	Fig.update_layout(xaxis2 = dict(title="Time"))

	Fig.update_layout(yaxis3 = dict(title="Travelled distance (km)"))
	Fig.update_layout(xaxis3 = dict(tickangle = 45, tickmode = 'array', tickvals = df3['list_index'],ticktext = df3['time']),
		uniformtext_minsize=8, uniformtext_mode='hide', title= 'Time')

	Fig.update_layout(yaxis4 = dict(title="Drix speed (m/s)"))
	Fig.update_layout(xaxis4 = dict(tickangle = 45, tickmode = 'array', tickvals = df3['list_index'],ticktext = df3['time']),
		uniformtext_minsize=8, uniformtext_mode='hide',title= 'Time')

	# - - - - - 

	# fig1.show()
	# fig2.show()
	# fig3.show()
	# fig4.show()
	# Fig.show()
	# fig5.show()

	# - - - - - 

	# plotly.offline.plot(Fig, filename= Data.ihm_path + '/gps/Bilan_gps3000.html', auto_open=False)

	IHM.html_gps(Data, 'GPS Data', [Fig, fig5], '/gps/Bilan_gps3000.html')


# = = = = = = = = = = = = = = = =  /drix_status  = = = = = = = = = = = = = = = = = = = = = = = =

def plot_drix_status(Data):

	Title = ['Thruster RPM', 'rudderAngle_deg', 'Gasoline Level (%)', 'Emergency mode', 'Remote Control Lost RPM', 'Shutdown requested', 'Reboot requested', 'Drix Mode', 'Drix Clutch', 'Keel state']

	if not Data.drix_status:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:

		fig0 = normal_plot(Data.drix_status['thruster_RPM'], Title[0])
		fig1 = normal_plot(Data.drix_status['rudderAngle_deg'],Title[1])
		fig2 = normal_plot(Data.drix_status['gasolineLevel_percent'],Title[2])

		fig3 = Binary_plot(Data.drix_status['emergency_mode'], Title[3], default_value=False)
		fig4 = Binary_plot(Data.drix_status['remoteControlLost'],Title[4], default_value=False)
		fig5 = Binary_plot(Data.drix_status['shutdown_requested'],Title[5], default_value=False)
		fig6 = Binary_plot(Data.drix_status['reboot_requested'],Title[6], default_value=False)

		fig7 = normal_plot(Data.drix_status['drix_mode'], Title[7], y_axis = {"DOCKING":0,"MANUAL":1,"AUTO":2})
		fig8 = normal_plot(Data.drix_status['drix_clutch'], Title[8], y_axis = {"FORWARD":0,"NEUTRAL":1,"BACKWARD":2,"ERROR":4})
		fig9 = normal_plot(Data.drix_status['keel_state'], Title[9], y_axis = {"DOWN":0,"MIDDLE":1,"UP":2,"ERROR":4,"GOING UP ERROR":5,"GOING DOWN ERROR":6,"UP AND DOWN ERROR":7})

		L = [fig0,fig1,fig2,fig3,fig4,fig5,fig6,fig7,fig8,fig9]
		Red_line = False

	IHM.html_page_creation(Data, 'Drix status', L, '/drix_status/Bilan_drix_status3000.html')

	# Fig = merge_plots(L, 'Drix Status Data', red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/drix_status/Bilan_drix_status3000.html', auto_open=False)



# = = = = = = = = = = = = = = = = = = = /d_phins/aipov  = = = = = = = = = = = = = = = = = = = = = = = =

def plot_phins(Data):

	Title = ['Heading (deg)', 'Pitch (deg)', 'Roll (deg)']

	if not Data.phins:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:
		fig0 = normal_plot(Data.phins['headingDeg'],Title[0])
		fig1 = normal_plot(Data.phins['pitchDeg'],Title[1])
		fig2 = normal_plot(Data.phins['rollDeg'],Title[2])

		L = [fig0,fig1,fig2]
		Red_line = False

	Fig = merge_plots(L, 'Phins Data', Height = 350, red_line = Red_line)

	# Fig.update_layout(hovermode='y unified')
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/phins/Bilan_phins3000.html', auto_open=False)

	IHM.html_phins(Data, 'Drix status', L, '/phins/Bilan_phins3000.html')



# = = = = = = = = = = = = = = = = = = /Telemetry2  = = = = = = = = = = = = = = = = = = = = = = = = = 

def plot_telemetry(Data):

	Title = ['Drix is started', 'Navigation lights', 'Foghorn', "Fans", 'Water temperature alarm', 'Oil pressure alarm', 'Water in fuel', 'Electronics water ingress', 'Electronics fire on board', 'Engine Water Ingress', 'Engine fire on board',
		 'Oil Pressure (Bar)', 'Engine water temperature (deg)', 'Engine on hours','Main battery voltage (V)', 'Backup battery voltage (V)', 'Engine Battery Voltage (V)', 'Main battery (%)', 'Backup battery (%)', 
		 'Consumed current main battery (Ah)', 'Consumed current backup battery (Ah)', 'Current Main Battery (A)', 'Current Backup Battery (A)', 'Time Left Main Battery (mins)', 'Time Left Backup Battery (mins)', 'Electronics Temperature (deg)', 'Electronics Hygrometry (%)', 'Electronics Hygrometry (%)', 'Engine Hygrometry (%)']
		
	if not Data.telemetry:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else: 
		print('-------------------')
		print("Data.telemetry : ",Data.telemetry.keys())
		print('-------------------')
		
		fig0 = Binary_plot(Data.telemetry['is_drix_started'], Title[0], default_value=True)
		fig1 = Binary_plot(Data.telemetry['is_navigation_lights_on'], Title[1], default_value=False)
		fig2 = Binary_plot(Data.telemetry['is_foghorn_on'], Title[2], default_value=False)
		fig3 = Binary_plot(Data.telemetry['is_fans_on'], Title[3], default_value=True)
		fig4 = Binary_plot(Data.telemetry['is_water_temperature_alarm_on'], Title[4], default_value=False)
		fig5 = Binary_plot(Data.telemetry['is_oil_pressure_alarm_on'], Title[5], default_value=False)
		fig6 = Binary_plot(Data.telemetry['is_water_in_fuel_on'],Title[6], default_value=False)
		fig7 = Binary_plot(Data.telemetry['electronics_water_ingress'], Title[7], default_value=False)
		fig8 = Binary_plot(Data.telemetry['electronics_fire_on_board'], Title[8], default_value=False)
		fig9 = Binary_plot(Data.telemetry['engine_water_ingress'], Title[9], default_value=False)
		fig10 = Binary_plot(Data.telemetry['engine_fire_on_board'], Title[10], default_value=False)

		fig11 = normal_plot(Data.telemetry['oil_pressure_Bar'], Title[11])
		fig12 = normal_plot(Data.telemetry['engine_water_temperature_deg'],Title[12])
		fig13 = normal_plot(Data.telemetry['engineon_hours_h'],Title[13])
		fig14 = normal_plot(Data.telemetry['main_battery_voltage_V'],Title[14])
		fig15 = normal_plot(Data.telemetry['backup_battery_voltage_V'], Title[15])
		fig16 = normal_plot(Data.telemetry['engine_battery_voltage_V'], Title[16])
		fig17 = normal_plot(Data.telemetry['percent_main_battery'], Title[17])
		fig18 = normal_plot(Data.telemetry['percent_backup_battery'], Title[18])

		fig19 = normal_plot(Data.telemetry['consumed_current_main_battery_Ah'], Title[19])
		fig20 = normal_plot(Data.telemetry['consumed_current_backup_battery_Ah'], Title[20])
		fig21 = normal_plot(Data.telemetry['current_main_battery_A'], Title[21])
		fig22 = normal_plot(Data.telemetry['current_backup_battery_A'], Title[22])
		fig23 = normal_plot(Data.telemetry['time_left_main_battery_mins'], Title[23])
		fig24 = normal_plot(Data.telemetry['time_left_backup_battery_mins'], Title[24])
		fig25 = normal_plot(Data.telemetry['electronics_temperature_deg'], Title[25])
		fig26 = normal_plot(Data.telemetry['electronics_hygrometry_percent'], Title[26])
		fig27 = normal_plot(Data.telemetry['engine_temperature_deg'], Title[27])
		fig28 = normal_plot(Data.telemetry['engine_hygrometry_percent'], Title[28])

		L = [fig0,fig1,fig2,fig3,fig4,fig5,fig6,fig7,fig8,fig9,fig10,fig11,fig12,fig13,fig14,fig15,fig16,fig17,fig18,fig19,fig20,fig21,fig22,fig23,fig24,fig25,fig26,fig27,fig28]
		Red_line = False


	# Fig = merge_plots(L,'Telemetry Data', red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/telemetry/Bilan_telemetry3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Telemetry', L, '/telemetry/Bilan_telemetry3000.html')




# = = = = = = = = = = = = = = = = = = /gpu_state  = = = = = = = = = = = = = = = = = = = = = = = = = 

def plot_gpu_state(Data):

	Title = ['GPU Temperature (deg)', 'GPU Utilization (deg)', 'GPU memory utilization (%)', 'GPU Total Memory (GB)', 'GPU Power Consumption (W)', 'GPU Power Consumption (W)']

	if not Data.gpu_state:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:

		fig0 = normal_plot(Data.gpu_state['temperature_deg_c'], Title[0])
		fig1 = normal_plot(Data.gpu_state['gpu_utilization_percent'], Title[1])
		fig2 = normal_plot(Data.gpu_state['mem_utilization_percent'], Title[2])
		fig3 = normal_plot(Data.gpu_state['total_mem_GB'], Title[3])
		fig4 = normal_plot(Data.gpu_state['power_consumption_W'], Title[4])
		fig5 = normal_plot(Data.gpu_state['power_consumption_W'], Title[5])

		L = [fig0, fig1,fig2,fig3,fig4,fig5]
		Red_line = False

	# Fig = merge_plots(L,'Gpu State', red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/gpu_state/Bilan_gpu_state3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Gpu State', L, '/gpu_state/Bilan_gpu_state3000.html')





# = = = = = = = = = = = = = = = = = = /trimmer_status  = = = = = = = = = = = = = = = = = = = = = = = = = 

def plot_trimmer_status(Data):

	Title = ['Primary Powersupply Consumption (A)', 'Secondary Powersupply Consumption (A)', 'Motor Temperature (deg)', 'PCB Temperature (deg)', 'Relative Humidity (%)']

	if not Data.gpu_state:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:
		fig0 = normal_plot(Data.trimmer_status['primary_powersupply_consumption_A'], Title[0])
		fig1 = normal_plot(Data.trimmer_status['secondary_powersupply_consumption_A'], Title[1])
		fig2 = normal_plot(Data.trimmer_status['motor_temperature_degC'], Title[2])
		fig3 = normal_plot(Data.trimmer_status['pcb_temperature_degC'], Title[3])
		fig4 = normal_plot(Data.trimmer_status['relative_humidity_percent'], Title[4])

		L = [fig0,fig1,fig2,fig3,fig4]
		Red_line = False

	# Fig = merge_plots(L,'Trimmer Status', red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/trimmer_status/Bilan_trimmer_status3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Trimmer status', L, '/trimmer_status/Bilan_trimmer_status3000.html')


# = = = = = = = = = = = = = = = = = = /d_iridium/iridium_status  = = = = = = = = = = = = = = = = = = = = = = = = = 

def plot_iridium_status(Data):

	Title = ['Iridium link state', 'Signal strength', 'Registration status', 'MO = mobile originated = outgoing messages from modem to sattelites (GSS), mo_status_code', 'last_mo_msg_sequence_number',
	 'MT = Mobile Terminated = incoming messages from modem to sattelites (GSS), mt_status_code', 'Mobile Terminated Message Sequence Number is assigned by the GSS when forwarding a message to the ISU', 'length in bytes of the mobile terminated SBD message received from the GSS, mt_length', 
	 'MT queued is a count of mobile terminated SBD messages waiting at the GSS to be transferred to the ISU (modem), mt_length', 'cmd_queue', 'Failed transaction (%)']

	if not Data.iridium_status:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:
		fig0 = Binary_plot(Data.iridium_status['is_iridium_link_ok'], Title[0], default_value=True)
		fig1 = normal_plot(Data.iridium_status['signal_strength'], Title[1])
		fig2 = normal_plot(Data.iridium_status['registration_status'], Title[2], y_axis = {"detached":0,"not registered":1,"registered":2,"registration denied":3})
		fig3 = normal_plot(Data.iridium_status['mo_status_code'], Title[3])
		fig4 = normal_plot(Data.iridium_status['last_mo_msg_sequence_number'], Title[4])
		fig5 = normal_plot(Data.iridium_status['mt_status_code'], Title[5])
		fig6 = normal_plot(Data.iridium_status['mt_msg_sequence_number'], Title[6])
		fig7 = normal_plot(Data.iridium_status['mt_length'], Title[7])
		fig8 = normal_plot(Data.iridium_status['gss_queued_msgs'], Title[8])
		fig9 = normal_plot(Data.iridium_status['cmd_queue'], Title[9])
		fig10 = normal_plot(Data.iridium_status['failed_transaction_percent'], Title[10])

		L = [fig0,fig1,fig2,fig3,fig4,fig5,fig6,fig7,fig8,fig9,fig10]
		Red_line = False

	# Fig = merge_plots(L,'Iridium Status',red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/iridium/Bilan_iridium_status3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Iridium Status', L, '/iridium/Bilan_iridium_status3000.html')



# = = = = = = = = = = = =  /autopilot_node/ixblue_autopilot/autopilot_outputs  = = = = = = = = = = = = = = 

def plot_autopilot(Data):

	Title = ['Speed', 'Active Speed', 'Delta', 'Regime', 'Yaw Rate', 'Comparison btw autopilot and drix speed']

	if not Data.autopilot:
		L = No_Data_Found_plots(Title)
		Red_line = True

	else:
		fig0 = normal_plot(Data.autopilot['Speed'], Title[0])
		fig1 = normal_plot(Data.autopilot['ActiveSpeed'], Title[1])
		fig2 = normal_plot(Data.autopilot['Delta'], Title[2])
		fig3 = normal_plot(Data.autopilot['Regime'], Title[3])
		fig4 = normal_plot(Data.autopilot['yawRate'], Title[4])
		fig5 = several_plot(Data.autopilot['speed_autopilot'], Title[5], list_y = ['y_gps','y_autopilot'], label_y = ['Gps speed','Autopilot speed'])
		
		L = [fig0,fig1,fig2,fig3,fig4,fig5]
		Red_line = False

	# Fig = merge_plots(L,'Autopilot Data',red_line = Red_line)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/autopilot/Bilan_autopilot3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Autopilot Data', L, '/autopilot/Bilan_autopilot3000.html')



# = = = = = = = = = = = = = = = = = = = = rc_command  = = = = = = = = = = = = = = = = = = = = = = = = = =

def plot_rc_command(Data):

	Title = ['Reception Mode']

	if not Data.rc_command:
		L = No_Data_Found_plots(Title)
		Fig = L[0]

	else:
		Fig = normal_plot(Data.rc_command['reception_mode'],Title[0], y_axis = {"UNKNOWN":0,"HF":1,"WIFI":2,"WIFI_VIRTUAL":3})

	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/rc_command/Bilan_rc_command3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'RC Command', [Fig], '/rc_command/Bilan_rc_command3000.html')


# = = = = = = = = = = = = = = = = = = = = diagnostics  = = = = = = = = = = = = = = = = = = = = = = = = = =

def plot_diagnostics(Data):

	L = []
	Diags = Data.diagnostics

	for k in list(Diags.keys()):

		L.append(normal_plot(Data.diagnostics[k], k))

	# Fig = merge_plots(L,'Diagnostics Data',Height = 200)
	# plotly.offline.plot(Fig, filename = Data.ihm_path + '/diagnostics/Bilan_diagnostics3000.html', auto_open=False)

	IHM.html_page_creation(Data, 'Diagnostics Data', L, '/diagnostics/Bilan_diagnostics3000.html')


# = = = = = = = = = = = = = = = = = = = = Tools  = = = = = = = = = = = = = = = = = = = = = = = = = =

def Binary_plot(df, Title, default_value = True, Width=1600, Height=300): # creates binary plot 

	error_value = 1 - default_value

	if error_value in df['y'].tolist():
		color = 'red'
	else:
		color = 'green'

	fig = px.line(df, x='Time', y='y', title = Title,width=Width, height=Height)

	fig.update_layout(yaxis=dict(tickvals = [1,0], ticktext = ['True','False']))
	fig.update_traces(line_color=color)
	# fig.show()

	return(fig)

# - - - - - - - - - - - -

def normal_plot(df, Title, y_axis = None, Width=1600, Height=400, scatter_bool = False):

	if 'y_max' in df.columns.tolist():

		fig = go.Figure()
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_min'],fill=None, mode='lines',line_color="rgb(100, 100, 100)",name = 'Extreme values'))
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_max'],fill='tonexty',fillcolor="rgb(175, 175, 175)",showlegend=False,line_color="rgb(100, 100, 100)"))
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_mean'],mode='lines', line_color='green',name = 'Mean values'))
		fig.update_layout(width=Width, height=Height, title = Title)

	else:

		if not scatter_bool:
			fig = px.line(df, x='Time', y='y', title = Title, width=Width, height=Height)

		else:
			fig = px.scatter(df, x='Time', y='y', title = Title, width=Width, height=Height)


	if y_axis:
		fig.update_layout(yaxis=dict(tickvals = list(y_axis.values()), ticktext = list(y_axis.keys())))
		
	# fig.show()
	return(fig)



def normal_plot2(df, Title, y_axis = None, Width=1600, Height=400, scatter_bool = False):

	if 'y_max' in df.columns.tolist():

		fig = go.Figure()
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_min'],fill=None, mode='lines',line_color="#116e69",name = 'Extreme values'))
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_max'],fill='tonexty',fillcolor="#116e69",showlegend=False,line_color="#116e69"))
		fig.add_trace(go.Scatter(x=df['Time'], y=df['y_mean'],mode='lines', line_color='#083734',name = 'Mean values')) # 1,3,2 [rgb(21,137,131), #083734, #0d524f]
		fig.update_layout(width=Width, height=Height, title = Title)

	else:

		if not scatter_bool:
			fig = px.line(df, x='Time', y='y', title = Title, width=Width, height=Height)

		else:
			fig = px.scatter(df, x='Time', y='y', title = Title, width=Width, height=Height)

		fig.update_traces(line_color='rgb(21,137,131)')

	fig.update_layout(
				    	font_family="Courier New",
				   		font_color="rgb(183,181,182)",
				   		title_font_size=28,
					    title_font_family="Times New Roman",
					    title_font_color="rgb(93,128,220)",
					    legend_title_font_color="rgb(183,181,182)"
					)

	fig.update_layout(title={'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'})

	if y_axis:
		fig.update_layout(yaxis=dict(tickvals = list(y_axis.values()), ticktext = list(y_axis.keys())))

	fig.update_layout(plot_bgcolor='#3c3c3c', paper_bgcolor='#2a2a2a')
	

	fig.update_layout(legend=dict(bgcolor= "#3c3c3c"))

	fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#4a4a4a', zerolinecolor= '#4a4a4a')
	fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#4a4a4a', zerolinecolor= '#4a4a4a')
		
	# fig.show()
	return(fig)


# - - - - - - - - - - - -

def several_plot(df, Title, list_y, label_y, y_axis = None, Width=1600, Height=400, scatter_bool = False):


	if not scatter_bool:
		fig = px.line(df, x='Time', y=list_y, title = Title,width=Width, height=Height)

	else:
		fig = px.scatter(df, x='Time', y=list_y, title = Title, width=Width, height=Height)

	for idx, name in enumerate(label_y):
	    fig.data[idx].name = name
	    fig.data[idx].hovertemplate = name

	if y_axis:
		fig.update_layout(yaxis=dict(tickvals = list(y_axis.values()), ticktext = list(y_axis.keys())))
		
	# fig.show()
	return(fig)


# - - - - - - - - - - - -

def merge_plots(L, Title, Height = 250, Width=1800, red_line = False):


	list_title = [fig['layout']['title']['text'] for fig in L]

	Fig = make_subplots(rows=len(L), cols=1,shared_xaxes=False, subplot_titles = list_title, row_width=[0.8]*len(L))


	for k in range(len(L)):

		for f in L[k]["data"]:
			Fig.add_trace(f,row=1 + k, col=1)

	# - - - - - 

	names = set()
	Fig.for_each_trace(
    lambda trace:
        trace.update(showlegend=False)
        if (trace.name in names) else names.add(trace.name))

	# - - - - - 

	Fig.update_layout(height=len(L)*Height, width=Width, title_text=Title)

	if red_line == True:

		for i in Fig['layout']['annotations']:
			i['font'] = dict(size=10,color='red')

	# Fig.show()

	return(Fig)


# - - - - - - - - - - - -

def No_Data_Found_plots(Title):

	L = []

	draft_template = go.layout.Template()
	draft_template.layout.annotations = [
	    dict(
	        name="draft watermark",
	        text="DRAFT",
	        
	        opacity=0.1,
	        font=dict(color="black", size=80),
	        xref="paper",
	        yref="paper",
	        x=0.5,
	        y=0.5,
	        showarrow=False,
	    )
	]

	for t in Title:

		fig = px.line(x = [1,10], y = [5,5], title = t)
		fig.update_layout(title_font_color="red")
		fig.update_layout(template=draft_template, annotations=[
        dict(            templateitemname="draft watermark",
            text="No Data Found",
        )
    ]
)
		fig.for_each_trace(lambda trace: trace.update(visible="legendonly"))

		L.append(fig)

	# fig.show()

	return(L)

