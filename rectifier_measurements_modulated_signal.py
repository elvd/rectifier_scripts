# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:42:42 2018

Perform rectifier measurements with a modulated signal.
Equipment used:
    - E4438C Vector Signal Generator
    - 34405A Multimetre

The multimetre is configured to measure DC voltage, while the VSG uses
pre-made digital modulation files, which are then loaded into the AWG's memory.

A single run of this script measures a single rectifier circuit with a single
DC load attached to it.

@author: eenvdo
"""

import time
import visa
import numpy as np


# %%  Functions
def init_siggen(instrument):
    #  Initialise the E4438C Vector Signal Generator and turns modulation on.
    instrument.write('*RST')
    instrument.write(':output:modulation:state on')
    instrument.write(':output:state off')
    instrument.query('*OPC?')


def init_mmetre(instrument):
    #  Initialise the multimetre and configure to measure DCV, with autoscale.
    instrument.write('*RST')
    instrument.write(':configure:voltage:dc auto')
    instrument.write(':trigger:source immediate')
    instrument.query('*OPC?')


def set_frequency(instrument, frequency):
    #  Sets the carrier frequency of the E4438C.
    frequency = str(frequency) + 'GHz'
    instrument.write(':source:frequency:cw {0}'.format(frequency))
    instrument.query('*OPC?')


def set_rf_power(instrument, power):
    #  Sets the output RF power of the E4438C. In the case of a modulated
    #  signal, the power is spread over the signal's bandwidth.
    power = str(power) + 'dBm'
    instrument.write(':source:power {0}'.format(power))
    instrument.query('*OPC?')


def conf_custom_dmod(instrument, dmod_file):
    #  Loads a configuration file describing a custom digital modulation into
    #  the E4438C. The file should already be on the E4438C.
    instrument.write(':source:radio:dmodulation:arb:setup "{0}"'.
                     format(dmod_file))
    instrument.write(':source:radio:dmodulation:arb:state on')
    time.sleep(conf_delay)
    instrument.query('*OPC?')


def conf_custom_mcarrier(instrument, mdmod_file):
    #  Loads a configuration file describing a custom multicarrier into
    #  the E4438C. The file should already be on the E4438C.
    instrument.write(':source:radio:dmodulation:arb:setup mcarrier')
    instrument.write(':source:radio:dmodulation:arb:setup:mcarrier "{0}"'.
                     format(mdmod_file))
    instrument.write(':source:radio:dmodulation:arb:state on')
    time.sleep(conf_delay)
    instrument.query('*OPC?')


def read_voltage(instrument):
    #  Reads a single measurement value from the multimetre.
    instrument.write(':initiate')
    reading = instrument.query(':fetch?')
    return reading


# %%  Run-time parameters and variable initialisation
diode = 'HSMS-286B'
circuit = 'Shunt'
power = 'Low'
#  These should be the same as the configuration files' filenames
modulations = ['16QAM-WPT', '2X10MHz', '4X5MHz']
dc_load = '1'

start_freq = 5.0  # in GHz
stop_freq = 6.0
step_freq = 0.1
npts_freq = int((stop_freq - start_freq) / step_freq + 1)
freq_ghz = np.linspace(start_freq, stop_freq, npts_freq)

start_prf = -9  # in dBm
stop_prf = 17
step_prf = 2
npts_prf = int((stop_prf - start_prf) / step_prf + 1)
prf_dbm = np.linspace(start_prf, stop_prf, npts_prf)

dc_voltage_data = np.empty((npts_freq, npts_prf))

meas_delay = 2.0  # time delay between RF source on and DC volt reading, sec
conf_delay = 10.0  # time delay from custom mod configure, sec

# %%  Connect to and initialise instruments
instruments = visa.ResourceManager()
instrument_list = instruments.list_resources()

#  This assumes 1 GPIB instrument and 1 USB instrument connected to control PC
siggen_addr = [addr for addr in instrument_list if 'GPIB' in addr]
siggen_addr = siggen_addr[0]

siggen = instruments.open_resource(siggen_addr)

init_siggen(siggen)
set_rf_power(siggen, prf_dbm[0])
set_frequency(siggen, freq_ghz[0])

mmetre_addr = [addr for addr in instrument_list if 'USB' in addr]
mmetre_addr = mmetre_addr[0]

mmetre = instruments.open_resource(mmetre_addr)

init_mmetre(mmetre)

# %% Main

for modulation in modulations:
    #  Filename for file containing measurement data
    meas_fname = '_'.join([diode, circuit, power, modulation, dc_load])
    meas_fname = '.'.join([meas_fname, 'csv'])

    if 'QAM' in modulation:
        conf_custom_dmod(siggen, modulation)
    else:
        conf_custom_mcarrier(siggen, modulation)

    siggen.write(':output:state on')
    siggen.query('*OPC?')

    for idx_freq, freq in enumerate(freq_ghz):
        set_frequency(siggen, freq)
        for idx_prf, prf in enumerate(prf_dbm):
            set_rf_power(siggen, prf)
            time.sleep(meas_delay)
            dc_voltage_data[idx_freq, idx_prf] = read_voltage(mmetre)

    siggen.write(':output:state off')
    siggen.query('*OPC?')

    np.savetxt(meas_fname, dc_voltage_data, delimiter='\t')
    dc_voltage_data = np.empty((npts_freq, npts_prf))

siggen.close()
mmetre.close()
