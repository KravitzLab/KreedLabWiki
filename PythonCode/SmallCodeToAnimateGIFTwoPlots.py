#%%
import matplotlib.pyplot as plt
from PIL import Image

# Step 2: Create an animated GIF from the saved plots
images = []
filenames = [r"C:\Users\lexkr\Downloads\Pellet.png", r"C:\Users\lexkr\Downloads\Poke.png"]

for filename in filenames:
    images.append(Image.open(filename))

# Make the GIF alternate between the two plots, looping back and forth
images[0].save(r"C:\Users\lexkr\Downloads\animated_plot.gif",
               save_all=True,
               append_images=[images[1], images[0]],  # Reverse order for back-and-forth effect
               duration=1000,  # 3000 ms = 3 seconds
               loop=0)  # Infinite loop
