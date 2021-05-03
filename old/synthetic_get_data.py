#!/usr/bin/env python
# coding: utf-8

# Get data from a synthetic board for testing and write to a file

import time
import sys
import mne
import numpy as np
import pandas as pd
import read_write_file as io
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter

synth_board_id = BoardIds.SYNTHETIC_BOARD.value

def main():
    params = BrainFlowInputParams()
    board = BoardShim(synth_board_id, params)
    board.prepare_session()
    #board.start_stream(450000, "file://file_stream.csv:w")
    board.start_stream()

    print("Stream started (synthetic data).")
    #print("Sample rate: ", BoardShim.get_sampling_rate(synth_board_id)) #250
    start_time = time.time()

    while True:
        try:
            time.sleep(1) #in seconds
            data = board.get_current_board_data(128) #get latest 128 data points, don't remove from internal buffer
            #data = board.get_board_data(); #get all data, remove from internal buffer
            DataFilter.write_file(data, 'file_stream.csv', 'w')
            io.print_current_data(data, synth_board_id)
        except KeyboardInterrupt:
            break

    board.stop_stream()
    print('Stopped streaming.')
    board.release_session()

    #io.plot_data(data)

if __name__ == "__main__":
    main()