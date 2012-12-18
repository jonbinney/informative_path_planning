import threading, datetime
import numpy as np
import ppas

class CovarianceTrainer(threading.Thread):
    def __init__(self, out, save_store, training_data_store, points_store, varname, exp_start):
        threading.Thread.__init__(self)
        self.daemon = True
        self.out = out
        self.save_store = save_store
        self.training_data_store = training_data_store
        self.points_store = points_store
        self.varname = varname
        self.exp_midnight = datetime.datetime(exp_start.year, exp_start.month, exp_start.day, 0, 0)
        print exp_start.hour
        if exp_start.hour < 13:
            self.exp_midnight += datetime.timedelta(days=1)


    def run(self):
        self.out.set_fraction(0.01)
        points = self.points_store['points']
        training_dates = self.training_data_store.keys()
        training_array = np.zeros((len(points), len(training_dates)))

        # build array of training data
        for date_i in range(len(training_dates)):
            date_str = training_dates[date_i]
            print date_str
            data = self.training_data_store[date_str]
            data_year, data_month, data_day = [int(s) for s in date_str.split('-')]
            data_midnight = datetime.datetime(data_year, data_month, data_day, 0, 0)
            time_offset = ppas.datetime_to_seconds(self.exp_midnight) - ppas.datetime_to_seconds(data_midnight)
            for p_i in range(len(points)):
                p = points[p_i]
                t = p[3] - time_offset
                val = ppas.roms.get_value(data, p[0], p[1], p[2], t, self.varname, interp='linear')
                training_array[p_i,date_i] = val
        self.out.set_fraction(0.5)

        # filter out bad data
        if self.varname == 'salt':
            varmin, varmax = 30., 40.
        elif self.varname == 'temp':
            varmin, varmax = 10., 100.
        else:
            dieee_unknown_var_type___
        good_columns = ((training_array > varmin) & ( training_array < varmax)).all(axis=0)
        self.out.set_fraction(0.7)

        # calculate covariance matrix
        kmat = np.cov(training_array[:,good_columns])
        self.save_store['kmat'] = kmat
        self.out.set_fraction(1.0)



    
