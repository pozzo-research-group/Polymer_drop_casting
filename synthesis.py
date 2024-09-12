#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
os.system("systemctl stop opentrons-robot-server")


# In[3]:


import opentrons.execute
import json 
import pandas as pd 

protocol = opentrons.execute.get_protocol_api('2.18')
CUSTOM_LABWARE_PATH = "./labware/"
protocol.home()


# In[4]:


protocol.set_rail_lights(True)


# In[5]:


# load all the labware modules
with open(CUSTOM_LABWARE_PATH+'20mlscintillation_12_wellplate_18000ul.json') as labware_file:
    stock_def = json.load(labware_file)
    stocks = protocol.load_labware_from_definition(stock_def, location=1)

synthesized_plate = protocol.load_labware(
    load_name="corning_96_wellplate_360ul_flat",
    location=2)

dropcast_plate = protocol.load_labware(
    load_name="corning_96_wellplate_360ul_flat",
    location=3)

with open(CUSTOM_LABWARE_PATH+'agilent_6_reservoir_47000ul.json') as labware_file:
    reservoir_def = json.load(labware_file)
    reservoir = protocol.load_labware_from_definition(reservoir_def, location=5)
    
tiprack = protocol.load_labware(
    load_name="opentrons_96_tiprack_300ul",
    location=7)
pipette = protocol.load_instrument(
    instrument_name="p300_single_gen2",
    mount="right",
    tip_racks=[tiprack]
    )


# In[7]:


synthesized_plate.set_offset(x=0.00, y=0.70, z=0.00)
dropcast_plate.set_offset(x=0.00, y=0.70, z=0.00)
tiprack.set_offset(x=0.50, y=1.00, z=0.00)
reservoir.set_offset(x=0.00, y=0.00, z=0.00)


# In[8]:


TIPS = ["A1", "A2", "A3", "A4", "A5"]
def dispense_stock_into_well(stock_id, volume, well):
    print("Dispensing Stock %d of %.2f volume into well %s..."%(stock_id+1, volume, well.well_name), end="\r", flush=True)

    pipette.pick_up_tip(tiprack[TIPS[stock_id]])       
    pipette.aspirate(volume, stocks[TIPS[stock_id]])
    pipette.dispense(volume, well)
    pipette.mix(2, 100, reservoir["A3"],rate=2)
    pipette.blow_out(reservoir["A5"].top())
    pipette.drop_tip(tiprack[TIPS[stock_id]])
    
    return 
    


# In[10]:


# import pandas as pd
# samples = pd.read_csv("samples.csv").to_numpy()
import numpy as np 

samples = np.array([[100, 200], [15, 10]])
for i in range(samples.shape[0]):
    dispense_stock_into_well(0, samples[i,0], synthesized_plate.wells()[i])
    dispense_stock_into_well(1, samples[i,1], synthesized_plate.wells()[i])


# In[15]:


def dropcast(volume, source_well, destination_well):
    print("Dropcasting %.2f volume of %s into well %s..."%(volume, 
                                                           source_well.well_name, 
                                                           destination_well.well_name), end="\r", flush=True)

    if not pipette.has_tip:
        pipette.pick_up_tip(tiprack["A5"])       
    pipette.aspirate(volume, source_well)
    pipette.dispense(volume, destination_well)
    pipette.mix(2, 100, reservoir["A3"],rate=2)
    pipette.blow_out(reservoir["A5"].top())
    


# In[16]:


for i in range(samples.shape[0]):
    dropcast(100, synthesized_plate.wells()[i], dropcast_plate.wells()[i])


# In[17]:


pipette.drop_tip(tiprack["A5"])


# In[19]:


protocol.home()
protocol.set_rail_lights(False)


# In[ ]:




