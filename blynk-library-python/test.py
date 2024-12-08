import BlynkLib
import time

BLYNK_TEMPLATE_ID = "TMPL6Uv2ihAzR"
BLYNK_TEMPLATE_NAME = "SmartParking"
BLYNK_AUTH = 'kd0EAcKzsj2OzniEuBoUHl4_PvXolbF7'

# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

tmr_start_time = time.time()
while True:
    blynk.run()

    t = time.time()
    if t - tmr_start_time > 1:
        print("1 sec elapsed, sending data to the server...")
        blynk.virtual_write(0, "Occupied")
        blynk.virtual_write(4, 0)
        tmr_start_time += 1
