import time
import datetime
import math
import json
import urllib2

from neopixel import *

NEOSEGMENT_COUNT = 8

# LED strip configuration:
LED_COUNT      = 7 * NEOSEGMENT_COUNT  # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP 	   = 0x00081000

_digitMapping = ( 
	[1,1,1,0,1,1,1],
	[0,0,1,0,0,0,1],
	[1,1,0,1,0,1,1],
	[0,1,1,1,0,1,1],
	[0,0,1,1,1,0,1],
	[0,1,1,1,1,1,0],
	[1,1,1,1,1,1,0],
	[0,0,1,0,0,1,1],
	[1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1]
)

_letterMapping = {
	'a' : [1,0,1,1,1,1,1],
	'u' : [1,1,1,0,1,0,1],
	's' : [0,1,1,1,1,1,0],
	'd' : [1,1,1,4,0,0,1]
}

rArray = [0] * LED_COUNT
gArray = [0] * LED_COUNT
bArray = [0] * LED_COUNT

bitcoin_price_URL = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
	strip.begin()

	def wheel(pos):
		"""Generate rainbow colors across 0-255 positions."""
		if pos < 85:
			return Color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Color(0, pos * 3, 255 - pos * 3)

	def clearAll():
		for i in range(0, strip.numPixels(), 1):
			strip.setPixelColor(i, Color(0, 0, 0))
		strip.show()

	def setSegment(index, segment, rColor, bColor, gColor):
		segm = 7 * index + segment
		rArray[segm] = rColor
		gArray[segm] = bColor
		bArray[segm] = gColor
		strip.setPixelColor(segm, Color(rArray[segm], gArray[segm], bArray[segm]))
		strip.show()

	def setSegment(index, segment, color):
		segm = 7 * index + segment
		rArray[segm] = color >> 16
		gArray[segm] = color >> 8
		bArray[segm] = color
		strip.setPixelColor(segm, Color(rArray[segm], gArray[segm], bArray[segm]))
		strip.show()

	def setDigit(index, number, color):
		if (number < 0) or (number > 9):
			return
		for segm in range(7 * index, 7 * index + 7, 1):
			rArray[segm] = 0
			gArray[segm] = 0
			bArray[segm] = 0

			if (_digitMapping[number][segm % 7]):
				rArray[segm] = color >> 16
				gArray[segm] = color >> 8
				bArray[segm] = color
		    
			strip.setPixelColor(segm, Color(rArray[segm], gArray[segm], bArray[segm]))
		 
		strip.show()


	def clearDigit(index):
		for segm in range(7 * index, 7 * index + 7, 1):
			rArray[segm] = 0
			gArray[segm] = 0
			bArray[segm] = 0
		    
			strip.setPixelColor(segm, Color(rArray[segm], gArray[segm], bArray[segm]))
		 
		strip.show()


	def writeNumber(start_index, max_length, number, color, justify = "right"):
		num_str = str(number)
		num_length = len(num_str)
		padding_length = max_length - num_length

		if (num_length > max_length or (start_index + max_length) > NEOSEGMENT_COUNT ):
			print 'Cannot Display Digits here'
			return

		pos = (padding_length) if (justify == "right") else 0

		for character_index, character in enumerate(num_str):
			digit = int(character)
			if (digit < 0 or digit > 9):
				return
			setDigit(start_index + character_index + pos, digit, color)

		if (padding_length > 0):
			for padding_index in xrange(padding_length):
				if (justify == "right"):
					clearDigit(start_index + padding_index)
				else:
					clearDigit(start_index + num_length + padding_index)

	def setLetter(index, letter, color):
		if (letter not in _letterMapping):
			return
		for segm in range(7 * index, 7 * index + 7, 1):
			rArray[segm] = 0
			gArray[segm] = 0
			bArray[segm] = 0

			if (_letterMapping[letter][segm % 7]):
				rArray[segm] = color >> 16
				gArray[segm] = color >> 8
				bArray[segm] = color
		    
			strip.setPixelColor(segm, Color(rArray[segm], gArray[segm], bArray[segm]))
		 
		strip.show()

	def retrieve_btc_price():
		btc_price = 0
		try:
			response = json.loads(urllib2.urlopen(bitcoin_price_URL).read())
			btc_price = int(round(float(response['data']['amount'])))
		except Exception as e:
			print ("Unable to connect to Bitcoin Price URL")
		return btc_price

	def display_bitcoin_price(current_bitcoin_price, letter_color, number_color):
		writeNumber(0, 5, current_bitcoin_price, number_color)	
		setLetter(5, 'u', letter_color)
		setLetter(6, 's', letter_color)
		setLetter(7, 'd', letter_color)
	
	def flash_bitcoin_price(old_bitcoin_price, current_bitcoin_price):
		if (old_bitcoin_price == current_bitcoin_price):
			display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
		else:
			if (current_bitcoin_price > old_bitcoin_price):
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0x00FF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0x00FF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0x00FF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)
			else:
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFF0000 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFF0000 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFF0000 )
				time.sleep(0.2)
				display_bitcoin_price(current_bitcoin_price, 0xAF00CE, 0xFFFF00 )
				time.sleep(0.2)

	clearAll()
	current_bitcoin_price = 0

	while True:
		old_bitcoin_price = current_bitcoin_price
		current_bitcoin_price = retrieve_btc_price()

		flash_bitcoin_price(old_bitcoin_price, current_bitcoin_price)

		time.sleep(10)
	
