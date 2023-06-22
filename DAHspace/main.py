# code written by team DAHspace, from Guimaraes, Portugal
from pathlib import Path
from logzero import logger, logfile
from sense_hat import SenseHat
from picamera import PiCamera
from orbit import ISS
from time import sleep
from datetime import datetime, timedelta
from skyfield.api import load
import csv


# Set up Sense Hat
sh = SenseHat()
sh.colour.integration_cycles = 64


def create_csv_file(data_file):
    """Create a new CSV file and add the header row"""
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Counter","Date/time", "Location", "mag_x", "mag_y", "mag_z", "yaw", "pitch",
                  "roll", "gyro_x", "gyro_y", "gyro_z")
        writer.writerow(header)

def add_csv_data(data_file, data):
    """Add a row of data to the data_file CSV"""
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
    

def get_sh_data():
    sh_data = []

    mag = sh.get_compass_raw()
    mag_x = round(mag.get('x'), 3)
    mag_y = round(mag.get('y'), 3)
    mag_z = round(mag.get('z'), 3)
        
    orientation = sh.get_orientation()
    yaw = round(orientation.get('yaw'), 3)
    pitch = round(orientation.get('pitch'), 3)
    roll = round(orientation.get('roll'), 3)
        
    gyro = sh.get_gyroscope_raw()
    gyro_x =round(gyro.get('x'), 3)
    gyro_y =round(gyro.get('y'), 3)
    gyro_z =round(gyro.get('z'), 3)
    
    return (mag_x, mag_y, mag_z, yaw, pitch, roll, gyro_x, gyro_y, gyro_z)

def capture(camera, image):
    # Capture the image
    camera.capture(image)



#--------------Main----------------------------------
if __name__ == "__main__":
    
    # Set up camera
    cam = PiCamera()
    cam.resolution = (4056, 3040)
    
    base_folder = Path(__file__).parent.resolve()

    # Set a logfile name
    logfile(base_folder/"DAHspace.log")
    logger.info(f"Mission Status: Initiated")
    
    # Initialise the CSV file
    data_file = base_folder/"data.csv"
    create_csv_file(data_file)

    # Initialise the counter
    counter = 1
    
    # Initialise the photo counter
    photo_counter = 1
    
    # Record the start and current time
    start_time = datetime.now()
    now_time = datetime.now()
    # Run a loop for (almost) three hours

    
while (now_time < start_time + timedelta(minutes=175)):
    try:        
        for _ in range(10):
            # Get coordinates of location on Earth below the ISS
            # Obtain the current time `t`
            t = load.timescale().now()
            # Compute where the ISS is at time `t`
            position = ISS.at(t)
            # Compute the coordinates of the Earth location directly beneath the ISS
            location = position.subpoint()
            
            # get magnetic field, orientation and gyroscope data
            mag_x, mag_y, mag_z, yaw, pitch, roll, gyro_x, gyro_y, gyro_z = get_sh_data()
            
            # Save the data to the file
            data = (
                counter,
                datetime.now(),
                location,
                mag_x,
                mag_y,
                mag_z,
                yaw,
                pitch,
                roll,
                gyro_x,
                gyro_y,
                gyro_z
            )
            add_csv_data(data_file, data)
            counter += 1
            sleep(3)
        
        # Determine brightness to evaluate whether it's day or night
        brightness = sh.colour.clear_raw
	
        if brightness > 50:
            # Capture image if it's day
            image_file = f"{base_folder}/photo_{photo_counter:03d}.jpg"
            capture(cam, image_file)
                
            # Log event
            logger.info(f"iteration {photo_counter}")
            photo_counter += 1
        else:
            print("Nighttime")

        # Update the current time
        now_time = datetime.now()
        
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')
        

logger.info(f"Mission Status: Complete") 
