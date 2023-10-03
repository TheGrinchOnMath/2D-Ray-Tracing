## Structure
the outermost shell (first executed part) initiates a loop that scans for inputs and mouse movement.
the mouse movement triggers reset functions that wipe the screen, set the variables for the first set of rays using 
the mouse position and number of intial reflections.

### modularity
the aim here is to minimize calculations in the physics functions by attempting to not do excessive calculations that contain roots and squares


### Physics and Render: 
the physics part hands over a numpy array to the render containing ray start and end coordinates

### Ideas and Things To Do:
- learn about how to derive complex nested functions and use that to find the function describing the tangent to any given point
- write report
- look into versioning on github (make a release 1 and 2)
- look into pathlib for MK2
- polish MK1 code, small optimizations such as error handling
