This is a modified version of the FED3 Bandit code in the FED3 library that has been optimized for synchronization with photometry or ephys recordings.

The .ino code in this folder is modified from the version in the FED3 library in the following ways:
  1. We added delays to separate events in recordings
  2. logLeftpoke and logRightpoke were removed to speed up function without engaging the SD card
  3. We added a custom Timeout function (at bottom of this script) to send pulses during Timeouts
  4. We added following pulses via the FED3 output port for sycnhronization with recording:  
    1 pulse = Left poke  
    2 pulses = Right poke  
    3 pulses = Pellet retrieval  
    4 pulses = Pellet drop (*** this requires a modified fed3.cpp library file to work! *** )  
     5 pulses = Rewarded poke  (these can be commented out for 100:0 sessions, as all pokes are rewarded/not)  
     6 pulses = Unrewarded poke (these can be commented out for 100:0 sessions, as all pokes are rewarded/not)    

  5. To make 4 output pulses work for Pellet drop we need to modified the FED3.cpp library file as follows: 
     Add this BNC function to the Feed() function in the fed3.cpp library file after if (pelletDispensed == true) {    
        BNC(50, 4);  //send 4 pulses of 50ms each to the BNC port when the pellet is dispensed
     A modified .cpp file is in this folder

  
  
