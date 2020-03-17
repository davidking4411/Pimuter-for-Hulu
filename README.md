# Pimuter-for-Hulu
Reads the "Ad" symbol on Hulu ads and mutes the Roku TV using its API when present.
Could potentially work for hulu streaming sticks or boxes depending on how the volume control is set up with the tv.
This was designed to run continuously so it checks every two minutes to see if Hulu is the active app and turns the image processing on or off accordingly to save power and heat that can shorten the pi's lifespan. A live view of the crop region and resulting mask is displayed for tuning the behavior. I'd suggest commenting these out to minimize the processing required of the pi when not tuning.

Just change the IP address of your Roku device. You can adjust the size of the crop region but for now this is done separately from the rectangle selection. Will combine these in the future into one parameter.
