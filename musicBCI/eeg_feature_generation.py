# -*- coding: utf-8 -*-
"""eeg_feature_generation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/167KolRCGPZDxcZkNfl7vgoGDIjVYM7Nu

###We look at generating a few features from EEG datasets, and combining all of them to obtain the feature vector.

Adapted from Jordan J. Bird, Aston University, where original script is by Dr. Luis Manso [lmanso], Aston University
https://github.com/jordan-bird/eeg-feature-generation
"""

import numpy as np
import scipy
import scipy.signal
import pywt

WAVELET = "db6"

def matrix_from_csv_file(file_path):
    """
	Returns the data matrix given the path of a CSV file.
	
	Parameters:
		file_path (str): path for the CSV file with a time stamp in the first column
			and the signals in the subsequent ones.
			Time stamps are in seconds, with millisecond precision
    Returns:
		numpy.ndarray: 2D matrix containing the data read from the CSV
	
	Author: 
		Original: [lmanso] 
		Revision and documentation: [fcampelo]
	
	"""
    csv_data = np.genfromtxt(file_path, delimiter=',')
    full_matrix = csv_data[1:,:-1]
    print(full_matrix.shape)
    return full_matrix

"""
def matrix_from_bci_file(file_path):
	# Returns the data matrix given the path of a CSV BCI file.
    # Read in the file, omitting the first six lines.
    csv_data = np.genfromtxt(file_path, delimiter=',', skip_header=6, usecols=(1,2,3,4,22))

    # Reorder the timestamp to first position
    i = [4,0,1,2,3]
    full_matrix = csv_data[:,i]
    return full_matrix
"""

def get_time_slice(full_matrix, period, start=0.):
    """
	Returns a slice of the given matrix, where start is the offset and period is 
	used to specify the length of the signal.
	
	Parameters:
		full_matrix (numpy.ndarray): matrix returned by matrix_from_csv()
		start (float): start point (in seconds after the beginning of records) 
		period (float): duration of the slice to be extracted (in seconds)
	Returns:
		numpy.ndarray: 2D matrix with the desired slice of the matrix
		float: actual length of the resulting time slice
		
	Author:
		Original: [lmanso]
		Reimplemented: [fcampelo]
	"""
    rstart = full_matrix[0, 0] + start
    print(full_matrix[0, 0], rstart)

    index_0 = np.max(np.where(full_matrix[:, 0] <= rstart))
    index_1 = np.max(np.where(full_matrix[:, 0] <= rstart + period))
    duration = full_matrix[index_1, 0] - full_matrix[index_0, 0]
    return full_matrix[index_0:index_1, :], duration


"""
The EEG data at this point has not been pre-processed. 
Instead, I chose to extract selected features per epoch (1 second). 
The features are subclassed as Wavelet-based features (4) and time-domain features (3).

*   Mean
*   Standard deviation
*   Minimum, maximum
*   Covariance matrix
Wavelet transform:
*   Energy
*   Entropy

Time-domain (Hjorth parameters):
*   Ability 
*   Mobility
*   Complexity
"""


def feature_mean(matrix):
    """
	Returns the mean value of each signal for the full time window
	
	Parameters:
		matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the 
		values of nsignals for a time window of length nsamples
		
	Returns:
		numpy.ndarray: 1D array containing the means of each column from the input matrix
		list: list containing feature names for the quantities calculated.
	Author:
		Original: [lmanso]
		Revision and documentation: [fcampelo]
	"""
    ret = np.mean(matrix, axis=0).flatten()
    names = ['mean_' + str(i) for i in range(matrix.shape[1])]
    return ret, names


def feature_stddev(matrix):
    """
	Computes the standard deviation of each signal for the full time window
	
	Parameters:
		matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the 
		values of nsignals for a time window of length nsamples
		
	Returns:
		numpy.ndarray: 1D array containing the standard deviation of each column 
		from the input matrix
		list: list containing feature names for the quantities calculated.
	Author:
		Original: [lmanso]
		Revision and documentation: [fcampelo]
	"""

    ret = np.std(matrix, axis=0, ddof=1).flatten()
    names = ['std_' + str(i) for i in range(matrix.shape[1])]

    return ret, names


def feature_mean_d(h1, h2):
    """
    Computes the change in the means (backward difference) of all signals
    between the first and second half-windows, mean(h2) - mean(h1)

    Parameters:
        h1 (numpy.ndarray): 2D matrix containing the signals for the first
        half-window
        h2 (numpy.ndarray): 2D matrix containing the signals for the second
        half-window

    Returns:
        numpy.ndarray: 1D array containing the difference between the mean in h2
        and the mean in h1 of all signals
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]

    """
    ret = (feature_mean(h2)[0] - feature_mean(h1)[0]).flatten()

    # Fixed naming [fcampelo]
    names = ['mean_d_h2h1_' + str(i) for i in range(h1.shape[1])]
    return ret, names


def feature_mean_q(q1, q2, q3, q4):
    """
    Computes the mean values of each signal for each quarter-window, plus the
    paired differences of means of each signal for the quarter-windows, i.e.,
    feature_mean(q1), feature_mean(q2), feature_mean(q3), feature_mean(q4),
    (feature_mean(q1) - feature_mean(q2)), (feature_mean(q1) - feature_mean(q3)),
    ...

    Parameters:
        q1 (numpy.ndarray): 2D matrix containing the signals for the first
        quarter-window
        q2 (numpy.ndarray): 2D matrix containing the signals for the second
        quarter-window
        q3 (numpy.ndarray): 2D matrix containing the signals for the third
        quarter-window
        q4 (numpy.ndarray): 2D matrix containing the signals for the fourth
        quarter-window

    Returns:
        numpy.ndarray: 1D array containing the means of each signal in q1, q2,
        q3 and q4; plus the paired differences of the means of each signal on
        each quarter-window.
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]

    """
    v1 = feature_mean(q1)[0]
    v2 = feature_mean(q2)[0]
    v3 = feature_mean(q3)[0]
    v4 = feature_mean(q4)[0]
    ret = np.hstack([v1, v2, v3, v4,
                     v1 - v2, v1 - v3, v1 - v4,
                     v2 - v3, v2 - v4, v3 - v4]).flatten()

    # Fixed naming [fcampelo]
    names = []
    for i in range(4):  # for all quarter-windows
        names.extend(['mean_q' + str(i + 1) + "_" + str(j) for j in range(len(v1))])

    for i in range(3):  # for quarter-windows 1-3
        for j in range((i + 1), 4):  # and quarter-windows (i+1)-4
            names.extend(['mean_d_q' + str(i + 1) + 'q' + str(j + 1) + "_" + str(k) for k in range(len(v1))])

    return ret, names


def feature_stddev_d(h1, h2):
    """
    Computes the change in the standard deviations (backward difference) of all
    signals between the first and second half-windows, std(h2) - std(h1)

    Parameters:
        h1 (numpy.ndarray): 2D matrix containing the signals for the first
        half-window
        h2 (numpy.ndarray): 2D matrix containing the signals for the second
        half-window

    Returns:
        numpy.ndarray: 1D array containing the difference between the stdev in h2
        and the stdev in h1 of all signals
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]

    """

    ret = (feature_stddev(h2)[0] - feature_stddev(h1)[0]).flatten()

    # Fixed naming [fcampelo]
    names = ['std_d_h2h1_' + str(i) for i in range(h1.shape[1])]

    return ret, names


def feature_min(matrix):
    """
    Returns the minimum value of each signal for the full time window

    Parameters:
        matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the
        values of nsignals for a time window of length nsamples

    Returns:
        numpy.ndarray: 1D array containing the min of each column from the input matrix
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]
    """

    ret = np.min(matrix, axis=0).flatten()
    names = ['min_' + str(i) for i in range(matrix.shape[1])]
    return ret, names


def feature_min_d(h1, h2):
    """
    Computes the change in min values (backward difference) of all signals
    between the first and second half-windows, min(h2) - min(h1)

    Parameters:
        h1 (numpy.ndarray): 2D matrix containing the signals for the first
        half-window
        h2 (numpy.ndarray): 2D matrix containing the signals for the second
        half-window

    Returns:
        numpy.ndarray: 1D array containing the difference between the min in h2
        and the min in h1 of all signals
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]

    """

    ret = (feature_min(h2)[0] - feature_min(h1)[0]).flatten()

    # Fixed naming [fcampelo]
    names = ['min_d_h2h1_' + str(i) for i in range(h1.shape[1])]
    return ret, names

def feature_max(matrix):
    """
    Returns the maximum value of each signal for the full time window

    Parameters:
        matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the
        values of nsignals for a time window of length nsamples

    Returns:
        numpy.ndarray: 1D array containing the max of each column from the input matrix
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]
    """

    ret = np.max(matrix, axis=0).flatten()
    names = ['max_' + str(i) for i in range(matrix.shape[1])]
    return ret, names


def feature_max_d(h1, h2):
    """
    Computes the change in max values (backward difference) of all signals
    between the first and second half-windows, max(h2) - max(h1)

    Parameters:
        h1 (numpy.ndarray): 2D matrix containing the signals for the first
        half-window
        h2 (numpy.ndarray): 2D matrix containing the signals for the second
        half-window

    Returns:
        numpy.ndarray: 1D array containing the difference between the max in h2
        and the max in h1 of all signals
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]

    """

    ret = (feature_max(h2)[0] - feature_max(h1)[0]).flatten()

    # Fixed naming [fcampelo]
    names = ['max_d_h2h1_' + str(i) for i in range(h1.shape[1])]
    return ret, names

def feature_logcov(covM):
    """
    Computes the matrix logarithm of the covariance matrix of the signals.
    Since the matrix is symmetric, only the lower triangular elements
    (including the main diagonal) are returned.

    In the unlikely case that the matrix logarithm contains complex values the
    vector of features returned will contain the magnitude of each component
    (the covariance matrix returned will be in its original form). Complex
    values should not happen, as the covariance matrix is always symmetric
    and positive semi-definite, but the guarantee of real-valued features is in
    place anyway.

    Details:
        The matrix logarithm is defined as the inverse of the matrix
        exponential. For a matrix B, the matrix exponential is

            $ exp(B) = \sum_{r=0}^{\inf} B^r / r! $,

        with

            $ B^r = \prod_{i=1}^{r} B / r $.

        If covM = exp(B), then B is a matrix logarithm of covM.

    Parameters:
        covM (numpy.ndarray): 2D [nsignals x nsignals] covariance matrix of the
        signals in a time window

    Returns:
        numpy.ndarray: 1D array containing the elements of the upper triangular
        (incl. main diagonal) of the matrix logarithm of the covariance matrix.
        list: list containing feature names for the quantities calculated.
        numpy.ndarray: 2D array containing the matrix logarithm of covM

    Author:
        Original: [fcampelo]
    """
    log_cov = scipy.linalg.logm(covM)
    indx = np.triu_indices(log_cov.shape[0])
    ret = np.abs(log_cov[indx])

    names = []
    for i in np.arange(0, log_cov.shape[1]):
        for j in np.arange(i, log_cov.shape[1]):
            names.extend(['logcovM_' + str(i) + '_' + str(j)])

    return ret, names, log_cov

def feature_covariance_matrix(matrix):
    """
    Computes the elements of the covariance matrix of the signals. Since the
    covariance matrix is symmetric, only the lower triangular elements
    (including the main diagonal elements, i.e., the variances of eash signal)
    are returned.

    Parameters:
        matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the
        values of nsignals for a time window of length nsamples

    Returns:
        numpy.ndarray: 1D array containing the variances and covariances of the
        signals
        list: list containing feature names for the quantities calculated.
        numpy.ndarray: 2D array containing the actual covariance matrix
    Author:
        Original: [fcampelo]
    """

    covM = np.cov(matrix.T)
    indx = np.triu_indices(covM.shape[0])
    ret = covM[indx]

    names = []
    for i in np.arange(0, covM.shape[1]):
        for j in np.arange(i, covM.shape[1]):
            names.extend(['covM_' + str(i) + '_' + str(j)])

    return ret, names, covM

def feature_eigenvalues(covM):
    """
    Computes the eigenvalues of the covariance matrix passed as the function
    argument.

    Parameters:
        covM (numpy.ndarray): 2D [nsignals x nsignals] covariance matrix of the
        signals in a time window

    Returns:
        numpy.ndarray: 1D array containing the eigenvalues of the covariance
        matrix
        list: list containing feature names for the quantities calculated.
    Author:
        Original: [lmanso]
        Revision and documentation: [fcampelo]
    """

    ret = np.linalg.eigvals(covM).flatten()
    names = ['eigenval_' + str(i) for i in range(covM.shape[0])]
    return ret, names


def calc_energy(data):
    """
    Get the energy from the data via wavelet transformation.

    Author:
        Shivam Chaudhary https://github.com/shivam-199/Python-Emotion-using-EEG-Signal/blob/master/eeg_emotion_python.ipynb

    Parameters:
        data : 1 * N vector
    Returns:
        energy: float
    """
    wavelet_energy = np.nansum(np.log2(np.square(data)))
    return round(wavelet_energy, 3)

def calc_entropy(data):
    """
    Get the shannon entropy from the data via wavelet transformation.
    Author:
        Shivam Chaudhary https://github.com/shivam-199/Python-Emotion-using-EEG-Signal/blob/master/eeg_emotion_python.ipynb.

    Parameters:
        data : 1 * N vector

    Returns:
        energy: float
    """
    probability = np.square(data)
    shannon_entropy = -np.nansum(probability * np.log2(probability))
    return round(shannon_entropy, 3)

def feature_energy(matrix):
    """
        Generate wavelet energy for the given timeslice matrix by channels (axis=1).
        Adapted from https://github.com/shivam-199/Python-Emotion-using-EEG-Signal/blob/master/eeg_emotion_python.ipynb

        Parameter:
            matrix: 2D ndrray of each time slice containing [nsamples x nsignals]
        Returns:
            ret: 1D ndarray of calculated energy by column.
            names: list containing feature names for the energies calculated.
    """
    ret = []
    for col in matrix.T:
        data = col
        #DWT by column
        (data, coeff_d) = pywt.dwt(data, WAVELET)
        ret.append(calc_energy(coeff_d))
    names = ['eng_' + str(i) for i in range(matrix.shape[1])]
    return ret, names

def feature_entropy(matrix):
    """
        Generate wavelet entropy for the given timeslice matrix by channels (axis=1).
        Adapted from https://github.com/shivam-199/Python-Emotion-using-EEG-Signal/blob/master/eeg_emotion_python.ipynb

        Parameter:
            matrix: 2D ndrray of each time slice containing [nsamples x nsignals]
        Returns:
            ret: 1D ndarray of calculated entropy by column.
            names: list containing feature names for the energies calculated.
    """
    ret = []
    for col in matrix.T:
        data = col
        # DWT by column
        (data, coeff_d) = pywt.dwt(data, WAVELET)
        ret.append(calc_entropy(coeff_d))
    names = ['ent_' + str(i) for i in range(matrix.shape[1])]
    return ret, names

def feature_activity(matrix):
    """
    	Computes the Hjorth parameter activity of each signal for the full time window

    	Parameters:
    		matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the
    		values of nsignals for a time window of length nsamples

    	Returns:
    		numpy.ndarray: 1D array containing the standard deviation of each column
    		from the input matrix
    		list: list containing feature names for the quantities calculated.
    """
    ret = np.var(matrix, axis=0)
    names = ['act_' + str(i) for i in range(matrix.shape[1])]
    return ret, names

def calc_der(col, timestamps):
    """
        Calculates the derivative for each data point given a matrix.

        Parameters
        ----------
        col: 1D ndarray containing the channel's values
        timestamps: 1D ndarray of timestamps
        Returns
        -------
        ret: 1D ndarray of derivatives
    """
    ret = []
    for i in range(col.shape[0]):
        der = 0
        # handle edge case
        if i == 0:
            der = (col[i + 1] - col[i]) / (timestamps[i + 1] - timestamps[i])
        elif i == (len(col) - 1):
            if not timestamps[i] - timestamps[i - 1] == 0:
                der = (col[i] - col[i - 1]) / (timestamps[i] - timestamps[i - 1])
        else:
            if not timestamps[i + 1] - timestamps[i - 1] == 0:
                der = (col[i + 1] - col[i - 1])/ (timestamps[i + 1] - timestamps[i - 1])
        ret.append(der)
    return ret

def feature_mobility(matrix, timestamps):
    """
    	Computes the Hjorth parameter activity of each signal for the full time window

    	Parameters
    	----------
    	matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the
    	    values of nsignals for a time window of length nsamples

    	Returns
    	----------
    	numpy.ndarray: 1D array containing the standard deviation of each column
    		from the input matrix
    	list: list containing feature names for the quantities calculated.
    """
    ret = []
    for col in matrix.T:
        # Calculation for mobility from https://www.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/27561/versions/1/previews/MATS/HjorthParameters.m/index.html
        dxV = np.var(calc_der(col, timestamps))
        ddxV = np.var(col)
        mob = np.sqrt(dxV / ddxV)
        ret.append(mob)
    names = ['mob_' + str(i) for i in range(matrix.shape[1])]
    return ret, names

def feature_complexity(mob_ret, timestamps):
    ret = []
    for mob in range(len(mob_ret)):
        dxV = 0
        # Calculation for complexity from https://www.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/27561/versions/1/previews/MATS/HjorthParameters.m/index.html
        if mob == 0:
            dxV = (mob_ret[1] - mob) / (timestamps[1] - timestamps[mob])
        elif mob == len(mob_ret) - 1:
            if not timestamps[mob] - timestamps[mob - 1] == 0:
                dxV = (mob - mob_ret[mob - 1]) / (timestamps[mob] - timestamps[mob - 1])
        else:
            if not timestamps[mob + 1] - timestamps[mob - 1] == 0:
                dxV = (mob_ret[mob + 1] - mob_ret[mob - 1]) / (timestamps[mob + 1] - timestamps[mob - 1])
        comp = dxV / mob_ret[mob]
        ret.append(comp)

    names = ['comp_' + str(i) for i in range(len(mob_ret))]
    return ret, names

def generate_feature_vector(matrix, state, timestamps):
    """
	Calculates all previously defined features and concatenates everything into 
	a single feature vector.
	
	Parameters:
		matrix (numpy.ndarray): 2D [nsamples x nsignals] matrix containing the 
		values of nsignals for a time window of length nsamples
		state (str): label associated with the time window represented in the 
		matrix.
		
	Returns:
		numpy.ndarray: 1D array containing all features
		list: list containing feature names for the features
	Author:
		Original: [lmanso]
		Updates and documentation: [fcampelo]
	"""

    # Extract the half- and quarter-windows
    h1, h2 = np.split(matrix, [int(matrix.shape[0] / 2)])
    q1, q2, q3, q4 = np.split(matrix,
                              [int(0.25 * matrix.shape[0]), int(0.50 * matrix.shape[0]), int(0.75 * matrix.shape[0])])

    var_names = []

    x, v = feature_mean(matrix)
    var_names += v
    var_values = x
    """
    x, v = feature_stddev(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])
    """
    x, v = feature_stddev_d(h1, h2)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_mean_d(h1, h2)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_mean_q(q1, q2, q3, q4)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_min(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_min_d(h1, h2)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_max(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_max_d(h1, h2)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v, covM = feature_covariance_matrix(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])
    """
    x, v = feature_eigenvalues(covM)
    var_names += v
    var_values = np.hstack([var_values, x])
    
    x, v, log_cov = feature_logcov(covM)
    var_names += v
    var_values = np.hstack([var_values, x])
    """
    x, v = feature_energy(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_entropy(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])

    x, v = feature_activity(matrix)
    var_names += v
    var_values = np.hstack([var_values, x])

    mob_ret, v = feature_mobility(matrix, timestamps)
    var_names += v
    var_values = np.hstack([var_values, mob_ret])

    x, v = feature_complexity(mob_ret, timestamps)
    var_names += v
    var_values = np.hstack([var_values, x])

    if state != None:
        var_values = np.hstack([var_values, np.array([state])])
        var_names += ['Label']

    return var_values, var_names


"""
Returns a number of feature vectors from a labeled CSV file, and a CSV header 
corresponding to the features generated.
full_file_path: The path of the file to be read
samples: size of the resampled vector
period: period of the time used to compute feature vectors
state: label for the feature vector
"""


def generate_feature_vectors_from_samples(file_path, nsamples, period=1.0,
                                          state=None,
                                          remove_redundant=False,
                                          cols_to_ignore=None):
    """
	Reads data from CSV file in "file_path" and extracts statistical features 
	for each time window of width "period". 
	
	Details:
	Successive time windows overlap by period / 2. All signals are resampled to 
	"nsample" points to maintain consistency. Notice that the removal of 
	redundant features (regulated by "remove_redundant") is based on the 
	feature names - therefore, if the names output by the other functions in 
	this script are changed this routine needs to be revised.
	
	Parameters:
		file_path (str): file path to the CSV file containing the records
		nsamples (int): number of samples to use for each time window. The 
		signals are down/upsampled to nsamples
		period (float): desired width of the time windows, in seconds
		state(str/int/float): label to attribute to the feature vectors
 		remove_redundant (bool): Should redundant features be removed from the 
	    resulting feature vectors (redundant features are those that are 
	    repeated due to the 1/2 period overlap between consecutive windows).
		cols_to_ignore (array): array of columns to ignore from the input matrix
		 
		
	Returns:
		numpy.ndarray: 2D array containing features as columns and time windows 
		as rows.
		list: list containing the feature names
	Author:
		Original: [lmanso]
		Reimplemented: [fcampelo]
	"""
    # Read the matrix from file
    matrix = matrix_from_csv_file(file_path)
    # We will start at the very beginning of the file
    t = 0.

    # No previous vector is available at the start
    previous_vector = None

    # Initialise empty return object
    ret = None
    headers = []
    # Until an exception is raised or a stop condition is met
    while True:
        # Get the next slice from the file (starting at time 't', with a
        # duration of 'period'
        # If an exception is raised or the slice is not as long as we expected,
        # return the current data available
        try:
            s, dur = get_time_slice(matrix, period=period, start=t)
            if cols_to_ignore is not None:
                s = np.delete(s, cols_to_ignore, axis=1)
        except IndexError:
            break
        if len(s) == 0:
            break
        if dur < 0.9 * period:
            break

        # Perform the resampling of the vector
        ry, rx = scipy.signal.resample(s[:, 1:], num=nsamples,
                                       t=s[:, 0], axis=0)

        # Slide the slice by 1/2 period
        t += 0.5 * period
        # Compute the feature vector. We will be appending the features of the
        # current time slice and those of the previous one.
        # If there was no previous vector we just set it and continue
        # with the next vector.
        timestamps = s[:, 0]
        r, headers = generate_feature_vector(ry, state, timestamps)

        if previous_vector is not None:
            # If there is a previous vector, the script concatenates the two
            # vectors and adds the result to the output matrix
            feature_vector = np.hstack([previous_vector, r])

            if ret is None:
                ret = feature_vector
            else:
                ret = np.vstack([ret, feature_vector])

        # Store the vector of the previous window
        previous_vector = r
        if state is not None:
            # Remove the label (last column) of previous vector
            previous_vector = previous_vector[:-1]

    feat_names = ["lag1_" + s for s in headers[:-1]] + headers

    if remove_redundant:
        # Remove redundant lag window features
        to_rm = ["lag1_mean_q3_", "lag1_mean_q4_", "lag1_mean_d_q3q4_"]

        # Remove redundancies
        for i in range(len(to_rm)):
            for j in range(ry.shape[1]):
                rm_str = to_rm[i] + str(j)
                idx = feat_names.index(rm_str)
                feat_names.pop(idx)
                ret = np.delete(ret, idx, axis=1)

    # Return
    return ret, feat_names


"""
def generate_feature_vectors_from_bci(file_path, nsamples, period,
                                      state=None,
                                      remove_redundant=False,
                                      cols_to_ignore=None):
    # Read the matrix from file
    matrix = matrix_from_bci_file(file_path)

    # We will start at the very beginning of the file
    t = matrix[0,0]
    # No previous vector is available at the start
    previous_vector = None

    # Initialise empty return object
    ret = None
    headers = []
    # Until an exception is raised or a stop condition is met
    while True:
        # Get the next slice from the file (starting at time 't', with a
        # duration of 'period'
        # If an exception is raised or the slice is not as long as we expected,
        # return the current data available
        try:
            s, dur = get_time_slice(matrix, period, start=t)
            if cols_to_ignore is not None:
                s = np.delete(s, cols_to_ignore, axis=1)
        except IndexError:
            break
        if len(s) == 0:
            break
        if dur < 0.9 * period:
            break
        # Perform the resampling of the vector
        ry, rx = scipy.signal.resample(s[:, 1:], num=nsamples,
                                       t=s[:, 0], axis=0)

        # Slide the slice by 1/2 period
        t += 0.5 * period

        # Compute the feature vector. We will be appending the features of the
        # current time slice and those of the previous one.
        # If there was no previous vector we just set it and continue
        # with the next vector.
        timestamps = s[:, 0]

        r, headers = generate_feature_vector(ry, 0, timestamps)

        if previous_vector is not None:
            # If there is a previous vector, the script concatenates the two
            # vectors and adds the result to the output matrix
            feature_vector = np.hstack([previous_vector, r])

            if ret is None:
                ret = feature_vector
            else:
                ret = np.vstack([ret, feature_vector])

        # Store the vector of the previous window
        previous_vector = r
        if state is not None:
            # Remove the label (last column) of previous vector
            previous_vector = previous_vector[:-1]

    feat_names = ["lag1_" + s for s in headers[:-1]] + headers

    if remove_redundant:
        # Remove redundant lag window features
        to_rm = ["lag1_mean_q3_", "lag1_mean_q4_", "lag1_mean_d_q3q4_"]

        # Remove redundancies
        for i in range(len(to_rm)):
            for j in range(ry.shape[1]):
                rm_str = to_rm[i] + str(j)
                idx = feat_names.index(rm_str)
                feat_names.pop(idx)
                ret = np.delete(ret, idx, axis=1)

    # Return
    return ret, feat_names
"""