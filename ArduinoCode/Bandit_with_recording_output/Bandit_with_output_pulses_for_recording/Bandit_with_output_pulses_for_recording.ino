/*
  Feeding experimentation device 3 (FED3)
  Bandit task

  This example shows a simple 2-armed bandit task. Here, the reward probabilities of left and right 
  always add 100, and change simultaneously. Thus, this is a special case of the 2-armed bandit task 
  that is equivalent to a probabilistic reversal task. 

  This code is modified for recordings in the following ways:
  - We added delays to separate events in recordings
  - We added a custom Timeout function (at bottom of this script) to send pulses during Timeouts
  - We also added following pulses via the FED3 output port for sycnhronization with recording:
    1 pulse = Left poke
    2 pulses = Right poke
    3 pulses = Pellet retrieval
    4 pulses = Pellet drop (*** this requires a modified fed3.cpp library file to work! *** )

  To make 4 output pulses work for Pellet drop: 
  Add this BNC function to the Feed() function in the fed3.cpp library file after if (pelletDispensed == true) {    
      BNC(50, 4);  //send 4 pulses of 50ms each to the BNC port when the pellet is dispensed

  Optional (these are not needed for 100:0 bandits so are commented out, but they can be useful when recording 80:20 bandits)
    5 pulses = Rewarded poke  (these are not needed for 100:0 sessions, as all pokes are rewarded/not)
    6 pulses = Unrewarded poke (these are not needed for 100:0 sessions, as all pokes are rewarded/not)
  
  logLeftpoke and logRightpoke were removed to speed up function without engaging the SD card

  Code written by alexxai@wustl.edu and meaghan.creed@wustl.edu and alegariamacal@wustl.edu
  June, 2023

  This project is released under the terms of the Creative Commons - Attribution - ShareAlike 3.0 license:
  human readable: https://creativecommons.org/licenses/by-sa/3.0/
  legal wording: https://creativecommons.org/licenses/by-sa/3.0/legalcode
  Copyright (c) 2020 Lex Kravitz
*/

#include <FED3.h>          //Include the FED3 library
String sketch = "Bandit";  //Unique identifier text for each sketch, change string only.
FED3 fed3(sketch);         //Start the FED3 object - don't change

int pellet_counter = 0;     //pellet counter variable
int timeoutIncorrect = 10;  //timeout duration in seconds, set to 0 to remove the timeout
int probs[2] = { 100, 0 };  //Reward probability options
int new_prob = 0;
String last_poke = "";
int random_n = 0;

void setup() {
  fed3.countAllPokes = false;
  //fed3.LoRaTransmit = true;
  fed3.pelletsToSwitch = 30;      // Number of pellets required to finish the block and change reward probabilities
  fed3.prob_left = 100;           // Initial reward probability of left poke
  fed3.prob_right = 0;            // Initial reward probability of right poke
  fed3.allowBlockRepeat = false;  // Whether the same probabilities can be used for two blocks in a row
  fed3.begin();                   // Setup the FED3 hardware, all pinmode screen etc, initialize SD card
  randomSeed(12);
}

void loop() {
  //////////////////////////////////////////////////////////////////////////////////
  //  This is the main bandit task. In general it will be composed of three parts:
  //  1. Set up conditions to trigger a change in reward probabilities
  //  2. Set up behavior upon a left poke
  //  3. Set up behavior upon a right poke
  //////////////////////////////////////////////////////////////////////////////////
  fed3.run();  //Call fed.run at least once per loop

  // This is part 1. In this example, reward probabilities will be switched when 30 rewards
  // (value of fed3.pelletsToswitch assigned in line 35) are obtained. Notice that in this example
  // the reward probability of left + reward probability of right always add to 100. Additionally
  // in this example, the reward probabilities in the new block are not allowed to be the same to
  // the reward probability of the previous block.
  if (pellet_counter == fed3.pelletsToSwitch) {
    pellet_counter = 0;
    new_prob = probs[random(0, 2)];
    if (!fed3.allowBlockRepeat) {
      while (new_prob == fed3.prob_left) {
        new_prob = probs[random(0, 2)];
      }
      fed3.prob_left = new_prob;
      fed3.prob_right = 100 - fed3.prob_left;
    } else {
      fed3.prob_left = new_prob;
      fed3.prob_right = 100 - fed3.prob_left;
    }
  }

  // This is part 2. This is the behavior of the task after a left poke.
  // Notice that in this example pellet_counter only increases if a pellet
  // was actually delivered (fed.Feed() is called). Additionally, the timeout
  // resets if the mouse pokes during timeout, and also white noise is present
  // through the whole timeout
  if (fed3.Left) {
    fed3.BNC(50, 1);
    fed3.BlockPelletCount = pellet_counter;
    //fed3.logLeftPoke();                                 //Log left poke
    fed3.LeftCount++;
    delay(500);
    random_n = random(100);
    if (random(100) < fed3.prob_left) {  //Select a random number between 0-100 and ask if it is between 0-80 (80% of the time).  If so:
      //fed3.BNC(50,5);                 // comment this out for 100-0 task
      fed3.Tone(800, 2000);  //Deliver 800Hz tone for 2s (this is different from FED3 conditionedStimulus BTW
      delay(2000);
      fed3.Feed();  //Deliver pellet
      fed3.BNC(50, 3);
      pellet_counter++;  //Increase pellet counter by one
    } else {             //If random number is between 81-100 (20% of the time)
      //fed3.BNC(50,6);
      fed3.Tone(300, 600);  //Play the error tone

      // clear poke flags before entering timeout
      fed3.Left = false;
      fed3.Right = false;

      timeoutWithTTL(timeoutIncorrect);
    }
    last_poke = "Left";
    fed3.Left = false;  //clear Left flag
  }

  // This is part 3. This is the behavior of the task after a right poke.
  // Notice that in this example the behavior after a right poke is exactly the
  // same as the the behvaior after a left poke.
  if (fed3.Right) {
    fed3.BNC(50, 2);
    fed3.BlockPelletCount = pellet_counter;
    //fed3.logRightPoke();                                  //Log Right poke
    fed3.RightCount++;
    delay(500);
    if (random(100) < fed3.prob_right) {  //Select a random number between 0-100 and ask if it is between 80-100 (20% of the time).  If so:
      //fed3.BNC(50,5);
      fed3.Tone(800, 2000);  //Deliver 800Hz tone for 2s (this is different from FED3 conditionedStimulus BTW
      delay(2000);
      fed3.Feed();  //Deliver pellet
      fed3.BNC(50, 3);
      pellet_counter++;  //Increase pellet counter by one
    } else {             //If random number is between 0-80 (80% of the time)
      //fed3.BNC(50,6);
      fed3.Tone(300, 600);  //Play the error tone

      // clear poke flags before entering timeout
      fed3.Left = false;
      fed3.Right = false;

      timeoutWithTTL(timeoutIncorrect);
    }
    last_poke = "Right";
    fed3.Right = false;  //clear Right flag
  }
}

// ------------------------------------------------
// Custom timeout:
// same behavior as fed3.Timeout(timeoutIncorrect)
// + sends TTL pulses when mouse pokes during timeout
// ------------------------------------------------
void timeoutWithTTL(unsigned long timeoutIncorrect) {
  unsigned long start = millis();
  while ((millis() - start) < (timeoutIncorrect * 1000)) {
    // play white noise during timeout
    fed3.Noise(250);  //200 ms noise tone (we use 220 to make sure it lasts at least 200ms) is blocking but OK for behavior

    if (fed3.Left) {
      fed3.BNC(50, 1);
      start = millis();  //reset the timeout with each poke
    }

    if (fed3.Right) {
      fed3.BNC(50, 2);
      start = millis();  //reset the timeout with each poke
    }

    // clear poke flags
    fed3.Left = false;
    fed3.Right = false;
  }
}