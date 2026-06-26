import math
import time

def calculate_distance(point1, point2):
    """
    Calculates the Euclidean distance between two points in 2D space.
    
    Parameters:
    - point1 (tuple/list): Coordinates of the first point (x, y).
    - point2 (tuple/list): Coordinates of the second point (x, y).
    
    Returns:
    - float: The straight-line distance between point1 and point2.
    """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    
    # Euclidean distance formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
    # math.hypot(dx, dy) computes math.sqrt(dx*dx + dy*dy) efficiently.
    return math.hypot(x2 - x1, y2 - y1)


def map_value(value, in_min, in_max, out_min, out_max):
    """
    Maps (scales) a value from one range to another.
    
    Example: Mapping a distance of 30 to 180 pixels to a volume range of 0 to 100.
    
    Parameters:
    - value (float): The current value to scale.
    - in_min (float): The minimum of the input range.
    - in_max (float): The maximum of the input range.
    - out_min (float): The minimum of the output range.
    - out_max (float): The maximum of the output range.
    
    Returns:
    - float: The scaled value clamped between out_min and out_max.
    """
    # 1. Clamp the input value so it doesn't exceed in_min or in_max
    clamped_value = max(in_min, min(value, in_max))
    
    # 2. Perform linear interpolation (mapping math)
    input_range = in_max - in_min
    output_range = out_max - out_min
    
    # Avoid division by zero if input range is invalid
    if input_range == 0:
        return out_min
        
    scaled_value = out_min + ((clamped_value - in_min) / input_range) * output_range
    return scaled_value


class FPSCounter:
    """
    A class to calculate and keep track of Frames Per Second (FPS).
    FPS is crucial in computer vision to measure the performance of our system.
    """
    def __init__(self):
        # Store the current time when the counter is initialized
        self.prev_time = time.time()

    def get_fps(self):
        """
        Calculates FPS based on the time difference since the last call.
        
        Returns:
        - float: The calculated FPS rounded to 1 decimal place.
        """
        current_time = time.time()
        elapsed_time = current_time - self.prev_time
        
        # Prevent division by zero if frames are processed faster than precision limit
        if elapsed_time <= 0:
            return 0.0
            
        # FPS = Number of frames (1) divided by time taken (seconds)
        fps = 1.0 / elapsed_time
        
        # Update prev_time for the next frame
        self.prev_time = current_time
        
        return round(fps, 1)
