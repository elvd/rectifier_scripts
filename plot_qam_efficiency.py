# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 16:45:18 2018

Loads manually recorded data from an Excel spreadsheet and produces graphs in
similar style to all other data processing scripts.

Each sheet in the excel file contains data for a single circuit at a single
frequency point. The data are arranged as a 2D table, with column headers
corresponding to the DC resistances, and rows are arranged in an ascending
RF power order.

The script produces one graph per sheet in the Excel file.

@author: eenvdo
"""

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.rc('text', usetex=True)
mpl.rc('font', family='serif')
import matplotlib.pyplot as plt


measurements_file = pd.ExcelFile('DC_Voltage_All_Boards.xlsx')
circuits_list = measurements_file.sheet_names

start_prf = -10  # in dBm
stop_prf = 16
step_prf = 2
npts_prf = int((stop_prf - start_prf) / step_prf + 1)

prf_dbm = np.linspace(start_prf, stop_prf, npts_prf)
prf_w = np.power(10, prf_dbm/10) / 1000

for circuit in circuits_list:
    measurement = measurements_file.parse(circuit)
    dc_load_list = measurement.columns

    measurement /= 1e3  # Data recorded in mV, convert to V
    pdc_w = measurement ** 2 / dc_load_list
    efficiency = pdc_w.div(prf_w, axis='rows') * 100

    fig, ax = plt.subplots()

    cs = ax.contourf(dc_load_list, prf_dbm, efficiency,
                     levels=range(0, 70, 10), cmap=plt.cm.PuBu)
    cs2 = ax.contour(cs, levels=range(0, 70, 10), colors='grey',
                     linewidths=0.5)

    ax.set_xlim(1, 1e6)
    ax.set_ylim(-10, 16)
    ax.set_yticks(prf_dbm)
    ax.set_xscale('log')

    cbar = plt.colorbar(cs)
    cbar.ax.set_ylabel('Efficiency, \%')

    plt.title(circuit)
    plt.xlabel(r'DC Load Resistance, $\Omega$')
    plt.ylabel('Input RF Power, dBm')

    fig.tight_layout()
    fig.savefig('.'.join([circuit, 'pdf']))
    fig.clear()
    plt.close(fig)
