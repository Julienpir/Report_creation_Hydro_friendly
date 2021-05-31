import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from pyproj import Proj

import main as Dr # Data_recovery 

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
#               This script handles all the data processing function
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

global G_variable
G_variable = 0


# = = = = = = = = = = = = = = = = = =  /gps  = = = = = = = = = = = = = = = = = = = = = = = =


def UnderSampleGps(Data, dist_min = 0.01, n = 10): #fct that processes gps data
    
    if Data.gps_raw is not None:

        N = len(Data.gps_raw['Time'])

        # - - - - - - Add distance data - - - - - -

        list_dist = [0]
        sum_dist = 0

        for k in range(1,N):
            a = np.array((Data.gps_raw['list_x'][k-1],Data.gps_raw['list_y'][k-1])) 
            b = np.array((Data.gps_raw['list_x'][k],Data.gps_raw['list_y'][k]))

            dist = np.linalg.norm(a - b)/1000 # in km
            sum_dist += abs(dist)

            list_dist.append(np.round(sum_dist*1000)/1000)


        Data.gps_raw = Data.gps_raw.assign(list_dist = list_dist) # distances in km

        

        # - - - - - Under distance sampling - - - - - -

        list_index = [0]
        a = np.array((Data.gps_raw['list_x'][0],Data.gps_raw['list_y'][0])) 
        for k in range(N):
            b = np.array((Data.gps_raw['list_x'][k],Data.gps_raw['list_y'][k]))
            dist = np.linalg.norm(a - b)/1000 # in km

            if dist > dist_min: # in order to reduce the data number
                list_index.append(k)
                a = np.array((Data.gps_raw['list_x'][k],Data.gps_raw['list_y'][k])) 

        Data.gps_UnderSamp_d = Data.gps_raw.iloc[list_index,:].reset_index()

        # - - - - - 

        l_diff = [Data.gps_UnderSamp_d['list_dist'][0]]
        for k in range(1,len(Data.gps_UnderSamp_d['list_dist'])):
            l_diff.append(np.round(Data.gps_UnderSamp_d['list_dist'][k] - Data.gps_UnderSamp_d['list_dist'][k - 1],3))

        Data.gps_UnderSamp_d = Data.gps_UnderSamp_d.assign(l_diff=l_diff)
        

def handle_actions(Data):

    # - = - = - = - gps - = - = - = -

    if Data.gps_raw is not None:

        # - - - - - - gps_actions - - - - - -

        L = []
        list_index_act = Data.gps_raw['action_type_index'].unique().tolist()

        for val in list_index_act:

            df = Data.gps_raw.loc[Data.gps_raw['action_type_index'] == val]

            L.append(df.iloc[0])
            L.append(df.iloc[-1])


        Data.gps_actions = pd.concat(L,sort=False)


        # - - - - - - Actions_data - - - - - -
        
        N = len(Data.gps_actions["Time"])
        list_t = []
        list_d = []
        list_speed = []
        list_knot = []
        list_dt = []
    
        for k in range(0,N,2):
            b = Data.gps_actions["list_dist"][k+1]
            a = Data.gps_actions["list_dist"][k]

            dist = b-a # in km
            dt = (Data.gps_actions["Time"][k+1] - Data.gps_actions['Time'][k]).total_seconds() # in s
            speed = (dist*1000)/dt # in m/s
            knots = speed*1.9438 # in knots/s

            list_t.append([Data.gps_actions["Time"][k],Data.gps_actions['Time'][k+1]]) # [[t0_start,t0_end], ... ,[ti_start,ti_end]]
            list_d.append(np.round(dist*100)/100) # in km
            list_speed.append(speed) # in m/s
            list_knot.append(knots) # in knots/s
            list_dt.append(dt) # in s

        Data.Actions_data = pd.DataFrame({"list_t":list_t,"list_d":list_d,"list_speed":list_speed,
            "list_knot":list_knot,"action_type":Data.gps_actions['action_type'][::2],"list_dt":list_dt})

  

def UnderSample(data_pd, n = 2): #fct that processes under sampling
    if data_pd is not None:
        return(data_pd.iloc[::n,:].reset_index())
    else:
        return(None)

# - - - - - - - - - - - - - -

def msg_reduced(list_msg): # fct which store only the when the value change in order to avoid rehearsals
                            # ex : l = (4, 4, 4, 4, 5) -> (4, None, None, None, 5)
    
    if len(list_msg) < 1:
        return(list_msg)

    l = [list_msg[0]]
    past = list_msg[0]

    for k in range(1,len(list_msg)):

        if list_msg[k] != past:
            past = list_msg[k]
            msg = list_msg[k]

        else: 
            msg = None

        l.append(msg)

    return(l)


# - - - - - - 

def extract_gps_data(Data):

    # - - - - - GNSS trajectory - - - - - -

    encode_action = {'IdleBoot' : 0,'Idle' : 1,'goto' : 2,'follow_me' : 3,'box-in': 4,"path_following" : 5,"dds" : 6,
    "gaps" : 7,"backseat" : 8,"control_calibration" : 9,"auv_following": 10,"hovering": 11,"auto_survey": 12}

    df1 = Data.gps_UnderSamp_d[['latitude','longitude', 'dist_drix_mothership']]
    df1.columns = ['l_lat', 'l_long', 'list_dist_mship']


    # - - - - 

    l_t = [int(Data.gps_UnderSamp_d['Time'][0].strftime('%s'))] + [int((Data.gps_UnderSamp_d['Time'][k] - Data.gps_UnderSamp_d['Time'][k-1]).total_seconds()) for k in range(1,len(Data.gps_UnderSamp_d['Time']))]
    l_action1 = [encode_action[k] for k in Data.gps_UnderSamp_d['action_type']]
    l_action2 = msg_reduced(l_action1)
    l_quality = msg_reduced(Data.gps_UnderSamp_d['fix_quality'])
    l_diff = msg_reduced(Data.gps_UnderSamp_d['l_diff'])

    df1 = df1.assign(t=l_t)
    df1 = df1.assign(fix_quality=l_quality)
    df1 = df1.assign(action_type=l_action2)
    df1 = df1.assign(l_diff=l_diff)


    # - - - - - Distance travelled graph - - - - - -

    if len(Data.gps_raw) < 1000:
        n_dist = 20
        df = Dp.UnderSample(Data.gps_raw, n_dist)

    else:
        n_dist = 200
        df = UnderSample(Data.gps_raw, n_dist)

    ini = df['Time'][0].strftime('%d:%H:%M:%S')
    dt = int((df['Time'][1]-df['Time'][0]).total_seconds())

    d0 = pd.DataFrame([ini,dt], columns =['t'])

    df2 = df['list_dist']
    df2 = pd.concat([d0, df2], axis=1)
    df2.columns = ['t', 'y']

    
    
    # - - - - - Speed Bar chart - - - - - -

    list_index = []
    list_speed = []
    list_dist = []
    action_type = []
    list_t = []

    for k in range(len(Data.Actions_data['list_dt'])):

        if (Data.Actions_data['action_type'][k] != 'Idle' and Data.Actions_data['action_type'][k] != 'IdleBoot'):
            
            list_speed.append(np.round(Data.Actions_data["list_speed"][k],3))
            action_type.append(encode_action[Data.Actions_data["action_type"][k]])
            list_index.append(k)
            list_t.append(int(Data.Actions_data["list_t"][k][0].strftime('%s')))
            list_dist.append(Data.Actions_data["list_d"][k])

    
    df3 = pd.DataFrame(list(zip(list_t, list_speed, list_dist, action_type)), columns =['t', 'y_speed','y_dist','action_type'])

    
    # - - - - Compression to csv format - - - -

    df1.to_csv(Data.result_path + '/gps/gps.csv', index=False)
    df2.to_csv(Data.result_path + '/gps/dist.csv', index=False)
    df3.to_csv(Data.result_path + '/gps/speed.csv', index=False)

    global G_variable

    L = df1.columns.tolist()
    for k in L:
        G_variable += len(df1[k])

    L = df2.columns.tolist()
    for k in L:
        G_variable += len(df2[k])

    L = df3.columns.tolist()
    for k in L:
        G_variable += len(df3[k])

    # - - - -

    Dr.report(' ')
    Dr.report('- - /gps - -')
    Dr.report('Data raw shape : ' + str(Data.gps_raw.shape))
    Dr.report(' ')
    Dr.report('gps, shape : ' + str(df1.shape))
    Dr.report('dist, shape : ' + str(df2.shape))
    Dr.report('speed, shape : ' + str(df3.shape))





# = = = = = = = = = = = = = = = = = = /mothership_gps  = = = = = = = = = = = = = = = = = = = = = = = = = =


def add_dist_mothership_drix(Data): # compute the distance btw the drix and the mothership
    
    list_t_drix = Data.gps_UnderSamp_d['Time']

    u = 0
    p = Proj(proj='utm',zone=10,ellps='WGS84')
    list_dist_drix_mship = []
    compt = 0 
    compt2 = 0 
    
    for k in range(len(Data.mothership_raw['Time'])):

        if u < len(list_t_drix):
            compt += 1

            if Data.mothership_raw['Time'][k] >= list_t_drix[u]:

                compt2 += 1

                x,y = p(Data.mothership_raw['latitude'][k], Data.mothership_raw['longitude'][k])
                a = np.array((x, y))
                b = np.array((Data.gps_UnderSamp_d['list_x'][u], Data.gps_UnderSamp_d['list_y'][u]))
                d = np.linalg.norm(a - b)/1000 # in km

                list_dist_drix_mship.append(int(abs(d)*1000)/1000)
                u += 1

    Data.gps_UnderSamp_d = Data.gps_UnderSamp_d.assign(dist_drix_mothership = list_dist_drix_mship)

# = = = = = = = = = = = = = = = =  /drix_status  = = = = = = = = = = = = = = = = = = = = = = = =


def extract_drix_status_data(Data):
    
    path = Data.result_path + "/drix_status"
    df = Data.drix_status_raw
    L = []

    L.append(noisy_msg(df, 'thruster_RPM', path, 100, N_round = 0))
    L.append(centered_sawtooth_curve(df,'rudderAngle_deg', path, 200, N_round = 0))
    L.append(noisy_msg(df,'gasolineLevel_percent', path, 15000, N_round = 0))
    L.append(data_reduced(df,'emergency_mode', path))
    L.append(data_reduced(df, 'remoteControlLost', path))
    L.append(data_reduced(df, 'shutdown_requested', path))
    L.append(data_reduced(df, 'reboot_requested', path))
    L.append(extract_drix_mode_data(df, path))
    L.append(extract_drix_clutch_data(df, path))
    L.append(extract_keel_state_data(df, path))

    # - - - 

    mode_debug('drix_status', L, df.shape)


# - - - - - - - - 

def extract_drix_mode_data(dff, path):

    encoder_dic = {"DOCKING":0,"MANUAL":1,"AUTO":2}
    label_names_unique = dff['drix_mode'].unique()

    cmt = 1
    for val in label_names_unique:
        if val not in list(encoder_dic.keys()):
            print("Unknown drix mode :",val)
            encoder_dic[val] = -cmt
            cmt +=1

    y_axis = {"vals":list(encoder_dic.values()),"keys":list(encoder_dic.keys())}
    list_msg = [encoder_dic[val] for val in dff['drix_mode']]

    df = data_reduced2(list_msg, dff['Time'], 'drix_mode', path)

    return('drix_mode', df.shape)


# - - - - - - - - 

def extract_drix_clutch_data(dff, path): # same operation as extract_drix_mode()

    encoder_dic = {"FORWARD":0,"NEUTRAL":1,"BACKWARD":2,"ERROR":4}
    label_names_unique = dff['drix_clutch'].unique()

    cmt = 1
    for val in label_names_unique:
        if val not in list(encoder_dic.keys()):
            print("Unknown drix clutch :",val)
            encoder_dic[val] = -cmt
            cmt +=1

    y_axis = {"vals":list(encoder_dic.values()),"keys":list(encoder_dic.keys())}
    list_msg = [encoder_dic[val] for val in dff['drix_clutch']]

    df = data_reduced2(list_msg, dff['Time'], 'drix_clutch', path)

    return('drix_clutch', df.shape)


# - - - - - - - - 


def extract_keel_state_data(dff, path): # same operation as extract_drix_mode()

    encoder_dic = {"DOWN":0,"MIDDLE":1,"UP":2,"ERROR":4,"GOING UP ERROR":5,"GOING DOWN ERROR":6,"UP AND DOWN ERROR":7}
    label_names_unique = dff['keel_state'].unique()

    cmt = 1
    for val in label_names_unique:
        if val not in list(encoder_dic.keys()):
            print("Unknown keel state :",val)
            encoder_dic[val] = -cmt
            cmt +=1

    y_axis = {"vals":list(encoder_dic.values()),"keys":list(encoder_dic.keys())}
    list_msg = [encoder_dic[val] for val in dff['keel_state']]

    df = data_reduced2(list_msg, dff['Time'], 'keel_state', path)

    return('keel_state', df.shape)



# = = = = = = = = = = = = = = = = = = = /d_phins/aipov  = = = = = = = = = = = = = = = = = = = = = = = =

def extract_phins_data(Data):

    path = Data.result_path + "/phins"
    df = Data.phins_raw
    n = 100

    L = []

    L.append(noisy_msg(df, 'headingDeg', path, n, N_round = 1))
    L.append(sawtooth_curve(df, 'rollDeg', path, n, N_round = 1))
    L.append(sawtooth_curve(df, 'pitchDeg', path, n, N_round = 1))

    # - - - 

    mode_debug('phins', L, df.shape)

    # df1 = noisy_msg(df, 'headingDeg', path, n, compression = False, N_round = 1)
    # df2 = sawtooth_curve(df, 'rollDeg', path, n, compression = False, N_round = 1)
    # df3 = sawtooth_curve(df, 'pitchDeg', path, n, compression = False, N_round = 1)

    # # d0 = pd.DataFrame(list(zip([n])), columns =['t'])
    # d1 = pd.DataFrame(list(zip(df1['t'],df1['y'])), columns =['t','y_heading'])
    # d2 = pd.DataFrame(list(zip(df2['y_min'], df2['y_max'])), columns =['y_min_roll', 'y_max_roll'])
    # d3 = pd.DataFrame(list(zip(df3['y_min'], df3['y_max'])), columns =['y_min_pitch', 'y_max_pitch'])

    # new = pd.concat([d1, d2, d3], axis=1)

    # new.to_csv('../Store_data/phins/phins.csv', index=False)

# = = = = = = = = = = = = = = = = = = /Telemetry2  = = = = = = = = = = = = = = = = = = = = = = = = = 

def extract_telemetry_data(Data):

    path = Data.result_path + "/telemetry"
    df = Data.telemetry_raw

    L = []

    L.append(data_reduced(df, 'is_drix_started', path))
    L.append(data_reduced(df, 'is_navigation_lights_on', path))
    L.append(data_reduced(df, 'is_foghorn_on', path))
    L.append(data_reduced(df, 'is_fans_on', path))
    L.append(data_reduced(df, 'is_water_temperature_alarm_on', path))
    L.append(data_reduced(df, 'is_oil_pressure_alarm_on', path))
    L.append(data_reduced(df, 'is_water_in_fuel_on', path))
    L.append(data_reduced(df, 'electronics_water_ingress', path))
    L.append(data_reduced(df, 'electronics_fire_on_board', path))
    L.append(data_reduced(df, 'engine_water_ingress', path))
    L.append(data_reduced(df, 'engine_fire_on_board', path))

    L.append(noisy_msg(df, 'oil_pressure_Bar', path, 100, N_round = 3))
    L.append(data_reduced(df, 'engine_water_temperature_deg', path))
    L.append(data_reduced(df, 'engineon_hours_h', path))
    L.append(data_reduced(df, 'main_battery_voltage_V', path))
    L.append(data_reduced(df, 'backup_battery_voltage_V', path))
    L.append(noisy_msg(df, 'engine_battery_voltage_V', path, 100, N_round = 1))
    L.append(data_reduced(df, 'percent_main_battery', path))
    L.append(data_reduced(df, 'percent_backup_battery', path))

    L.append(data_reduced(df, 'consumed_current_main_battery_Ah', path))
    L.append(data_reduced(df, 'consumed_current_backup_battery_Ah', path))
    L.append(data_reduced(df, 'current_main_battery_A', path))
    L.append(data_reduced(df, 'current_backup_battery_A', path))
    L.append(data_reduced(df, 'time_left_main_battery_mins', path))
    L.append(data_reduced(df, 'time_left_backup_battery_mins', path))
    L.append(noisy_msg(df, 'electronics_temperature_deg', path, 100, N_round = 1))
    L.append(noisy_msg(df, 'electronics_hygrometry_percent', path, 100, N_round = 1))
    L.append(data_reduced(df, 'engine_temperature_deg', path))
    L.append(data_reduced(df, 'engine_hygrometry_percent', path))

    # - - - 

    mode_debug('telemetry', L, df.shape)




# = = = = = = = = = = = = = = = = = = /gpu_state  = = = = = = = = = = = = = = = = = = = = = = = = = 

def extract_gpu_state_data(Data):

    path = Data.result_path + "/gpu_state"
    df = Data.gpu_state_raw
    L = []

    L.append(noisy_msg(df, 'temperature_deg_c', path, 60, N_round = 1))
    L.append(sawtooth_curve(df, 'gpu_utilization_percent', path, 10, N_round = 0))
    L.append(sawtooth_curve(df, 'mem_utilization_percent', path, 20, N_round = 0))
    L.append(data_reduced(df, 'total_mem_GB', path))
    L.append(noisy_msg(df, 'power_consumption_W', path, 10, N_round = 1))
    L.append(sawtooth_curve(df, 'power_consumption_W', path, 60, N_round = 1))

    # - - - 

    mode_debug('gpu_state', L, df.shape)
    


# = = = = = = = = = = = = = = = = = = /trimmer_status  = = = = = = = = = = = = = = = = = = = = = = = = = 

def extract_trimmer_status_data(Data):

    path = Data.result_path + "/trimmer_status"
    df = Data.trimmer_status_raw
    L = []

    L.append(sawtooth_curve(df, 'primary_powersupply_consumption_A', path, n = 100, N_round = 2)) 
    L.append(sawtooth_curve(df, 'secondary_powersupply_consumption_A', path, n = 100, N_round = 2))

    # df1 = sawtooth_curve(df, 'primary_powersupply_consumption_A', path, n = 100, compression = False, N_round = 2) 
    # df2 = sawtooth_curve(df, 'secondary_powersupply_consumption_A', path, n = 100, compression = False, N_round = 2) 

    # d1 = pd.DataFrame(list(zip(df1['t'])), columns =['t'])
    # d2 = pd.DataFrame(list(zip(df1['y_max'])), columns =['y_max_prim'])
    # d3 = pd.DataFrame(list(zip(df2['y_max'])), columns =['y_max_sec'])

    # new = pd.concat([d1, d2, d3], axis=1)
    # new.to_csv(path + '/power_consumption_A.csv', index=False)

    L.append(noisy_msg(df, 'motor_temperature_degC', path, 500, N_round = 1))
    L.append(noisy_msg(df, 'pcb_temperature_degC', path, 400, N_round = 1))
    L.append(data_reduced(df, 'relative_humidity_percent', path))

    # - - - 

    mode_debug('trimmer_status', L, df.shape)



# = = = = = = = = = = = = = = = = = = /d_iridium/iridium_status  = = = = = = = = = = = = = = = = = = = = = = = = = 

def extract_iridium_status_data(Data):

    path = Data.result_path + "/iridium"
    df = Data.iridium_status_raw
    L = []

    L.append(data_reduced(df, 'is_iridium_link_ok', path))
    L.append(data_reduced(df, 'signal_strength', path))
    L.append(extract_registration_status_data(df, path))
    L.append(data_reduced(df, 'mo_status_code', path))
    L.append(data_reduced(df, 'last_mo_msg_sequence_number', path))
    L.append(data_reduced(df, 'mt_status_code', path))
    L.append(data_reduced(df, 'mt_msg_sequence_number', path))
    L.append(data_reduced(df, 'mt_length', path))
    L.append(data_reduced(df, 'gss_queued_msgs', path))
    L.append(data_reduced(df, 'cmd_queue', path))
    L.append(data_reduced(df, 'failed_transaction_percent', path))

    # - - - 

    mode_debug('iridium', L, df.shape)


# - - - - - - - - - -


def extract_registration_status_data(dff, path): # same operation as extract_drix_mode()

    encoder_dic = {"detached":0,"not registered":1,"registered":2,"registration denied":3}
    label_names_unique = dff['registration_status'].unique()

    cmt = 1
    for val in label_names_unique:
        if val not in list(encoder_dic.keys()):
            print("Unknown keel state :",val)
            encoder_dic[val] = -cmt
            cmt +=1

    y_axis = {"vals":list(encoder_dic.values()),"keys":list(encoder_dic.keys())}

    list_msg = [encoder_dic[val] for val in dff['registration_status']]
    df = data_reduced2(list_msg, dff['Time'], 'registration_status', path)

    return('registration_status', df.shape)



# = = = = = = = = = = = =  /autopilot_node/ixblue_autopilot/autopilot_outputs  = = = = = = = = = = = = = = 


def extract_autopilot_data(Data):

    path = Data.result_path + "/autopilot"
    df = Data.autopilot_raw
    L = []

    L.append(noisy_msg(df,'Speed', path, 50, N_round = 2))
    L.append(data_reduced(df, 'ActiveSpeed', path))
    L.append(sawtooth_curve(df, 'Delta', path, 50, N_round = 3))
    L.append(sawtooth_curve(df, 'Regime', path, 50, N_round = 3))
    L.append(sawtooth_curve(df, 'yawRate', path, 50, N_round = 2))
    L.append(extract_diff_speed_data(Data, path))

    # - - - 

    mode_debug('autopilot', L, df.shape)
    

# - - - - - - - - - -


def extract_diff_speed_data(Data, path, N = 5):

    list_speed_gps = []
    list_speed_autopilot = []
    list_t = []
    u = 0

    for k in range(1 + N,len(Data.gps_UnderSamp_d['Time']),N):

        # - - Compute gsp speed - - - 

        list_t.append(Data.gps_UnderSamp_d['Time'][k])

        dist = Data.gps_UnderSamp_d['list_dist'][k] - Data.gps_UnderSamp_d['list_dist'][k-(1+N)] # in km
        dt = (Data.gps_UnderSamp_d["Time"][k] - Data.gps_UnderSamp_d['Time'][k-(1+N)]).total_seconds() # in s
        speed = (dist*1000)/dt # in m/s
        knots = speed*1.9438 # in knots/s

        list_speed_gps.append(speed)

    l = []

    while (list_t[u] < Data.autopilot_raw['Time'][0]): # for the case, where the autopilot starts after 
        u += 1 

        if u == len(list_t):
            break

    u_ini = u
    for k in range(len(Data.autopilot_raw['Time'])):

        if u < len(list_t):

            if Data.autopilot_raw['Time'][k] >= list_t[u]:

                # - - Compute autopilot mean speed - - 
                list_speed_autopilot.append(np.mean(l))
                u += 1
                l = []

            l.append(Data.autopilot_raw["Speed"][k])

    
    list_t = reduce_time_value(list_t[u_ini:u]) # we select only the values which can be compared to the autopilot data
    list_speed_gps = list_speed_gps[u_ini:u] 
    list_speed_autopilot = list_speed_autopilot 

    list_speed_gps = [np.round(k,1) for k in list_speed_gps]
    list_speed_autopilot = [np.round(k,1) for k in list_speed_autopilot]

    df = pd.DataFrame(list(zip(list_t, list_speed_gps, list_speed_autopilot)), columns =['t', 'y_gps', 'y_autopilot'])

    compress_data(path, 'speed_autopilot', df)

    return('speed_autopilot', df.shape)



# = = = = = = = = = = = = = = = = = = = = rc_command  = = = = = = = = = = = = = = = = = = = = = = = = = =

def extract_rc_command_data(Data):

    path = Data.result_path + "/rc_command"
    dff = Data.rc_command_raw

    encoder_dic = {"UNKNOWN":0,"HF":1,"WIFI":2,"WIFI_VIRTUAL":3}
    label_names_unique = dff['reception_mode'].unique()

    cmt = 1
    for val in label_names_unique:
        if val not in list(encoder_dic.keys()):
            print("Unknown reception_mode :",val)
            encoder_dic[val] = -cmt
            cmt +=1

    y_axis = {"vals":list(encoder_dic.values()),"keys":list(encoder_dic.keys())}
    list_msg = [encoder_dic[val] for val in dff['reception_mode']]
    L = []

    df = data_reduced2(list_msg, dff['Time'], 'reception_mode', path)
    compress_data(path, 'reception_mode', df)

    L.append(('reception_mode', df.shape))

    # - - - 

    mode_debug('rc_command', L, dff.shape)



# = = = = = = = = = = = = = = = = = = = = diagnostics  = = = = = = = = = = = = = = = = = = = = = = = = = =

def extract_diagnostics_data(Data):
    global G_variable

    L = []
    path = Data.result_path + "/diagnostics"
    dff = Data.diagnostics_raw

    Dr.report(' ')
    Dr.report('- - /diagnostics - -')
    Dr.report(' ')


    for k in dff.L_keys:
            n = len(np.unique(dff.L[k].level))
            if n>1:             

                list_t, Ly = data_reduction(dff.L[k].level, dff.L[k].time) 
                list_t, Ly = data_simplification(Ly, list_t)

                list_t = [k.strftime('%d:%H:%M:%S') for k in list_t]
                df = pd.DataFrame(list(zip(list_t, Ly)), columns =['t', 'y'])
                name = dff.L[k].name
                l = name.split(" ")
                Name = "".join(l)

                compress_data(path, Name, df)
                L.append(df)

                Dr.report(Name + ', shape : ' + str(df.shape))
    
    print("G_variable ",G_variable)

    Dr.report(' ')
    Dr.report('Global number of data : ' + str(G_variable))
    Dr.report(' ')




# = = = = = = = = = = = = = = = = = = = = Tools  = = = = = = = = = = = = = = = = = = = = = = = = = =

def return_G_variable():
    global G_variable

    print("Number of data after processing : ",G_variable)

    return()


def reduce_time_value(list_t): # conserves only the main data, ex: 2021-02-01 10:02:30 -> 01:10:02:30

    return([val.strftime('%d:%H:%M:%S') for val in list_t])


# - - - - - - - - - 

def compressed_time(list_msg, n):

    ini = list_msg[0].strftime('%d:%H:%M:%S')
    list_t = [list_msg[k + int(n/2)] for k in range(0,len(list_msg) - n,n)]
    res = [ini]

    if len(list_t)>1:

        dt = int((list_t[1]-list_t[0]).total_seconds())
        res.append(dt)

        for k in range(2,len(list_t)):
            delta = int((list_t[k]-list_t[k-1]).total_seconds())
            if delta != dt:
                res.append(delta)
                dt = delta
            else:
                res.append(None)

    else : 
        res = [ini]

    return(res)


# - - - - - - - - - 

def centered_sawtooth_curve(dff, msg, path, n = 10, compression = True, N_round = 3):

    # - - - Data Recovery - - -
    list_msg = dff[msg]
    Ly_max = [np.round(np.max(abs(list_msg[k:k + n])), N_round) for k in range(0,len(list_msg) - n,n)] 

    d0 = pd.DataFrame(compressed_time(dff['Time'].tolist(), n), columns =['t'])
    df = pd.DataFrame(list(zip(Ly_max)), columns =['y'])
    new = pd.concat([d0, df], axis=1)

    if compression:
        compress_data(path, msg, new)

    return(msg, new.shape)


# - - - - - - - - - 


def sawtooth_curve(dff, msg, path, n = 10, compression = True, N_round = 3): # extracts the mean curve, the max curve, the min curve 

    # - - - Data Recovery - - -
    list_msg = dff[msg]
    Ly_max = [np.round(np.max(list_msg[k:k + n]),N_round) for k in range(0,len(list_msg) - n,n)]
    Ly_min = [np.round(np.min(list_msg[k:k + n]),N_round) for k in range(0,len(list_msg) - n,n)]

    d0 = pd.DataFrame(compressed_time(dff['Time'].tolist(),n), columns =['t'])
    df = pd.DataFrame(list(zip(Ly_min, Ly_max)), columns =['y_min', 'y_max'])
    new = pd.concat([d0, df], axis=1)

    if compression:
        compress_data(path, msg, new)

    return(msg, new.shape)


# - - - - - - - - - 


def noisy_msg(dff, msg, path, n = 10, compression = True, N_round = 3): # data filtering with the mean each n values 

    # - - - Data Recovery - - -
    list_msg = dff[msg]
    Ly = [np.round(np.mean(list_msg[k:k + n]),N_round) for k in range(0,len(list_msg) - n,n)]
    
    d0 = pd.DataFrame(compressed_time(dff['Time'].tolist(), n), columns =['t'])
    df = pd.DataFrame(list(zip(Ly)), columns =['y'])
    new = pd.concat([d0, df], axis=1)

    if compression:
        compress_data(path, msg, new)

    return(msg, new.shape)


# - - - - - - - - - 

def data_reduction(list_msg, list_index): # Selects data only when there is a changing value

    Ly = [list_msg[0]]
    Lx = [list_index[0]]

    for k in range(1,len(list_msg)):

        if list_msg[k] != Ly[-1]:

            Ly.append(list_msg[k-1])
            Ly.append(list_msg[k])

            Lx.append(list_index[k-1])
            Lx.append(list_index[k])

    Ly.append(list_msg[len(list_msg)-1])
    Lx.append(list_index[len(list_index)-1])

    return(Lx, Ly)

# - - - - 

def data_reduced(dff, msg, path, compression = True):

    # ~ ~ ~ Data Recovery ~ ~ ~

    list_t, Ly = data_reduction(dff[msg], dff['Time']) 
    list_t = reduce_time_value(list_t)

    df = pd.DataFrame(list(zip(list_t, Ly)), columns =['t', 'y'])
    
    if compression:
        compress_data(path, msg, df)

    return(msg, df.shape)


# - - - - - - - - - - - - 


def data_reduced2(list_msg, list_T, msg, path, compression = True):

    # - - - Data Recovery - - -

    list_t, Ly = data_reduction(list_msg, list_T) 
    list_t = reduce_time_value(list_t)

    df = pd.DataFrame(zip(list_t, Ly), columns =['t', 'y'])
    
    if compression:
        compress_data(path, msg, df)

    return(df)

# - - - - - - - - - - - - 

def data_simplification(list_msg, list_t):

    list_y = [list_msg[0]]
    list_x = [list_t[0]]

    past_value = list_msg[0]
    past_t = list_t[0]


    for k in range(1, len(list_msg) - 1):

        if list_msg[k] != 0:

            list_y.append(list_msg[k])
            list_x.append(list_t[k])


        else:

            if list_t[k] > (list_t[k-1] + timedelta(seconds = 30)) or list_t[k] < (list_t[k+1] - timedelta(seconds = 30)):

                list_y.append(list_msg[k])
                list_x.append(list_t[k])

    list_y.append(list_msg[len(list_msg) - 1])
    list_x.append(list_t[len(list_msg) - 1])

    return(data_reduction(list_y, list_x))



# - - - - - - - - - - - - 

def compress_data(path, msg, df):
    global G_variable

    L = df.columns.tolist()

    for k in L:
        G_variable += len(df[k])

    name = path + '/' + msg + '.csv'
    df.to_csv(name, index=False)

    return()


# - - - - - - - - - - - - 

def mode_debug(topic, L, shape): 

    Dr.report(' ')
    Dr.report('- - /'+ topic + ' - -')
    Dr.report('Data raw shape : ' + str(shape))
    Dr.report(' ')

    for val in L:
        Dr.report(val[0] + ', shape : '+ str(val[1]))


# - - - - - - - - - - - - 

def filter_binary_msg(data, condition): # report the times (start and end) when the condition is fulfilled

    list_event = []
    l = data.query(condition).index.tolist()

    if not(l):
        print('Nothing found for ',condition)
        return None

    v_ini = l[0]
    debut = data['Time'][l[0]]

    for k in range(1,len(l)):
        if l[k] != (v_ini + 1):
            fin = data['Time'][l[k-1]]

            list_event.append([debut,fin])
            v_ini = l[k]
            debut = data['Time'][v_ini]

        else:
            v_ini += 1

    return(list_event)


  

