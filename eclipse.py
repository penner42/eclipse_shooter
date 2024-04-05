import gphoto2 as gp
import csv 
from datetime import *
import configparser as cp
import time
from dateutil.relativedelta import relativedelta   
import math
from pydub import AudioSegment
from pydub.playback import play

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac
    
class config(cp.ConfigParser):
    def __init__(self):
        pass


class Camera():
    def __init__(self):
        self.context = gp.Context()
        self.camera = gp.Camera()

        initialized = False
        while not initialized:
            try:
                self.camera.init(self.context)
                initialized = True
            except gp.GPhoto2Error as e:
                if e.code == -6 or e.code == -105:
                    input("Failed to initialize. Connect camera and press enter.")
                else:
                    print(e)                
       
        try:
            self.exposure = self.camera.get_single_config("shutterspeed")
            self.bracket_mode = self.camera.get_single_config("aeb")
            self.releasemode = self.camera.get_single_config("eosremoterelease")
            self.set_config("capturetarget", "Memory card")
            self.set_config("eosremoterelease", "Release Full")
            self.set_config("aeb", "off")
            self.set_config("iso", "100")
            self.set_config("aperture", "8")
        except gp.GPhoto2Error as e:
            print(e)

    def set_config(self, c, v):
        conf = self.camera.get_single_config(c)
        conf.set_value(v)
        self.camera.set_single_config(c, conf)
                

    def get_config(self, c):
        try:
            return self.camera.get_single_config(c).get_value()
        except gp.GPhoto2Error as e:
            return ""

    def shoot(self, shutterspeed, bracket):
        captured = False
        while not captured:
            try:
                self.set_config("shutterspeed", shutterspeed)
                if bracket is not None:
                    self.set_config("aeb", bracket)
                    self.set_config("eosremoterelease", "Immediate")
                    time.sleep(max(0.4, convert_to_float(shutterspeed)*3))
                else:
                    self.set_config("aeb", "off")
                    self.camera.trigger_capture()
                
                captured = True

            except gp.GPhoto2Error as e:
                self.set_config("eosremoterelease", "Release Full")

        released = False
        while not released:
            try:
                self.set_config("eosremoterelease", "Release Full")
                released = True
            except gp.GPhoto2Error as e:
                raise(e)


class EclipseData():
    def __init__(self):
        self.read_csv()

    def time_to_datetime(self, t):
        return datetime.strptime(t.strip(), "%Y-%m-%d %H:%M:%S")

    def read_csv(self):
        with open('solareclipses-local.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                if "Date" in row[0]:
                    continue
                self.eclipse_date = row[0].strip()
                try:
                    self.partial_start = self.time_to_datetime(self.eclipse_date+" "+row[2])
                except ValueError as e:
                    self.partial_start = None

                try: 
                    self.totality_start = self.time_to_datetime(self.eclipse_date+" "+row[3])
                except ValueError as e:
                    self.totality_start = None

                try: 
                    self.totality_end = self.time_to_datetime(self.eclipse_date+" "+row[6])
                except ValueError as e:
                    self.totality_end = None

                try: 
                    self.partial_end = self.time_to_datetime(self.eclipse_date+" "+row[7])
                except ValueError as e:
                    self.partial_end = None

        f.close()
        
def seconds_to(t):
    return (t - datetime.now()).total_seconds()

if __name__ == '__main__':
    e = EclipseData()

    partial_1       = e.partial_start  - relativedelta(seconds=60)
    remove_filter   = e.totality_start - relativedelta(seconds=30)
    bailys_beads_1  = e.totality_start - relativedelta(seconds=15)
    totality        = e.totality_start + relativedelta(seconds=15)
    bailys_beads_2  = e.totality_end   - relativedelta(seconds=15)
    partial_2       = e.totality_end   + relativedelta(seconds=15)
    replace_filter  = e.totality_end   + relativedelta(seconds=20)
    end             = e.partial_end    + relativedelta(seconds=60)

    print("Now              : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Partial start    : %s (%s)" % (partial_1, e.partial_start))
    print("Remove filter    : %s"      % remove_filter)
    print("Baily's beads 1 : %s"      % bailys_beads_1)
    print("Totality start   : %s (%s)" % (totality, e.totality_start))
    print("Baily's beads 2 : %s"      % bailys_beads_2)
    print("Replace filter   : %s"      % replace_filter)
    print("Partial ends     : %s (%s)" % (end, e.partial_end))

    partial_exposures = [
        ["1/400", "+/- 1/3"],
        ["1/200", "+/- 1/3"],
        ["1/100", "+/- 1/3"]
    ]
    bailys_exposures = [
        ["1/6400", "+/- 1/3"],
        ["1/3200", "+/- 1/3"],
        ["1/1600", "+/- 1/3"],
        ["1/50",   "+/- 1/3"],
        ["1/100",  "+/- 1/3"]
    ]
    totality_exposures = [
        ["1/6400", "+/- 1/3"],
        ["1/3200", "+/- 1/3"],
        ["1/1600", "+/- 1/3"],
        ["1/1000", "+/- 1/3"],
        ["1/500",  "+/- 1/3"],
        ["1/250",  "+/- 1/3"],
        ["1/125",  "+/- 1/3"],
        ["1/60",   "+/- 1/3"],
        ["1/30",   "+/- 1/3"],
        ["1/15",   "+/- 1/3"],
        ["1/8",    "+/- 1/3"],
        ["1/4",    "+/- 1/3"],
        ["0.5",    "+/- 1/3"],
        ["0.8", None],
        ["1",   None],
        ["1.3", None],
        ["1.6", None],
        ["2",   None],
        ["2.5", None],
        ["3.2", None],
        ["6.3", None],
        ["8",   None]
    ]

    c = Camera()
    remove_filter_audio = AudioSegment.from_mp3("remove_filter.mp3")
    replace_filter_audio = AudioSegment.from_mp3("replace_filter.mp3")
    
    dialmode = ""
    while dialmode != "Manual":
        dialmode = c.get_config("autoexposuremodedial")
        if dialmode != "Manual":
            input("Make sure the camera is on and the exposure dial is set to M, then press enter.")

    focusmode = ""
    while focusmode != "Manual":
        focusmode = c.get_config("focusmode")
        if focusmode != "Manual":
            input("Make sure the camera is on and set to manual focus, then press enter.")

    moviemode = "1"
    while moviemode != "0":
        moviemode = c.get_config("eosmovieswitch")
        if moviemode != "0":
            input("Make sure the camera is on and not in movie mode, then press enter.")

    # PARTIAL_1
    while seconds_to(partial_1) > 0:
        try:
            print("\rWaiting to shoot Partial 1 in %s" % math.floor(seconds_to(partial_1)), end=" seconds...      ", flush=True)
            # keep camera on
            c.get_config("autoexposuremodedial")
            time.sleep(min(1, seconds_to(partial_1)))

        except ValueError as e:
            pass
    print("")

    while seconds_to(remove_filter) > 0:
        next_bracket = datetime.now() + relativedelta(seconds=20)
        for i in range(len(partial_exposures)):
            shutter = partial_exposures[i][0]
            bracket = partial_exposures[i][1]
            print("\rPartial 1: Next bracket in %s seconds. Remove filter in %s" % (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(remove_filter))), end=" seconds.      ", flush=True)
            if seconds_to(remove_filter) > 20:
                c.shoot(shutter, bracket)
            else:
                break
        if seconds_to(remove_filter) > 20:
            while seconds_to(next_bracket) > 0:
                print("\rPartial 1: Next bracket in %s seconds. Remove filter in %s" % (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(remove_filter))), end=" seconds.      ", flush=True)
                try:
                    time.sleep(min(1, seconds_to(next_bracket)))
                except ValueError as e:
                    pass
        else:
            print("\rPartial 1: Finished.", end="                                                                    ", flush=True)
            break
    print("")

    # REMOVE FILTER
    while seconds_to(remove_filter) > 0:
        print("\rWaiting to remove filter in %s" % math.floor(seconds_to(remove_filter)), end=" seconds.                ", flush=True)
        try:
            time.sleep(min(1, seconds_to(remove_filter)))
        except ValueError as e:
            pass
    if seconds_to(replace_filter) > 0:
        print("\r\nREMOVE FILTER!!!!\n")
        play(remove_filter_audio)

    # BAILYS_BEADS_1
    while seconds_to(bailys_beads_1) > 0:
        print("\rWaiting to shoot Baily's Beads 1 in %s" % math.floor(seconds_to(bailys_beads_1)), end=" seconds...           ", flush=True)
        try:
            time.sleep(min(1, seconds_to(bailys_beads_1)))
        except ValueError as e:
            pass
    print("")

    exposure = 0
    while seconds_to(totality) > 0:
        print("\rShooting Bailys Beads 1 for %s" % math.floor(seconds_to(totality)), end=" seconds.           ", flush=True)
        shutter = bailys_exposures[exposure][0]
        bracket = bailys_exposures[exposure][1]
        exposure = (exposure + 1) % len(bailys_exposures)
        c.shoot(shutter, bracket)        
    print("")

    exposure = 0
    while seconds_to(bailys_beads_2) > 0:
        print("\rShooting Totality for %s" % math.floor(seconds_to(bailys_beads_2)), end=" seconds.           ", flush=True)
        shutter = totality_exposures[exposure][0]
        bracket = totality_exposures[exposure][1]
        if seconds_to(bailys_beads_2) < convert_to_float(shutter):
            break
        exposure = (exposure + 1) % len(totality_exposures)
        c.shoot(shutter, bracket)        
    print("")

    # BAILYS_BEADS_2
    exposure = 0
    while seconds_to(partial_2) > 0:
        print("\rShooting Bailys Beads 2 for %s" % math.floor(seconds_to(partial_2)), end=" seconds. REPLACE FILTER AFTER!", flush=True)
        shutter = bailys_exposures[exposure][0]
        bracket = bailys_exposures[exposure][1]
        exposure = (exposure + 1) % len(bailys_exposures)
        c.shoot(shutter, bracket)        
    print("\nREPLACE FILTER!!!!!\n")
    play(replace_filter_audio)    

    # PARTIAL_2
    while seconds_to(end) > 0:
        next_bracket = datetime.now() + relativedelta(seconds=20)
        for i in range(len(partial_exposures)):
            print("\rPartial 2: Next bracket in %s seconds. Done in %s" % (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(end))), end=" seconds.      ", flush=True)
            if seconds_to(end) > 20:
                shutter = partial_exposures[i][0]
                bracket = partial_exposures[i][1]
                c.shoot(shutter, bracket)
            else:
                break
        if seconds_to(end) > 20:
            while seconds_to(next_bracket) > 0:
                print("\rPartial 2: Next bracket in %s seconds. Done in %s" % (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(end))), end=" seconds.      ", flush=True)
                try:
                    time.sleep(min(1, seconds_to(next_bracket)))
                except ValueError as e:
                    pass
        else:
            print("\rPartial 2: Finished.", end="                                                                    ")
            break
    print("\nDONE!")