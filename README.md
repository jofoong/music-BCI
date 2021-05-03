# music-BCI
This project requires [SuperCollider](https://supercollider.github.io/download) to run.  

In this root folder you will find the main file for generating sound, [sound_generator.scd](https://github.com/jolenefoong/music-BCI/blob/main/sound_generator.scd), and a sample file converted from EEGs, [sc-input.txt](https://github.com/jolenefoong/music-BCI/blob/main/sc-input.txt). The file was sorted by mental state.  
<img src="musicBCI/sc-interface.png" height="600">  
SuperCollider interface

##### Booting the audio server and playing sound
Each line in SuperCollider is run line by line, or in blocks encased by parentheses. Boot the audio server by running the single line ```s.boot;``` with the pointer on any region of the line using Shift+Enter. Once the server is up and running, load in the blocks by clicking anywhere within their parentheses with Ctrl+Enter.

##### Troubleshooting: the audio server cannot boot
- stop SC, confirm sclang/scide/scsynth are down with TaskManager
- Open Event Viewer, delete all application and system logs
- Open powershell as administrator, add a 6005 event: ```write-eventlog -logname System -source 'EventLog' -EventID 6005 -EntryType Information -Category 0 -message "foobar"```
- Restart SC

##### OpenBCI GUI
In the /old directory, it contains an implemented W_ProminentFrequency.pde for visualising the current frequency that is most prominent. Original code for the OpenBCI GUI is from  https://github.com/OpenBCI/OpenBCI_GUI, and requires [Processing](https://docs.openbci.com/docs/06Software/01-OpenBCISoftware/GUIDocs) to run as a sketch.
<img src="old/prom-freq.png" height="400">
Demonstrating prominent frequency
