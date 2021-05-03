# music-BCI
This project requires [SuperCollider](https://supercollider.github.io/download) to run.  

In this root folder you will find the main file for generating sound, [sound_generator.scd](https://github.com/jolenefoong/music-BCI/blob/main/sound_generator.scd), and a sample file converted from EEGs, [sc-input.txt](https://github.com/jolenefoong/music-BCI/blob/main/sc-input.txt). The file was sorted by mental state.  

##### Booting the audio server and playing sound
Each line in SuperCollider is run line by line, or in blocks encased by parentheses. Boot the audio server by running the single line ```s.boot;``` with the pointer on any region of the line using Shift+Enter. Once the server is up and running, load in the blocks by clicking anywhere within their parentheses with Ctrl+Enter.
