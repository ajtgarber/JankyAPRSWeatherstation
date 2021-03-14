import bme680
import time
from datetime import datetime
import os

try:
	sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
	sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
#sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

#sensor.set_gas_heater_temperature(320)
#sensor.set_gas_heater_duration(150)
#sensor.select_gas_heater_profile(0)

f = open("sensorlog.txt", "a")

last_temp = -400
last_press = -400
last_humidity = -400

last_press_diff1 = -400
last_press_diff2 = -400
last_press_diff3 = -400

last_smoothed_pressure = 0
smoothed_pressure = 0

max_pressure = -400
min_pressure = 2000

interval = 900

try:
	while True:
		if sensor.get_sensor_data():
			temperature = str(round(sensor.data.temperature, 2))
			pressure = str(round(sensor.data.pressure+31, 2))
			humidity = str(round(sensor.data.humidity, 2))
			
			if float(pressure) > max_pressure:
				max_pressure = float(pressure)
			elif float(pressure) < min_pressure:
				min_pressure = float(pressure)

			if last_temp == -400:
				last_temp = temperature
			if last_press == -400:
				last_press = pressure
			if last_humidity == -400:
				last_humidity = humidity

			pressure_roc = (3600*(float(pressure)-float(last_press)))/interval
			pressure_roc = round(pressure_roc, 2)
			
			if last_press_diff1 == -400:
				last_press_diff1 = pressure_roc
				last_press_diff2 = pressure_roc
				last_press_diff3 = pressure_roc
				last_smoothed_pressure = pressure_roc
				smoothed_pressure = pressure_roc
			
			last_press_diff1 = last_press_diff2
			last_press_diff2 = last_press_diff3
			last_press_diff3 = pressure_roc
			
			last_smoothed_pressure = smoothed_pressure
			smoothed_pressure = round((last_press_diff1 + last_press_diff2 + last_press_diff3) / 3.0, 2)
			
			# needs to actually 'trigger' based on the smoothed pressures
			local_min_found = False
			if last_smoothed_pressure < -0.05 and smoothed_pressure > 0.05:
				local_min_found = True

			date = datetime.now().strftime("%m/%d/%Y,%H:%M:%S")

			f.write(date + "," + temperature + "," + pressure + "," + humidity + "," + "0," + str(local_min_found) + "\n")
			print(date + "," + temperature + "," + pressure + "," + humidity + "," + "0," + str(local_min_found))
			os.system('python send_kiss_frame.py KE8EZC-1 KE8EZC ":KE8EZC   :'+pressure+'mb, last: '+last_press+'mb, ROC: '+str(pressure_roc)+'mb/Hr, localmin: '+str(local_min_found)+'"')
			f.flush()

			last_temp = temperature
			last_press = pressure
			last_humidity = humidity
		time.sleep(interval)
except KeyboardInterrupt:
	pass

f.close()

