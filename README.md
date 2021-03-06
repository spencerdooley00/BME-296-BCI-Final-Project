# BME-296-BCI-Final-Project


Our project uses a public dataset of EEG recordings taken during music perception and imagination. The data was acquired during an ongoing study that has currently comprised of 10 subjects listening to and imagining 12 short music fragments (each 7-16 seconds long) taken from well-known musical pieces. The stimuli were selected from different genres and capture several musical dimensions such as tempo and the presence of lyrics. The dataset is intended to enable music information retrieval researchers to easily test and adapt their existing approaches for music analysis like fingerprinting, beat tracking or tempo estimation on this new kind of data. The 10 subjects are currently denoted as P01, P04, P05, P06, P07, P09, P11, P12, P13, and P14. This dataset is a result of ongoing joint work between the Owen Lab and the Music and Neuroscience Lab at the Brain and Mind Institute of the University of Western Ontario. Information on loading the data in Python is listed below:

Link to download data by subject: http://bmi.ssc.uwo.ca/OpenMIIR-RawEEG_v1/

Notes pertaining to data:

- Loaded in MNE’s .fif format
- Band-pass filtered and re-referenced electrode data
- Raw EEG, EEG sample times (in seconds), channel names, and the sampling frequency can be extracted from the file
- Raw EEG of size (channels, time points) in our case (64, 2478166) for P01
- EEG sample times of length (sample time points) - 2478166 for P01
- 64 channels, channel names are a list of channels - for all subjects
- Sampling frequency of 512 Hz for all subjects 


Epoching Data:
- Use MNE’s built in find_events() and Epochs() functions to epoch the data into the 240 trials 

Code to load and handle data:


Make sure to import the MNE python
```
import mne
```


Reading the .fif file into python
```
fif_file=mne.io.read_raw_fif(f'{subject}-raw.fif', preload=True)
```


Our load_data() function that loads the fif file and extracts the data we will use. Before the data is extracted from the file
it is band-pass filtered between 1 - 30 Hz and re-referenced to the average across electrodes. Fif file is also returned if user 
wants to extract different data.
```
def load_data(subject):
    print('Band-pass filtering between 1 - 30 Hz...')
    fif_file.filter(1,30)
    print('Rereferencing the raw data to the average across electrodes...')
    fif_file.set_eeg_reference(ref_channels='average')
    fif_file=mne.io.read_raw_fif(f'{subject}-raw.fif', preload=True)
    raw_eeg_data = fif_file.get_data()
    channel_names = fif_file.ch_names[0:64]
    eeg_times = fif_file.times
    fs = fif_file.info['sfreq']
    return fif_file, raw_eeg_data, eeg_times, channel_names, fs
    

fif_file, raw_eeg_data, eeg_times, channel_names = load_data('P01')
```



Sources and Inspiration:  

-   https://www.frontiersin.org/articles/10.3389/fpsyg.2017.01255/full
-   http://ismir2015.uma.es/articles/224_Paper.pdf





