# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 15:14:49 2018

This script loads the simulated rectifier efficiency as a function of input RF
power, DC load resistance, and RF frequency; and outputs a series of 2D contour
plots, one for each frequency. The simulated data is obtained from Keysight ADS
and consists of one csv file per circuit.

The script produces one multipage pdf file, containing all the simulation data
for a particular circuit. Each page corresponds to a different frequency point.

@author: eenvdo
"""

import os
import numpy as np
import matplotlib as mpl
mpl.rc('text', usetex=True)
mpl.rc('font', family='serif')
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt


filenames = os.listdir(os.getcwd())

# These are predefined and are the same between simulations and measurements
dc_load_list = np.array([1, 10, 100, 200, 300, 390, 512, 600, 910, 2.2e3,
                         5.2e3, 11e3, 51e3, 110e3, 1.2e6])  # in Ohm
freq_ghz = np.array([5.1, 5.2, 5.7, 5.8])  # in GHz
prf_dbm = np.linspace(-10, 16, 14)  # in dBm

# Create 2D contour plot coordinates
nx, ny = np.meshgrid(dc_load_list, prf_dbm, indexing='ij')

for filename in filenames:
    sim_data = np.loadtxt(filename, delimiter=',')
    sim_data = sim_data[:, 3]
    # original data is in 4 columns: freq, RDC, PRF, efficiency
    sim_data = np.reshape(sim_data, (4, 15, 14))

    pdf_filename = os.extsep.join([filename.split(os.extsep)[0], 'pdf'])
    plots_file = matplotlib.backends.backend_pdf.PdfPages(pdf_filename)

    for idx, frequency in enumerate(freq_ghz):
        fig, ax = plt.subplots()
        cs = ax.contourf(nx, ny, sim_data[idx, :, :],
                         levels=range(0, 70, 10),
                         cmap=plt.cm.PuBu)
        cs2 = ax.contour(cs, levels=range(0, 70, 10), colors='grey',
                         linewidths=0.5)

        ax.set_xscale('log')
        ax.set_xlim(1, 1e6)
        ax.set_ylim(-10, 16)
        ax.set_yticks(prf_dbm)

        cbar = plt.colorbar(cs)
        cbar.ax.set_ylabel('Efficiency, \%')

        plt.title(' '.join(['Frequency =', str(frequency), 'GHz']))
        plt.xlabel(r'DC Load Resistance, $\Omega$')
        plt.ylabel('Input RF Power, dBm')

        fig.tight_layout()
        plots_file.savefig(fig)
        fig.clear()
        plt.close(fig)

    plots_file.close()
