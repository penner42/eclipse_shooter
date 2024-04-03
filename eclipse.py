import gphoto2 as gp
import csv 
from datetime import *
import configparser as cp
import time
from dateutil.relativedelta import relativedelta   
import math
from pydub import AudioSegment
from pydub.playback import play

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
            mode = self.camera.get_single_config("capturetarget")
            mode.set_value("Memory card")
            self.camera.set_single_config("capturetarget", mode)
            self.releasemode = self.camera.get_single_config("eosremoterelease")
            mode = self.camera.get_single_config("aeb")
            mode.set_value("off")
            self.camera.set_single_config("aeb", mode)

        except gp.GPhoto2Error as e:
            print(e)

    def dialmode(self):
        try:
            return self.camera.get_single_config("autoexposuremodedial").get_value()
        except gp.GPhoto2Error as e:
            return ""

    def shoot(self, shutterspeed, bracket):
        captured = False
        while not captured:
            try:
                self.exposure.set_value(shutterspeed)
                self.camera.set_single_config("shutterspeed", self.exposure)

                if bracket is not None:
                    self.bracket_mode.set_value(bracket)
                    self.camera.set_single_config("aeb", self.bracket_mode)
                    self.releasemode.set_value("Immediate")
                    self.camera.set_single_config("eosremoterelease", self.releasemode)
                    time.sleep(0.4)
                else:
                    self.bracket_mode.set_value("off")
                    self.camera.set_single_config("aeb", self.bracket_mode)
                    self.camera.trigger_capture()
                
                captured = True

            except gp.GPhoto2Error as e:
                self.releasemode.set_value("Release Full")
                self.camera.set_single_config("eosremoterelease", self.releasemode)

        released = False
        while not released:
            try:
                self.releasemode.set_value("Release Full")
                self.camera.set_single_config("eosremoterelease", self.releasemode)
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
    c = Camera()
    remove_filter_audio = AudioSegment.from_mp3("remove_filter.mp3")
    replace_filter_audio = AudioSegment.from_mp3("replace_filter.mp3")
    
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
    print("Bailey's beads 1 : %s"      % bailys_beads_1)
    print("Totality start   : %s (%s)" % (totality, e.totality_start))
    print("Bailey's beads 2 : %s"      % bailys_beads_2)
    print("Replace filter   : %s"      % replace_filter)
    print("Partial ends     : %s (%s)" % (end, e.partial_end))

    dialmode = ""
    while dialmode != "Manual":
        dialmode = c.dialmode()
        if dialmode != "Manual":
            input("Make sure the camera is on and the exposure dial is set to M, then press enter.")

    # PARTIAL_1
    while seconds_to(partial_1) > 0:
        try:
            print("\rWaiting to shoot Partial 1 in %s" % math.floor(seconds_to(partial_1)), end=" seconds...      ", flush=True)
            time.sleep(min(1, seconds_to(partial_1)))
        except ValueError as e:
            pass
    print("")

    while seconds_to(remove_filter) > 0:
        c.shoot("1/640", None)
        if seconds_to(remove_filter) > 20:
            next_bracket = datetime.now() + relativedelta(seconds=20)
            while seconds_to(next_bracket) > 0:
                print("\rPartial 1: Next bracket in %s seconds. Remove filter in %s" % 
                      (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(remove_filter))), end=" seconds.      ", flush=True)
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
    if seconds_to(remove_filter) < 0 and seconds_to(replace_filter) > 0:
        print("\r\nREMOVE FILTER!!!!\n")
        play(remove_filter_audio)

    # BAILEYS_BEADS_1
    while seconds_to(bailys_beads_1) > 0:
        print("\rWaiting to shoot Bailey's Beads in %s" % math.floor(seconds_to(bailys_beads_1)), end=" seconds...           ", flush=True)
        try:
            time.sleep(min(1, seconds_to(bailys_beads_1)))
        except ValueError as e:
            pass
    print("")

    while seconds_to(totality) > 0:
        print("\rShooting Baileys Beads 1 for %s" % math.floor(seconds_to(totality)), end=" seconds.           ", flush=True)
        c.shoot("1/4000", "+/- 1")
    print("")

    while seconds_to(bailys_beads_2) > 0:
        print("\rShooting Totality for %s" % math.floor(seconds_to(bailys_beads_2)), end=" seconds.           ", flush=True)
        c.shoot("1/640", "+/- 1")
        c.shoot("1/400", "+/- 1")
    print("")

    # BAILEYS_BEADS_2
    while seconds_to(partial_2) > 0:
        print("\rShooting Baileys Beads 2 for %s" % math.floor(seconds_to(partial_2)), end=" seconds. REPLACE FILTER AFTER!", flush=True)
        c.shoot("1/4000", "+/- 1")
    print("\nREPLACE FILTER!!!!!\n")
    play(replace_filter_audio)    

    # PARTIAL_2
    while seconds_to(end) > 0:
        c.shoot("1/640", None)
        if seconds_to(end) > 20:
            next_bracket = datetime.now() + relativedelta(seconds=20)
            while seconds_to(next_bracket) > 0:
                print("\rPartial 2: Next bracket in %s seconds. Done in %s" % 
                      (math.floor(seconds_to(next_bracket)),math.floor(seconds_to(end))), end=" seconds.      ", flush=True)
                try:
                    time.sleep(min(1, seconds_to(next_bracket)))
                except ValueError as e:
                    pass
        else:
            print("\rPartial 2: Finished.", end="                                                                    ")
            break
    print("\nDONE!")