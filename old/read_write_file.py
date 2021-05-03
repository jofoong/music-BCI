#!/usr/bin/env python
# coding: utf-8


#TODO: rename function.

import numpy as np
import pandas as pd
import mne

from brainflow.board_shim import BoardShim
from brainflow.data_filter import DataFilter
from mne.channels import read_layout

#Reference: Read write file from Brainflow documentation examples - https://brainflow.readthedocs.io/en/stable/Examples.html#python-read-write-file
def print_current_data(data, board_id):
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    df = pd.DataFrame(np.transpose(data))
    print('Data From the Board')
    print(df.head(5))

    # data serialization using brainflow API
    # demo how to convert it to pandas DF and plot data

    #restored_data = DataFilter.read_file('test.csv')
    #restored_df = pd.DataFrame(np.transpose(restored_data))
    #print('Data From the File')
    #print(restored_df.head(5))

def plot_data(data, board_id):
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    eeg_data = data[eeg_channels, :]
    eeg_data = eeg_data / 1000000  # BrainFlow returns uV, convert to V for MNE
    # Creating MNE objects from brainflow data arrays
    ch_types = ['eeg'] * len(eeg_channels)
    ch_names = BoardShim.get_eeg_names(board_id)
    sfreq = BoardShim.get_sampling_rate(board_id)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    raw.plot_psd(average=False)

    df = pd.DataFrame(np.transpose(data))
    print('Data From the Board')
    print(df.head(5))



    eeg_channels = BoardShim.get_eeg_channels(synth_board_id)





