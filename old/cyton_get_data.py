# Connects to the Cyton board, gets data, and writes to file.

# Required parameters for the BoardShim constructor for Cyton are:\n",
#  - board_id = 0
#  - serial_port
#  - mac_address (if empty, Brainflow will attempt to autodiscover)
#  - optional: timeout (for device discovery; default 15sec)

# TODO: write to file with Cyton board. See what data format with empty channels.

import time
import numpy as np
import brainflow
from brainflow.board_shim import (
    BoardShim,
    BrainFlowInputParams,
    LogLevels,
    BoardIds
)
from brainflow.data_filter import (
    DataFilter,
    FilterTypes,
    AggOperations
)

board_id = BoardIds.CYTON_BOARD.value

def main():
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()

    #params.serial_port = //see where dongle is connecting to in device manager",
    #params.timeout= 20

    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream(45000, 'file://cyton_session_data.csv:w')
    time.sleep(5)

    data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    # data = board.get_board_data() # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    print(data)

if __name__ == "__main__":
    main()