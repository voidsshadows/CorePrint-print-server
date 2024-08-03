# CorePrint-print-server
This project leverages the core print CTP500WH, a Python script, an HTML site, and a Cloudflare Worker to print messages posted on a website.
# Core Print CTP500WH Messaging System

## Description

This project allows users to submit quotes through a web interface, which are then stored and can be printed using a Core Print CTP500WH printer. The system consists of a web frontend for submitting and viewing quotes, a Cloudflare Worker for handling API requests and data storage, and a Python script for printing the quotes via Bluetooth.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
  - [Cloudflare Worker](#cloudflare-worker)
  - [Web Interface](#web-interface)
  - [Python Script](#python-script)
- [Usage](#usage)
- [To-Do](#to-do)

## Features

- **Submit Quotes**: Users can submit quotes via a web form.
- **View Quotes**: Submitted quotes are displayed on the web interface.
- **Print Quotes**: A Python script fetches the latest quotes and prints them using a Bluetooth printer.
- **CORS Support**: The Cloudflare Worker handles CORS requests to allow cross-origin requests.

## Requirements

- Cloudflare account
- Core Print CTP500WH printer with Bluetooth
- Python 3.x
- Required Python libraries: `Pillow`, `requests`
- Bluetooth-enabled device for running the Python script
- Web server to host the HTML page
- the python script requires the luton.ttf file

## Setup

### Cloudflare Worker

1. **Create a Cloudflare Worker**:
   - Go to your Cloudflare dashboard and create a new Worker.
   - Copy and paste the `worker.js` code into the Cloudflare Worker script editor.

2. **Deploy the Worker**:
   - Deploy the Worker and note the endpoint URL (e.g., `https://your-worker-url.workers.dev/`).

### Web Interface

1. **Create an HTML file**:
   - Copy the HTML code provided and save it as `index.html`.

2. **Host the HTML file**:
   - Upload the `index.html` file to your web server or a static site hosting service.

### Python Script

1. **Install required Python libraries**:
   ```bash
   pip install Pillow requests
2.**Copy the Python script code and save it as `print_quotes.py`.**
3. **Update the `printerMACAddress` with the MAC address of your Core Print CTP500WH printer.**
4. **Update the `api_url` with the endpoint URL of your Cloudflare Worker.**


## To-Do

- **Improve Error Handling**: Enhance the Python script to handle Bluetooth and network errors more gracefully.
- **Notification System**: Notify users when their quotes are printed.
- **Enhanced Sanitization**: Improve input sanitization to prevent more sophisticated injection attacks.
- **Rate Limiting**: Implement rate limiting to prevent spam submissions.
   **Out of Paper**: Let users know when the printer is out of paper.
