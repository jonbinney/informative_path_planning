#!/usr/bin/env python
import roslib
roslib.load_manifest('pplan')
import sys, time, os, os.path
import numpy as np
import matplotlib
matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvasGTK
from matplotlib.backends.backend_gtk import NavigationToolbar2GTK as NavigationToolbar
import gtk, gtk.glade, gobject

import pplan, ppas

class PPlanGUI:
    def __init__(self):
        gladefile = os.path.join(roslib.packages.get_pkg_dir('pplan'), "glade/pplan_gui.glade")
        self.windowname = "main_window"
        self.w_tree = gtk.glade.XML(gladefile, self.windowname)
        dic = {'on_main_window_destroy' : gtk.main_quit,
               'on_get_data_button_clicked' : self.get_data,
               'on_make_graph_button_clicked' : self.make_graph,
               'on_calc_kernel_button_clicked' : self.calc_kernel,
               'on_plan_path_button_clicked' : self.plan_path,
               }
        self.w_tree.signal_autoconnect(dic)

        main_window = self.w_tree.get_widget('main_window')
                                        
        # setup matplotlib stuff on first notebook page (empty graph)
        self.figure = Figure(figsize=(6,4), dpi=72)
        self.axis = self.figure.add_subplot(111)
        self.axis.set_xlabel('Longitude')
        self.axis.set_ylabel('Latitude')
        self.axis.set_title('')
        self.axis.grid(True)
        self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
        self.canvas.show()
        self.graphview = self.w_tree.get_widget('vbox1')
        self.graphview.pack_start(self.canvas, True, True)
        self.nav_bar = NavigationToolbar(self.canvas, main_window)
        self.graphview.pack_start(self.nav_bar, False, True)

        run_dir = sys.argv[1]
        self.settings = pplan.PPlanSettings(run_dir)
        # initialize the data directory, if not done already
        self.store = ppas.Store(self.settings.data_dir)

        self.plot_graph()
        self.plot_path()

    def get_data(self, event):
        ''' Start a new thread to fetch data. '''
        progress_bar = self.w_tree.get_widget('get_data_progress_bar')
        out = pplan.GTKOutputter(progress_bar)
        s = self.settings
        rp = s.roi_properties
        tp = s.training_properties
        save_dir = os.path.join(s.data_dir, 'training_data')
        downloader = pplan.ROMSDownloader(
            out, ppas.Store(save_dir), rp['lat0']-0.03, rp['lat1']+0.03, rp['lon0']-0.03, rp['lon1']+0.03,
            rp['depth']-10., rp['depth']+10., tp['dates'])
        downloader.start()

    def make_graph(self, event):
        progress_bar = self.w_tree.get_widget('make_graph_progress_bar')
        out = pplan.GTKOutputter(progress_bar)
        graph_maker = pplan.GraphMaker(
            out, ppas.Store(self.settings.data_dir), self.settings.roi_properties, self.settings.graph_properties)
        graph_maker.start()

    def calc_kernel(self, event):
        progress_bar = self.w_tree.get_widget('calc_kernel_progress_bar')
        out = pplan.GTKOutputter(progress_bar)
        save_dir = self.settings.data_dir
        training_data_dir = os.path.join(self.settings.data_dir, 'training_data')
        points_dir = self.settings.data_dir
        cov_trainer = pplan.CovarianceTrainer(
            out, ppas.Store(save_dir), ppas.Store(training_data_dir), ppas.Store(points_dir),
            self.settings.roi_properties['qoi'], self.settings.roi_properties['starttime'])
        cov_trainer.start()

    def plan_path(self, event):
        progress_bar = self.w_tree.get_widget('plan_path_progress_bar')
        out = pplan.GTKOutputter(progress_bar)
        save_dir = self.settings.data_dir
        graph_dir = self.settings.data_dir
        path_planner = pplan.PathPlanner(
            out, ppas.Store(save_dir), ppas.Store(graph_dir), self.settings.planner_properties)
        path_planner.start()

    def plot_graph(self):
        try:
            G = self.store['G']
            graph_plotter = ppas.plot.GraphPlotter(G, 'latlon')
            graph_plotter.plot(ax=self.axis, nodenames=False)
        except Exception:
            pass

    def plot_path(self):
        try:
            G = self.store['G']
            P = self.store['P']
            graph_plotter = ppas.plot.GraphPlotter(G, 'latlon')
            graph_plotter.plot_path(P, ax=self.axis, nodenames=False)
        except Exception:
            pass
        

    def main(self):
        gtk.main()

if __name__ == '__main__':
    gobject.threads_init()
    gui = PPlanGUI()
    gui.main()
