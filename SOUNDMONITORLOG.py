from m5stack import *
from m5ui import *
from uiflow import *
import wifiCfg
import urequests
import machine
import unit
import ntptime

setScreenColor(0x222222)
mic_2 = unit.get(unit.MICROPHONE_AD, unit.PORTB)

label0 = M5TextBox(55, 69, "label0", lcd.FONT_Default, 0xFFFFFF, rotate=0)

# Initialize ADC for reading analog signals
adc0 = machine.ADC(machine.Pin(36))

circle0 = M5Circle(85, 115, 15, 0xFFFFFF, 0xFFFFFF)

# Function to get current NTP time
def getCurrentTime():
    ntptime.settime()
    current_time = utime.localtime()  # Get current time
    return current_time

# Function to generate Oracle timestamp
def oracletimestamp():
  global month, day, hour, minute, strmonth, second, strday, strhour, strminute, strsecond
  month = ntp.month()
  day = ntp.day()
  hour = ntp.hour()
  minute = ntp.minute()
  second = ntp.second()
  if month < 10:
    strmonth = (str('0') + str(str(month)))
  else:
    strmonth = str(month)
  if day < 10:
    strday = (str('0') + str(str(day)))
  else:
    strday = str(day)
  if hour < 10:
    strhour = (str('0') + str(str(hour)))
  else:
    strhour = str(hour)
  if minute < 10:
    strminute = (str('0') + str(str(minute)))
  else:
    strminute = str(minute)
  if second < 10:
    strsecond = (str('0') + str(str(second)))
  else:
    strsecond = str(second)
  return (str((ntp.year())) + str(((str('-') + str(((str(strmonth) + str(((str('-') + str(((str(strday) + str(((str('T') + str(((str(strhour) + str(((str(':') + str(((str(strminute) + str(((str(':') + str(((str(strsecond) + str('Z'))))))))))))))))))))))))))))))))

ntp = ntptime.client(host='cn.pool.ntp.org', timezone=8)


# Function to send data to Oracle table via HTTP POST request
def sendDataToOracle(mic_value, message):
    timestamp = oracletimestamp()
    data = {'DATETIMESTAMP': timestamp, 'MICVALUE': mic_value, 'MESSAGE': message}
    try:
        req = urequests.post(url='https://fciszjhbmsy6qgt-db1n8ia.adb.us-ashburn-1.oraclecloudapps.com/ords/iot/soundmonitorlog/', json=data)
        if req.status_code == 200:
            print("Data sent successfully to Oracle table.")
        else:
            print("Failed to send data to Oracle table. Status code:", req.status_code)
    except Exception as e:
        print("Error:", e)

while True:
    mic_value = adc0.read()  # Read analog signal from microphone
    if mic_value >= 4095:  # Check if the sound level is above a certain threshold
        rgb.setColorAll(0x00FF00)  # Set circle color to white
        sendDataToOracle(mic_value, "Patient Is Stable")
        wait_ms(10)

    else:
        rgb.setColorAll(0x0000FF)
        wait_ms(200)
        rgb.setColorAll(0xFF0000)
        wait_ms(200)
        sendDataToOracle(mic_value, "Emergency Help Needed!")

    label0.setText(str(mic_value))
