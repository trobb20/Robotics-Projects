# OnshapeSpikePrime
This repo provides python scripts that allow you to create digital twins for monitoring and controlling a LEGO Spike Prime robot connected to the USB port.

## Assembly Setup
Right now, only revolute mates and slider mates are supported by these scripts. In your Onshape assembly, you should rename the mates to either "Control" or "Monitor" to use them as inputs for motion on the Spike Prime, or monitors for the sensors on the Spike Prime.

<img width="205" alt="Screen Shot 2021-09-13 at 9 19 02 AM" src="https://user-images.githubusercontent.com/54808875/133090701-4d009f52-1db0-4f9e-94dc-f824d0e94912.png">

## Setup

Start by cloning this repo into your Documents folder by running the following command in terminal or command prompt:
```
git clone https://github.com/PTC-Education/OnshapeSpikePrime
```
After cloning this repo, go into the new folder that was created by typing
```
cd OnshapeSpikePrime
```
In this folder, you must import some python libraries by running the following commands. **note** you may need to do "pip3 install ..." depending on how your python version is configured.
```
pip3 install -r requirements.txt
```

## Configuration

You will need to generate API Keys from the [Onshape Developer Portal](https://dev-portal.onshape.com/). You can add these to a file named "apikeys.py" that lives in the OnshapeSpikePrime folder or one level higher (these API keys have been deleted and are only there for demo purposes). **Make sure you never share these with anybody!!**
```
base = 'https://ptc.onshape.com' ## only need to specify base if different than "https://cad.onshape.com"
access = 'Z97asb1257FkEwzp3EmCpa'
secret = 'nHwN3q7asdvg4aryFC9rxYyo9U4o415WokYa8VOQ9YfUh4Zx'
```

## Using Python Scripts for USB Connection to Spike Prime Hub

Run the file from terminal or command prompt by typing the following commands
```
python OnshapeSpikeControl.py
python OnshapeSpikeMonitor.py
```
**Note**: depending on how python is configured or if you're using windows, you may have to replace the "python" command with "python3" or "py"

If you see an output saying "resource busy", unplug and replug the usb cord, then run the script again. If the script does not execute the first time, try again.

You can stop execution of the script at any time by pressing Control-C.
