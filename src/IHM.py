from airium import Airium
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt, mpld3
import plotly



#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
#							This script handles all IHM creation                            #
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#


def filter_binary_msg(data, condition): # report the times (start and end) when the condition is fulfilled

    list_event = []
    l = data.query(condition).index.tolist()

    if not(l):
        # print('Nothing found for ',condition)
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


def display_binary_msg(Liste, msg):

	L = [msg,'<br>']
	
	for val in Liste:
		L.append('Btw :')
		L.append(str(val[0]))
		L.append("and")
		L.append(str(val[1]))
		L.append('<br>')

	return(' '.join(L))



def display_date(date):
	l = date.split('-')
	
	days =int(l[0])
	month = int(l[1])
	year = int(l[2])
	hours = int(l[3])
	minutes = int(l[4])
	seconds = int(l[5])

	return(datetime(year, month, days, hours, minutes, seconds).ctime())
	
    	
def generate_ihm(report_data):

	a = Airium()

	a('<!DOCTYPE html>')
	with a.html(lang="pl"):
		with a.head():
			a.meta(charset="utf-8")
			a.title(_t="Mission Report")

		with a.body():
			with a.h1(id="id23409231", klass='main_header'):
				a("Mission Report")

			with a.p():
				a("Drix mission between "+ display_date(report_data.date_d)+" and "+ display_date(report_data.date_f))

			with a.h2(id="id23409231", klass='main_header'):
				a("Gps data : "+"<a href = ../IHM/gps/Bilan_gps.html>Processed</a>"+'<br>')

			with a.p():
				a("Total Distance performed : "+str(report_data.msg_gps["global_dist"])+" km"+'<br>')
				a("Average speed : "+str(report_data.msg_gps['global_speed'])+" in m/s, "+str(report_data.msg_gps["global_knots"])+" in knot")

			with a.h2(id="id23409231", klass='main_header'):
				a("Drix status data: "+"<a href = ../IHM/drix_status/Bilan_drix_status.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Telemetry data : "+"<a href = ../IHM/telemetry/Bilan_telemetry.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Gpu state data : "+"<a href = ../IHM/gpu_state/Bilan_gpu_state.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Phins data : "+"<a href = ../IHM/phins/Bilan_phins.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Trimmer data : "+"<a href = ../IHM/trimmer_status/Bilan_trimmer_status.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Iridium data : "+"<a href = ../IHM/iridium/Bilan_iridium_status.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Autopilot data : "+"<a href = ../IHM/autopilot/Bilan_autopilot.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("RC_command data : "+"<a href = ../IHM/rc_command/Bilan_rc_command.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Diagnostics data : "+"<a href = ../IHM/diagnostics/Bilan_diagnostics.html>Processed</a>"+'<br>')

	html = str(a) # casting to string extracts the value

	with open('../IHM/Mission_report.html', 'w') as f:
		 f.write(str(html))





def generate_ihm3000(Data):

	a = Airium()

	a('<!DOCTYPE html>')
	with a.html(lang="pl"):
		with a.head():
			a.meta(charset="utf-8")
			a.title(_t="Mission Report")

		with a.body():
			with a.h1(id="id23409231", klass='main_header'):
				a("Mission Report")

			with a.p():
				a("Drix mission between "+ display_date(Data.date_d)+" and "+ display_date(Data.date_f))

			with a.h2(id="id23409231", klass='main_header'):
				a("Gps data : "+"<a href = gps/Bilan_gps3000.html>Processed</a>"+'<br>')

			with a.p():
				a("Total Distance performed : "+str(Data.msg_gps["global_dist"])+" km"+'<br>')
				a("Average speed : "+str(Data.msg_gps['global_speed'])+" in m/s, "+str(Data.msg_gps["global_knots"])+" in knot")

			with a.h2(id="id23409231", klass='main_header'):
				a("Drix status data: "+"<a href = drix_status/Bilan_drix_status3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Telemetry data : "+"<a href = telemetry/Bilan_telemetry3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Gpu state data : "+"<a href = gpu_state/Bilan_gpu_state3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Phins data : "+"<a href = phins/Bilan_phins3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Trimmer data : "+"<a href = trimmer_status/Bilan_trimmer_status3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Iridium data : "+"<a href = iridium/Bilan_iridium_status3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Autopilot data : "+"<a href = autopilot/Bilan_autopilot3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("RC_command data : "+"<a href = rc_command/Bilan_rc_command3000.html>Processed</a>"+'<br>')

			with a.h2(id="id23409231", klass='main_header'):
				a("Diagnostics data : "+"<a href = diagnostics/Bilan_diagnostics3000.html>Processed</a>"+'<br>')

	html = str(a) # casting to string extracts the value

	with open(Data.ihm_path + '/Mission_report3000.html', 'w') as f:
		 f.write(str(html))




def html_page_creation(Data, page_name, L, path):

	a = Airium()

	a('<!DOCTYPE html>')

	with a.html(lang="pl"):

		with a.h1(id="id23409231", klass='main_header'):
				a(page_name)
			
		
		for k in L:
			a(plotly.offline.plot(k, include_plotlyjs='cdn', output_type='div'))

	html = str(a) # casting to string extracts the value



	with open(Data.ihm_path + path, 'w') as f:

		 f.write(str(html))


# - - - - - - - - - - - - - - 

def html_gps(Data, page_name, L, path):

	a = Airium()

	a('<!DOCTYPE html>')

	with a.html(lang="pl"):

		with a.h1(id="id23409231", klass='main_header'):
			a(page_name)

		with a.p():
			a("Total Distance performed : "+str(Data.msg_gps["global_dist"])+" km"+'<br>')
			a("Average speed : "+str(Data.msg_gps['global_speed'])+" in m/s, "+str(Data.msg_gps["global_knots"])+" in knot"+'<br>')

		with a.p():
			a("Survey distance : "+str(Data.msg_gps["path_following_dist"])+' kms'+'<br>')
			a("Survey Average speed : "+str(Data.msg_gps["path_following_speed"])+' m/s, '+'<br>')
			a("Survey duration : "+str(Data.msg_gps["path_following_dt"])+'  '+'<br>')


		a(plotly.offline.plot(L[0], include_plotlyjs='cdn', output_type='div'))
		a(plotly.offline.plot(L[1], include_plotlyjs='cdn', output_type='div'))


	html = str(a) # casting to string extracts the value

	with open(Data.ihm_path + path, 'w') as f:

		 f.write(str(html))


# - - - - - - - - - - - - - -  


def html_phins(Data, page_name, L, path):

	a = Airium()

	a('<!DOCTYPE html>')

	with a.html(lang="pl"):

		with a.h1(id="id23409231", klass='main_header'):
			a(page_name)

		a(plotly.offline.plot(L[0], include_plotlyjs='cdn', output_type='div'))

		with a.h1(id="id23409231", klass='main_header'):
			a("Pitch Curve")

		with a.p():

			a("Max negative : "+str(Data.msg_phins["pitch_min"])+" (deg)"+'<br>')
			a("Max positive : "+str(Data.msg_phins["pitch_max"])+" (deg)"+'<br>')
			a("Mean value : "+str(Data.msg_phins["pitch_mean"])+" (deg)"+'<br>')

		a(plotly.offline.plot(L[1], include_plotlyjs='cdn', output_type='div'))

		with a.h1(id="id23409231", klass='main_header'):
			a("Roll Curve")

		with a.p():

			a("Max negative : "+str(Data.msg_phins["roll_min"])+" (deg)"+'<br>')
			a("Max positive : "+str(Data.msg_phins["roll_max"])+" (deg)"+'<br>')
			a("Mean value : "+str(Data.msg_phins["roll_mean"])+" (deg)"+'<br>')

		a(plotly.offline.plot(L[2], include_plotlyjs='cdn', output_type='div'))



	html = str(a) # casting to string extracts the value



	with open(Data.ihm_path + path, 'w') as f:

		 f.write(str(html))




def html_phins2(Data, page_name, L, path):

	a = Airium()

	a('<!DOCTYPE html>')

	with a.html(lang="pl"):

		a("<link rel=\"stylesheet\"  href=\"test.css\"/>")

		with a.body():

			with a.h1(id="id23409231", klass='main_header'):
				a(page_name)

			a(plotly.offline.plot(L[0], include_plotlyjs='cdn', output_type='div'))

			with a.h1(id="id23409231", klass='main_header'):
				a("Pitch Curve")

			with a.p():

				a("Max negative : "+str(Data.msg_phins["pitch_min"])+" (deg)"+'<br>')
				a("Max positive : "+str(Data.msg_phins["pitch_max"])+" (deg)"+'<br>')
				a("Mean value : "+str(Data.msg_phins["pitch_mean"])+" (deg)"+'<br>')

			a(plotly.offline.plot(L[1], include_plotlyjs='cdn', output_type='div'))

			with a.h1(id="id23409231", klass='main_header'):
				a("Roll Curve")

			with a.p():

				a("Max negative : "+str(Data.msg_phins["roll_min"])+" (deg)"+'<br>')
				a("Max positive : "+str(Data.msg_phins["roll_max"])+" (deg)"+'<br>')
				a("Mean value : "+str(Data.msg_phins["roll_mean"])+" (deg)"+'<br>')

			a(plotly.offline.plot(L[2], include_plotlyjs='cdn', output_type='div'))



	html = str(a) # casting to string extracts the value



	with open(Data.ihm_path + path, 'w') as f:

		 f.write(str(html))