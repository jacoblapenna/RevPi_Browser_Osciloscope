# RevPi_Browser_App
Basic browser app to plot data from first channel of AIO connected to a Revolution Pi.

## Install
1. SSH to the Revolution Pi.
2. Install Redis on the Revolution Pi: https://redis.io/docs/getting-started/installation/install-redis-on-linux/
3. Clone this repo to the Revolution Pi. AIO channel 1 is setup with default name `InputValue_1` in PiCtory.
4. From within project directory on Revolution Pi:<br/>
    `$ python -m venv .env`<br/>
    `$ source .env/bin/activate`<br/>
    `$ pip install -r requirements.text`<br/>

## Run
1. Check that redis-server is running: `$ systemctl status redis-server.service`

    a. If the redis service is not running, use `$ sudo systemctl restart redis-server.service` or, simply `$ redis-server`.
2. `$ python app.py`

    a. Program automatically obtains IP of device it's running on (printed in debug message).
3. In a browser, navigate to the Revolution Pi's IP (stated in the terminal from step 2) via port 8080.

## Usage
The application is a basic oscilloscope for the first channel of an AIO module with symbolic name of "inputValue_1". To modify the time per division, change the `max_len` variable on line 6 of static/js/main.mjs based on the following equation:<br/>
<br/>
max_len = sr * 5 * SPD </br>
<br/>
Where sr is the sample rate, 5 is the number of divisions on the oscilloscope, and SPD is the desired seconds per division. The scope width, in seconds, is then 5*SPD.


The static/js/Deque.mjs impliments a custom JavaScript data structure that mimics the python deque data structure (i.e. O(1) FIFO array). This structure also is responsible for drawing the oscilloscope and has methods for automatic marking of local extrema of the data. This is depicted in the following image showing a 0.1 Hz sine wave with local extrema shown at the red dots. This extrema detection is provided on the front end by the static/js/ExtremaDetector.mjs object, and its ability to correctly find extrema is based on the input threshold and signal noise. If extrema detection is desired on the back end instead, simply deploy similar code in a python class.


This is a very basic oscilloscope application, and is not maintained regularly. It merely serves as an example to start similar, more complex projects with the Revolution Pi.
