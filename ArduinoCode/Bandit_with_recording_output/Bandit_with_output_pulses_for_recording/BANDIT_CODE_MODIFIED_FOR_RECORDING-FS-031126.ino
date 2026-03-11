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
    5 pulses = Rewarded poke
    6 pulses = Unrewarded poke
  
  logLeftpoke and logRightpoke were removed to speed up function without engaging the SD card

  Code written by alexxai@wustl.edu and meaghan.creed@wustl.edu and alegariamacal@wustl.edu
  June, 2023

  Copyright (c) 2020 Lex Kravitz
*/

#include <FED3.h>

String sketch = "Bandit";
FED3 fed3(sketch);

int pellet_counter = 0;
int timeoutIncorrect = 10;
int probs[2] = {100, 0};
int new_prob = 0;

String last_poke = "";
int random_n = 0;

void setup() {

  fed3.countAllPokes = false;
  //fed3.LoRaTransmit = true;

  fed3.pelletsToSwitch = 30;
  fed3.prob_left = 100;
  fed3.prob_right = 0;
  fed3.allowBlockRepeat = false;

  fed3.begin();

  randomSeed(12);

  fed3.disableSleep();
}

void loop() {

  fed3.run();

  // -------------------------------
  // Block switch logic
  // -------------------------------

  if (pellet_counter == fed3.pelletsToSwitch) {

    pellet_counter = 0;

    new_prob = probs[random(0,2)];

    if (!fed3.allowBlockRepeat) {

      while (new_prob == fed3.prob_left) {
        new_prob = probs[random(0,2)];
      }

      fed3.prob_left  = new_prob;
      fed3.prob_right = 100 - fed3.prob_left;

    } else {

      fed3.prob_left  = new_prob;
      fed3.prob_right = 100 - fed3.prob_left;

    }
  }

  // =========================================================
  // LEFT POKE
  // =========================================================

  if (fed3.Left) {

    fed3.BNC(50,1);

    fed3.BlockPelletCount = pellet_counter;

    delay(500);

    random_n = random(100);

    if (random(100) < fed3.prob_left) {

      fed3.Tone(800,2000);

      delay(2000);

      fed3.Feed();

      fed3.BNC(50,3);

      pellet_counter++;

    } else {

      fed3.Tone(300,600);

      // clear poke flags before entering timeout
      fed3.Left  = false;
      fed3.Right = false;

      timeoutWithTTL(timeoutIncorrect);
    }

    last_poke = "Left";

    fed3.Left = false;
  }

  // =========================================================
  // RIGHT POKE
  // =========================================================

  if (fed3.Right) {

    fed3.BNC(50,2);

    fed3.BlockPelletCount = pellet_counter;

    delay(500);

    if (random(100) < fed3.prob_right) {

      fed3.Tone(800,2000);

      delay(2000);

      fed3.Feed();

      fed3.BNC(50,3);

      pellet_counter++;

    } else {

      fed3.Tone(300,600);

      // clear poke flags before entering timeout
      fed3.Left  = false;
      fed3.Right = false;

      timeoutWithTTL(timeoutIncorrect);
    }

    last_poke = "Right";

    fed3.Right = false;
  }

}


// =========================================================
// CUSTOM TIMEOUT
// =========================================================

void timeoutWithTTL(unsigned long timeoutIncorrect) {

  unsigned long start = millis();

  while ((millis() - start) < (timeoutIncorrect * 1000)) {

    Serial.print("in timeout, ");
    Serial.println(millis() - start);

    // play white noise during timeout
    fed3.Noise(200);

    if (fed3.Left) {

      Serial.println("Left in timeout");

      fed3.BNC(50,1);

      start = millis();
    }

    if (fed3.Right) {

      Serial.println("Right in timeout");

      fed3.BNC(50,2);

      start = millis();
    }

    fed3.Left  = false;
    fed3.Right = false;
  }

  Serial.println("Done!");
}