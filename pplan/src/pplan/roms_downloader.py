import threading, time
import numpy as np
import ppas

class ROMSDownloader(threading.Thread):
    def __init__(self, out, save_store,
                 lat0, lat1,
                 lon0, lon1,
                 depth0, depth1,
                 dates):
        threading.Thread.__init__(self)
        self.daemon = True
        self.out = out
        self.save_store = save_store
        self.lat0, self.lat1, self.lon0, self.lon1 = lat0, lat1, lon0, lon1
        self.depth0, self.depth1 = depth0, depth1
        self.dates = dates

    def run(self):
        self.out.set_fraction(0.0)
        for date_i in range(len(self.dates)):
            date = self.dates[date_i]
            try:
                # connect to ROMS
                dset = ppas.roms.open_dataset(date)
                
                # get the data
                data = ppas.roms.get_data(
                    dset, self.lat0, self.lat1, self.lon0, self.lon1, self.depth0, self.depth1)
                self.save_store[str(date)] = data
                self.out.writeln('Got ROMS data for %s' % str(date))                
            except Exception, e:
                self.out.writeln('No ROMS data available for %s' % str(date))
                self.out.writeln(str(e))

            self.out.set_fraction(float(date_i+1)/len(self.dates))
            time.sleep(0.1)

    
