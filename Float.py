import board
import busio
import adafruit_lps35hw
import RPi.GPIO as GPIO #type: ignore
import asyncio
import time 
import serial
import spidev #type: ignore
from lib_nrf24 import NRF24 #type: ignore


P1 = 1 #gpio pin 1 (adjustable depending on what pin is choses)
P2 = 2 #gpio pin 2 (adjustable depending on what pin is choses)
P3 = 3 #gpio pin 3 (adjustable depending on what pin is choses)
P4 = 4 #gpio pin 4 (adjustable depending on what pin is choses)
mx = 1 #corresponds to data collection
lc = 50 #corresponds to data collection
pipes = [0xA1, 0xA1, 0xA1, 0xA1, 0x01]
radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)  # CE pin on GPIO 17
radio.setChannel(0x76)  # Set the channel (0-127)
radio.setPayloadSize(32)  # Set payload size to 32 bytes
radio.setDataRate(NRF24.BR_1MBPS)  # Set the data rate
radio.openWritingPipe(0xF0F0F0F0E1)  # Set the writing pipe address
radio.startListening()

THE_list = [] #list into which data is appended
DepthOffset = 0 #depth (calculation)
Upper_Limit = 100 #depth (beginning)height (editable/adjustable)
Downward_Limit = 300 #depth (end)height (editable/adjustable)

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_lps35hw.LPS35HW(i2c)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(P1, GPIO.OUT) #a change here will correspond to P1-P4 cariabes
GPIO.setup(P2, GPIO.OUT)
GPIO.setup(P3, GPIO.OUT)
GPIO.setup(P4, GPIO.OUT)


async def main(): #main code (change if functions needed/ adjust order in main function)
    try:
        await Initial_Serial_Message()
        asyncio.create_task(data_collection())
        await handle_switch(1)
        await handle_switch(5)
        await handle_switch(2)
        await handle_switch(5)
        await transmitter_module()
        asyncio.create_task(data_collection())
        await handle_switch(3)
        await handle_switch(5)
        await handle_switch(4)
        await handle_switch(5)
        await transmitter_module()

    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up...")
    finally:
        GPIO.cleanup() 
        print("Congrats, program is now complete")



async def Initial_Serial_Message():  # Initial message for team confirmation
    radio.stopListening()  # Ensure the NRF24 is in transmission mode
    message = "Crubotics"
    data = message.encode('utf-8')  # Convert the string to bytes

    while len(data) > 32:
        # Split the data if it exceeds 32 bytes
        chunk = data[:32]
        radio.write(chunk)  # Send the chunk
        data = data[32:]  # Remove the sent chunk

    if data:
        radio.write(data)  # Send any remaining part of the message

    radio.startListening()  # Resume listening mode after sending
    print("Crubotics")

def transmitter_module(): #transmitter transmission
    radio.stopListening()  # Stop listening before sending

    for item in THE_list:
        data = item.encode('utf-8')  # Convert string to bytes
        while len(data) > 32:
            # Split the data if it exceeds 32 bytes
            chunk = data[:32]
            radio.write(chunk)  # Send the chunk
            data = data[32:]  # Remove the sent chunk

        # Send any remaining data that is less than or equal to 32 bytes
        if data:
            radio.write(data)

    THE_list.clear()  # This will reset the list for the next batch of data

    radio.startListening()  # Start listening again if necessary
    print("Data transmitted.")


    radio.startListening()  # Start listening again if necessary
    print("Data transmitted.")


async def data_collection():  #awaic asyncio.sleep is a non interrupting timer as a regular sleep from time module will not work with a loop like this unless one to use python threading
    while True: #infinite loop 
        pressure = sensor.pressure #pressure data
        temperature = sensor.temperature  #temp data
        depth = int(pressure / 1.0038 - DepthOffset)
        ft = depth * 0.328084
        print(f"Pressure: {pressure:.2f} hPa, Temperature: {temperature:.2f} °C, Depth:{ft}")
        while lc < mx: # while 1 < 50 will this loop be true
            THE_list.append(f"Pressure: {pressure:.2f} hPa, Temperature: {temperature:.2f} °C\n, Depth:{ft}")
            await asyncio.sleep(5)
            lc += 1  #adds 1+ to lc after a loop ends)


async def handle_switch(S1): #additionally if statements would work in this case/creating seperate functions as well but with match and case statement is better for editing in addition to be way less risky compare to if/else statements
     match S1:               #match and case statements essentially is a matching function it will match to a certain pattern of sorts (with this method is far more organized)
        case 1:
            GPIO.output(P1, GPIO.HIGH)
            GPIO.output(P2, GPIO.HIGH)
            GPIO.output(P3, GPIO.LOW)
            GPIO.output(P4, GPIO.LOW)
            print("First element matched!")
            await asyncio.sleep(100)  

        case 5:
            GPIO.output(P1, GPIO.LOW)
            GPIO.output(P2, GPIO.LOW)
            GPIO.output(P3, GPIO.LOW)
            GPIO.output(P4, GPIO.LOW)
            print("Switch 5 deactivated!")
            await asyncio.sleep(500)  
        case 2:
            GPIO.output(P1, GPIO.LOW)
            GPIO.output(P2, GPIO.LOW)
            GPIO.output(P3, GPIO.HIGH)
            GPIO.output(P4, GPIO.HIGH)
            print("Second element matched!")
            await asyncio.sleep(100) 

        case 3:
            GPIO.output(P1, GPIO.HIGH)
            GPIO.output(P2, GPIO.HIGH)
            GPIO.output(P3, GPIO.LOW)
            GPIO.output(P4, GPIO.LOW)
            print("Third element matched!")
            await asyncio.sleep(100) 

        case 4:
            GPIO.output(P1, GPIO.HIGH)
            GPIO.output(P2, GPIO.HIGH)
            GPIO.output(P3, GPIO.LOW)
            GPIO.output(P4, GPIO.LOW)
            print("Fourth element matched!")
            await asyncio.sleep(100)  
        
        case 6:
            GPIO.output(P1, GPIO.LOW)
            GPIO.output(P2, GPIO.LOW)
            GPIO.output(P3, GPIO.LOW)
            GPIO.output(P4, GPIO.LOW)
            await asyncio.sleep(100) 

        case _:
            print("No specific match found")

if __name__ == "__main__":
    asyncio.run(main()) #main function stated at end 

