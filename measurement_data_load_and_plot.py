# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:20:36 2018

This is the first and main data processing and visualisation script for
RF-DC rectifier measurement data.

The scripts reads in csv files obtained either from the LabVIEW measurement
VI or the rectifier_measurements_modulated_signal.py file. The data consists
of one csv file per circuit per DC load resistance. Within that file, each line
corresponds to a particular frequency, with measurements on the same line
corresponding to increasing input RF power.

Once all the files for a particular circuit and/or modulation are loaded, the
rectification efficiency is calculated and plotted as a 2D contour plot.

The results are saved as a multipage pdf file, with each page being a contour
plot corresponding to aa single frequency point. X axis is DC load resistance,
Y axis is input RF power, and the colour of the contours is the efficiency.

@author: eenvdo
"""

import os
import numpy as np
import matplotlib as mpl
mpl.rc('text', usetex=True)
mpl.rc('font', family='serif')
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf


# Input parameters, leave modulation as '' if CW signal is used
diode = 'HSMS-286B'
circuit = 'Shunt'
power = 'Low'
modulation = '4X5MHz'

dirname = '_'.join([diode, circuit, power])
filenames = os.listdir(dirname)

start_freq = 5.2  # in GHz
stop_freq = 5.8
step_freq = 0.6
npts_freq = int(np.round(stop_freq - start_freq, 1) / step_freq + 1)
freq_ghz = np.linspace(start_freq, stop_freq, npts_freq)

start_prf = -10  # in dBm
stop_prf = 16
step_prf = 2
npts_prf = int((stop_prf - start_prf) / step_prf + 1)
prf_dbm = np.linspace(start_prf, stop_prf, npts_prf)
prf_w = np.power(10, prf_dbm/10) / 1000

# This array contains all measurement data for one circuit - efficiency as a
# function of DC resistance, RF frequency, and input RF power
dc_load_list = np.array([1, 10, 100, 200, 300, 390, 512, 600, 910, 2.2e3,
                         5.2e3, 11e3, 51e3, 110e3, 1.2e6])

measured_data = np.zeros((np.size(filenames), np.size(freq_ghz),
                          np.size(prf_dbm)))

for idx, filename in enumerate(filenames):
    data = np.loadtxt(os.sep.join([dirname, filename]), delimiter='\t')
    # Extract value of DC resistance from measurement data filename
    dc_load = int(filename.split(os.extsep)[0].split('_')[-1])
    # Find correct place to copy the data
    dc_load_index = np.where(dc_load_list == dc_load)[0][0]
    measured_data[dc_load_index, :, :] = data

pdc_w = np.zeros(np.shape(measured_data))
efficiency = np.zeros(np.shape(measured_data))

for idx, load in enumerate(dc_load_list):
    pdc_w[idx, :, :] = measured_data[idx, :, :] ** 2 / load
    efficiency[idx, :, :] = (pdc_w[idx] / prf_w) * 100

plots_file = matplotlib.backends.backend_pdf.PdfPages(os.extsep.join([dirname,
                                                                     'pdf']))

nx, ny = np.meshgrid(dc_load_list, prf_dbm, indexing='ij')

for idx, frequency in enumerate(freq_ghz):
    fig, ax = plt.subplots()
    cs = ax.contourf(nx, ny, efficiency[:, idx, :], levels=range(0, 70, 10),
                     cmap=plt.cm.PuBu)
    cs2 = ax.contour(cs, levels=range(0, 70, 10), colors='grey',
                     linewidths=0.5)

    ax.set_xlim(1, 1e6)
    ax.set_ylim(-10, 16)
    ax.set_yticks(prf_dbm)
    ax.set_xscale('log')

    cbar = plt.colorbar(cs)
    cbar.ax.set_ylabel('Efficiency, \%')

    plt.title(' '.join(['Modulation = ', modulation, ' Frequency =',
                        str(frequency), 'GHz']))
    plt.xlabel(r'DC Load Resistance, $\Omega$')
    plt.ylabel('Input RF Power, dBm')

    fig.tight_layout()
    plots_file.savefig(fig)
    fig.clear()
    plt.close(fig)

plots_file.close()
