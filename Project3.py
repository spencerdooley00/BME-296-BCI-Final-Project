# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 16:36:55 2021

@author: spenc
"""
#%%
import mne
from mne.io.pick import channel_type
import numpy as np
import matplotlib.pyplot as plt
from mne.preprocessing import ICA


from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

def load_data(subject):
    '''
    

    Parameters
    ----------
    subject : string of subject number (two digits)
        DESCRIPTION.

    Returns
    -------
    fif_file : MNE FIF file
        DESCRIPTION.
    raw_eeg_data : Array of size (channels, samples) - samples depend on which subject is read
        DESCRIPTION.
    eeg_times : Array of time points eeg samples were taken
        DESCRIPTION.
    channel_names: Array of channel names (each is string)
        DESCRIPTION.
    fs : float
        DESCRIPTION.

    '''

    fif_file=mne.io.read_raw_fif(f'data/P{subject}-raw.fif', preload=True)
    raw_eeg_data = fif_file.get_data()[0:64, :]
    channel_names = fif_file.ch_names[0:64]
    eeg_times = fif_file.times
    fs = fif_file.info['sfreq']
    channel_names = np.array(channel_names)
    return fif_file, raw_eeg_data, eeg_times, channel_names, fs
    



def get_eeg_epochs(fif_file, raw_eeg_data, start_time, end_time, fs):
    '''
    

    Parameters
    ----------
    fif_file : TYPE
        DESCRIPTION.
    raw_eeg_data : TYPE
        DESCRIPTION.
    start_time : TYPE
        DESCRIPTION.
    end_time : TYPE
        DESCRIPTION.
    fs : TYPE
        DESCRIPTION.

    Returns
    -------
    eeg_epochs : TYPE
        DESCRIPTION.
    epoch_times : TYPE
        DESCRIPTION.
    target_events : TYPE
        DESCRIPTION.
    all_trials : TYPE
        DESCRIPTION.
    event_stimulus_ids : TYPE
        DESCRIPTION.

    '''
    eeg_epochs = np.array([])
    all_trials = mne.find_events(fif_file)
    all_trials = all_trials[np.logical_not(np.logical_and(all_trials[:,2] > 20, all_trials[:,2] >2000))]
    target_events = all_trials[np.logical_not(np.logical_and(all_trials[:,2] > 20, all_trials[:,2] > 999))]
    
    
    event_stimulus_ids = []
    for event_index in range(len(target_events)):
        stimulus_id = target_events[event_index, 2]//10
        event_stimulus_ids.append(stimulus_id)
        
    event_start_times = all_trials[:, 0]
    for event_start_time in event_start_times:
        start_epoch = int(event_start_time) - int(start_time*fs)
        end_epoch = int(int(event_start_time) + (end_time*fs))
        epoch_data = raw_eeg_data[:, start_epoch:end_epoch]
        eeg_epochs = np.append(eeg_epochs, epoch_data)
    eeg_epochs = np.reshape(eeg_epochs, [len(all_trials), np.size(raw_eeg_data, axis=0), int(end_time*fs)])
    epoch_times = np.arange(0, np.size(eeg_epochs, axis=2))
    return eeg_epochs, epoch_times, target_events, all_trials, event_stimulus_ids


def get_event_truth_labels(all_trials):
    '''
    

    Parameters
    ----------
    all_trials : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    is_target_event = np.array([])
    for trial_index in range(len(all_trials)):
        if all_trials[trial_index, 2] < 1000 :
            is_target_event = np.append(is_target_event,True)
        elif all_trials[trial_index, 2] < 2000 :
            is_target_event = np.append(is_target_event,False)
    return np.array(is_target_event, dtype='bool')


# def get_tempo_labels(event_stimulus_ids):
#     tempo_labels=[]
#     for stimulus_id in event_stimulus_ids:
#         if stimulus_id == 1 or stimulus_id==11:
#             tempo=212
#         elif stimulus_id == 2 or stimulus_id==12:
#             tempo=189
#         elif stimulus_id == 3 or stimulus_id==13:
#             tempo=200
#         elif stimulus_id == 4 or stimulus_id==14:
#             tempo=160
#         elif stimulus_id == 21:
#             tempo = 178
#         elif stimulus_id == 22:
#             tempo = 166
#         elif stimulus_id == 23:
#             tempo = 104
#         elif stimulus_id == 24:
#             tempo = 140
        
#         tempo_labels.append(tempo)
#     return np.array(tempo_labels)



# def get_truth_labels(tempo_labels):

#     is_trial_greater_than_170bpm = [tempo_labels[:] >= 170]
#     return is_trial_greater_than_170bpm[0]





def plot_power_spectrum(eeg_epochs_fft, fft_frequencies, is_target_event, channels_to_plot, channel_names):
    '''
    

    Parameters
    ----------
    eeg_epochs_fft : Array of complex128
        3-D array holding epoched data in the frequency domain for each trial.
    fft_frequencies : Array of float64
        Array containing the frequency corresponding to each column of the Fourier transform data.
    is_trial_15Hz : 1-D boolean array 
        Boolean array representing trials in which flashing at 15 Hz occurred.
    channels_to_plot : list 
        list of channels we wish to plot the raw data for.
    channels : Array of str128
        List of channel names from original dataset.

    Returns
    -------
    None.

    '''
    target_trials = eeg_epochs_fft[is_target_event]
    non_target_trials = eeg_epochs_fft[~is_target_event]
    
    # Calculate mean power spectra
    mean_target_trials = np.mean(abs(target_trials), axis=0)**2
    mean_non_target_trials = np.mean(abs(non_target_trials), axis=0)**2
    
    mean_power_spectrum_target = mean_target_trials/mean_target_trials.max(axis=1, keepdims=True)
    mean_power_spectrum_nontarget = mean_non_target_trials/mean_non_target_trials.max(axis=1, keepdims=True)

    power_in_db_target = 10*np.log10(mean_power_spectrum_target)
    power_in_db_nontarget = 10*np.log10(mean_power_spectrum_nontarget)

    # Plot mean power spectrum of 12 and 15 Hz trials
    for channel_index, channel in enumerate(channels_to_plot):
        index_to_plot = np.where(channel_names==channel)[0][0]
        ax1=plt.subplot(len(channels_to_plot), 1, channel_index+1)
        plt.plot(fft_frequencies,power_in_db_target[index_to_plot], label='target', color='red')
        plt.plot(fft_frequencies,power_in_db_nontarget[index_to_plot], label='nontarget', color='green')
        plt.legend()
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')
        plt.tight_layout()

        plt.grid()
    plt.savefig(f'figures/MeanPowerSpectrumChannel{channel}')

    

def perform_ICA(raw_fif_file, channel_names, top_n_components):
    '''
    

    Parameters
    ----------
    raw_fif_file : TYPE
        DESCRIPTION.
    channel_names : TYPE
        DESCRIPTION.
    top_n_components : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    picks_eeg = mne.pick_types(raw_fif_file.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')[0:64]
    ica = mne.preprocessing.ICA(n_components=64, random_state=97, max_iter=800)
    # picks = mne.pick_types(raw_fif_file.info, meg=False, eeg=True, eog=False, stim=False)
    ica.fit(raw_fif_file, picks=picks_eeg, decim=3, reject=dict(mag=4e-12, grad=4000e-13))
    mixing_matrix = ica.mixing_matrix_
    ica.plot_components(picks = np.arange(0,top_n_components))

def extract_eeg_features(eeg_epochs):
    '''
    

    Parameters
    ----------
    eeg_epochs : TYPE
        DESCRIPTION.

    Returns
    -------
    mean_eeg : TYPE
        DESCRIPTION.
    rms_eeg : TYPE
        DESCRIPTION.
    std_eeg : TYPE
        DESCRIPTION.

    '''
    mean_eeg = np.mean(eeg_epochs, axis=2)
    rms_eeg = np.sqrt(np.mean(eeg_epochs**2, axis=2))
    std_eeg = np.std(eeg_epochs, axis=2)

    return mean_eeg, rms_eeg, std_eeg


# %%
