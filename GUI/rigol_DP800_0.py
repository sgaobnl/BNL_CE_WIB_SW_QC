from dcps import RigolDP800
from os import environ

# Retrieve the VISA resource string from environment variable or set a default
resource = environ.get('DP800_USB', 'USB0::0x1AB1::0x0E11::DP8C184550811::INSTR')

# Initialize the Rigol DP800 power supply
rigol = RigolDP800(resource)

# Open the connection to the device
rigol.open()

# Set the channel to 1
rigol.channel = 1

# Query and display the voltage and current settings for channel 1
print(f'Ch. {rigol.channel} Settings: {rigol.queryVoltage():6.4f} V  {rigol.queryCurrent():6.4f} A')

# Enable the output for channel 1
rigol.outputOn()

# Measure and display the actual voltage and current
print(f'Measured Voltage: {rigol.measureVoltage():6.4f} V')
print(f'Measured Current: {rigol.measureCurrent():6.4f} A')

# Set the output voltage to 5.0V
rigol.setVoltage(5.0)

# Turn off the output for channel 1
rigol.outputOff()

# Close the connection to the device
rigol.close()
