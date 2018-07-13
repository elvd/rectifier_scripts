# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:41:57 2018

The functionality of this script is almost identical to that of
"measurement_data_load_and_plot.py", except for producing multiple line graphs
on a single figure. These line graphs correspond to particular input RF powers.

Asides from that, the script still produces one figure per circuit and per
frequency, with DC load on the X axis and efficiency on the Y axis.

The script uses the same files as input data, but only extracts the lines
corresponding to the input RF powers specified by prf_plot_list for the
frequency specified by freq_plot.

@author: eenvdo
"""
import os
import numpy as np
from scipy.interpolate import interp1d
import matplotlib as mpl
mpl.rc('text', usetex=True)
mpl.rc('font', family='serif')
mpl.rc('font', variant='small-caps')
mpl.rc('figure', figsize=(8, 8/1.618))
mpl.rc('xtick', labelsize=10)
mpl.rc('ytick', labelsize=10)
mpl.rc('axes', labelsize=10)
mpl.rc('lines', antialiased=True)
import matplotlib.pyplot as plt
import brewer2mpl


diode = 'HSMS-286B'
circuit = 'Shunt'
power = 'High'

freq_plot = 5.2  # in GHz
prf_plot_list = [-4, 0, 4, 12]  # in dBm

dirname = '_'.join([diode, circuit, power])
filenames = os.listdir(dirname)

start_freq = 5.0  # in GHz
stop_freq = 6.0
step_freq = 0.1
npts_freq = int((stop_freq - start_freq) / step_freq + 1)
freq_ghz = np.linspace(start_freq, stop_freq, npts_freq)

start_prf = -10  # in dBm
stop_prf = 16
step_prf = 2
npts_prf = int((stop_prf - start_prf) / step_prf + 1)
prf_dbm = np.linspace(start_prf, stop_prf, npts_prf)
prf_w = np.power(10, prf_dbm/10) / 1000


# These are predefined and are the same between simulations and measurements
dc_load_list = np.array([1, 10, 100, 200, 300, 390, 512, 600, 1e3, 2.2e3,
                         5.2e3, 11e3, 51e3, 110e3, 1.2e6])

# This array contains all measurement data for one circuit - efficiency as a
# function of DC resistance, RF frequency, and input RF power
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

# Make the plot look nicer
plot_x = np.array([1, 10, 100, 200, 300, 390, 512, 600, 1e3, 2.2e3, 5.2e3,
                   11e3, 51e3, 110e3, 1e6])
plot_x_smooth = np.logspace(start=0, stop=6, num=4001, base=10.0)

fig, ax = plt.subplots()

graph_colours = brewer2mpl.get_map('PuOr', 'Diverging', 4).mpl_colors

for idx, prf_plot in enumerate(prf_plot_list):
    # Find the relevant data
    freq_plot_index = np.where(freq_ghz == freq_plot)[0][0]
    prf_plot_index = np.where(prf_dbm == prf_plot)[0][0]
    plot_y = efficiency[:, freq_plot_index, prf_plot_index]

    interp_func = interp1d(plot_x, plot_y, kind=1)
    plot_y_smooth = interp_func(plot_x_smooth)

    # plot discrete measurement points
    ax.semilogx(plot_x, plot_y, linestyle='None', marker='o',
                markerfacecolor=graph_colours[idx],
                markeredgecolor=graph_colours[idx],
                markersize=4)
    line_label = ' '.join([r'$P_{RF}=$', str(prf_plot), 'dBm'])

    # plot smooth interpolated line
    ax.semilogx(plot_x_smooth, plot_y_smooth, linestyle='-',
                color=graph_colours[idx],
                linewidth=1, label=line_label)

ax.legend()

ax.set_xlabel(r'DC load resistance, $\Omega$')
ax.set_ylabel(r'Efficiency, \%')
ax.set_title('Diode {} in {} at {} GHz'.
             format(diode, circuit, str(freq_plot)))

ax.set_xlim(1, 1e6)
fig.tight_layout()

fig_filename = '_'.join([diode, circuit, str(freq_plot)])
fig_filename = '.'.join([fig_filename, 'pdf'])

fig.savefig(fig_filename)
fig.clear()
plt.close(fig)
