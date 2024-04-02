import gphoto2 as gp
import csv 
from datetime import datetime
import configparser as cp
import time

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
        

if __name__ == '__main__':
    e = EclipseData()
    c = Camera()
    # while True:
    #     try:
    #         c.shoot("1/6400")
    #     except KeyboardInterrupt as e:
    #         exit()
    c.shoot("1/5000", None)
    c.shoot("1/8000", "+/- 1")
    c.shoot("1/6400", None)
    c.shoot("1/2500", None)
