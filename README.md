# This is the source code for the Travail de Maturité at the time of the report coming out

## Installation:
download all the files into a folder. put the images in a subfolder named `assets`.
Open a command-line terminal (Powershell or CMD in Windows, Terminal in MacOS, Terminal in Linux). Navigate to the folder by copying its path (context menu) and typing `cd "[copied path]"` into the terminal. 

To install the required libraries run:
`python.exe -m pip install -r requirements.txt` if you are using windows,
`pip install -r requirements.txt` for other operating systems.

## Running the Simulation:
The main.py file contains 3 options that are editable by the user. the first is a list called DIR. The strings in that list represent the subfolders that lead to the image you want to use. for example:
`["assets", "images", "image.png"]`

the MAX_REFLECTIONS and INIT_RAYS options scale with one another. INIT_RAYS sets the amount of rays that are created from the mouse positions, and MAX_REFLECTIONS sets the maximum amount of reflections. BE WARNED!!! 