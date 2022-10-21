import obspython as obs
import time
import datetime

def script_description():
    return ""

def _start_obs():
    print("[%s]start streaming" % str(datetime.datetime.now()))
    obs.obs_frontend_streaming_start()

def _stop_obs():
    print("[%s]stop streaming" % str(datetime.datetime.now()))
    obs.obs_frontend_streaming_stop()


# run _restart_obs every 24h
obs.timer_add(_stop_obs, 1000*60*60*24)
obs.timer_add(_start_obs, (1000*60*60*24) + (1000*10))
#obs.timer_add(_restart_obs, 10000)
