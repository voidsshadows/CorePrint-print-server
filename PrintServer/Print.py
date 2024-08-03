import socket
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageChops
import PIL.ImageOps
import requests
from time import sleep
import struct

printerMACAddress = 'xx.xx.xx.xx.xx.xx'
printerWidth = 384
port = 1
api_url = 'api.url.goes.here'  # Replace with your actual API URL
last_printed_message = None  # Store the last printed message

def initializePrinter(soc):
    soc.send(b"\x1b\x40")

def getPrinterStatus(soc):
    soc.send(b"\x1e\x47\x03")
    return soc.recv(38)

def getPrinterSerialNumber(soc):
    soc.send(b"\x1D\x67\x39")
    return soc.recv(21)

def getPrinterProductInfo(soc):
    soc.send(b"\x1d\x67\x69")
    return soc.recv(16)

def sendStartPrintSequence(soc):
    soc.send(b"\x1d\x49\xf0\x19")

def sendEndPrintSequence(soc):
    soc.send(b"\x0a\x0a\x0a\x0a")

def trimImage(im):
    bg = PIL.Image.new(im.mode, im.size, (255,255,255))
    diff = PIL.ImageChops.difference(im, bg)
    diff = PIL.ImageChops.add(diff, diff, 2.0)
    bbox = diff.getbbox()
    if bbox:
        return im.crop((bbox[0], bbox[1], bbox[2], bbox[3] + 10))  # Don't cut off the end of the image

def create_text(text, font_name="Lucon.ttf", font_size=12):
    img = PIL.Image.new('RGB', (printerWidth, 5000), color=(255, 255, 255))
    font = PIL.ImageFont.truetype(font_name, font_size)
    
    d = PIL.ImageDraw.Draw(img)
    lines = []
    for line in text.splitlines():
        lines.append(get_wrapped_text(line, font, printerWidth))
    lines = "\n".join(lines)
    d.text((0,0), lines, fill=(0,0,0), font=font)
    return trimImage(img)

def get_wrapped_text(text: str, font: PIL.ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

def printImage(soc, im):
    if im.width > printerWidth:
        # Image is wider than printer resolution; scale it down proportionately
        height = int(im.height * (printerWidth / im.width))
        im = im.resize((printerWidth, height))
        
    if im.width < printerWidth:
        # Image is narrower than printer resolution; pad it out with white pixels
        padded_image = PIL.Image.new("1", (printerWidth, im.height), 1)
        padded_image.paste(im)
        im = padded_image
        
    im = im.rotate(180)  # Print it so it looks right when spewing out of the mouth
    
    # If image is not 1-bit, convert it
    if im.mode != '1':
        im = im.convert('1')
        
    # If image width is not a multiple of 8 pixels, fix that
    if im.size[0] % 8:
        im2 = PIL.Image.new('1', (im.size[0] + 8 - im.size[0] % 8, im.size[1]), 'white')
        im2.paste(im, (0, 0))
        im = im2
        
    # Invert image, via greyscale for compatibility
    im = PIL.ImageOps.invert(im.convert('L'))
    # ... and now convert back to single bit
    im = im.convert('1')

    buf = b''.join((bytearray(b'\x1d\x76\x30\x00'), 
                    struct.pack('2B', int(im.size[0] / 8 % 256), 
                                int(im.size[0] / 8 / 256)), 
                    struct.pack('2B', int(im.size[1] % 256), 
                                int(im.size[1] / 256)), 
                    im.tobytes()))
    initializePrinter(soc)
    sleep(0.5)
    sendStartPrintSequence(soc)
    sleep(0.5)
    soc.send(buf)
    sleep(0.5)
    sendEndPrintSequence(soc)
    sleep(0.5)

def fetchDataFromAPI():
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Assuming the API returns JSON data
        print("Fetched data:", data)  # Debugging line
        return data
    except requests.RequestException as e:
        print(f"API request error: {e}")
        return []

def processAndPrintData(soc, data):
    if isinstance(data, list):
        if not data:
            print("No data available.")
            return
        
        # Sort the data by timestamp (newest first)
        sorted_data = sorted(data, key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Process the most recent item
        item = sorted_data[0]
        username = item.get('username', 'Unknown User')
        message = item.get('message', 'No message')
        text = f"User: {username}\nMessage: {message}"

        global last_printed_message
        if message != last_printed_message:
            img = create_text(text, font_size=40)  # Adjust font size as needed
            printImage(soc, img)
            last_printed_message = message
            print("Printed new message:", message)  # Debugging line
        else:
            print("No new message to print.")
    else:
        print("Unexpected data format:", data)

def main():
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((printerMACAddress, port))

    print("Connecting to printer...")
    getPrinterStatus(s)
    sleep(0.5)
    getPrinterSerialNumber(s)
    sleep(0.5)
    getPrinterProductInfo(s)
    sleep(0.5)

    try:
        while True:
            data = fetchDataFromAPI()
            processAndPrintData(s, data)
            sleep(10)  # Wait 10 seconds before checking for updates
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
