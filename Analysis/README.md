
 ### Quality Control of the LArASIC for DUNE using the DAT board
---------------

**Files in this folder :**<br/>

* ***utils.py :*** utility functions and class needed for all other parts of the analysis <br/>
* ***spymemory_decode_copy.py :*** copy of spymemory_decode to decode the raw data<br/>
* ***Init_checkout.py :*** file having the class INIT_CHECK <br/>
* ***qc_selection.json :*** input file where the selection criteria of the chips should be saved/entered 
qc_selection :
```
{
    "QC_INIT_CHK": {
        "FE_PWRON": {
            "V" : [Vmin, Vmax]
        }
        "ASICDAC_CALI_CHK": {
            "pedestal": [pedmin, pedmax],
            "rms": [rmsmin, rmsmax],
            "pulseAmp": [pulseAmpmin, pulseAmpmax]
        },
        "DIRECT_PLS_CHK" : {
            "pedestal": [pedmin, pedmax],
            "rms": [rmsmin, rmsmax],
            "pulseAmp": [pulseAmpmin, pulseAmpmax]
        },
        "isPosPeak": true/false
    }
}
```
* ***QC_PWR.py :*** file having the class QC_PWR for the extraction of informations from raw data of the power measurement
---
This README file will include all informations about the scripts like: <br/>
* input data <br/>
* output format <br/>
* how to run the scripts?<br/>

##### Output format for each chipID :
* **QC_INIT_CHK**
```json
{
    "logs": {
        "date": "",
        "testsite": "",
        "env": "",
        "note": "",
        "DAT_SN": "",
        "WIB_slot": ""
    },
    "WIB_PWR" : {},
    "WIB_LINK" : {},
    "FE_PWRON" : {
        "V":{
            "data": {
                "VDDA": val,
                "VDDO": val,
                "VDDP": val
            },
            "unit": "V"
        },
        "I":{
            "data": {
                "VDDA": val,
                "VDDO": val,
                "VDDP": val
            },
            "unit": "mA"
        },
        "P":{
            "data": {
                "VDDA": val,
                "VDDO": val,
                "VDDP": val
            },
            "unit": "mW"
        }
    },
    "ADC_PWRON" : {},
    "CD_PWRON": {},
    "ASICDAC_CALI_CHK" : {
        "CFG_info": [],
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": []
    },
    ...,
    "DIRECT_PLS_CHK" : {
        "CFG_info": [],
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": []
    },
    ....
}
```

* **QC_PWR**
    * **Configuration**:
        * SNC0: 900mV
        * SNC1: 200mV
        * SDD0: SEDC output buffer DISABLED
        * SDD1: SEDC output buffer ENABLED
        * SDF0: SE output buffer DISABLED
        * SDF1: SE output buffer ENABLED
        **The configuration SDD1 + SDF1 is not used.**
    * **Data format:**
```json
{
    "logs": {
        "date": "",
        "testsite": "",
        "env": "",
        "note": "",
        "DAT_SN": "",
        "WIB_slot": ""
    },
    "config0": {
        "CFG_info" : {},
        "V": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "I": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val            
        },
        "P": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "unitPWR":
        {
            "V": "V",
            "I": "mA",
            "P": "mW"
        },
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": []
    },
    "config1": {...},
    ...
}
```
**config0, config1, etc.** are of the form `200mV_sedcBufOFF_seBuffON` where `200mV` is the value of `SNC`, `sedcBufOFF` is the value of `SDD`, and `seBufON` is the value of `SDF`

* **QC_FE_MON :**
```json
{
    "BL": {
        "200mV" : [],
        "900mV" : []
    },
    "VBGR_Temp": {
        "unit" : "",
        "VBGR" : 0,
        "MON_Temper" : 0,
        "MON_VBGR" : 0
    },
    "DAC_meas": {
        "config0": {
            "DAC" : [],
            "data": [],
            "GAIN" : 0,
            "unit_of_gain": "mV/bit",
            "INL" : 0
        },
        "config1": {
            "DAC" : [],
            "data": [],
            "GAIN" : 0,
            "unit_of_gain": "mV/bit",
            "INL" : 0
        },
        ...
    }
}
```
* **QC_CHKRES**
```json
{
    "logs":{
        "date": "",
        "testsite": "",
        "env": "",
        "note": "",
        "DAT_SN": "",
        "WIB_slot": ""
    },
    "cfg0":{
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": [],
        "CFG_Info":{
            "param_chk": "",
            "SDD": "",
            "SDF": "",
            "SLKH": "",
            "SLK": "",
            "SNC": "",
            "STS": "",
            "ST": "",
            "SGP": "",
            "SG": ""
        }
    },
    "cfg1":{
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": [],
        "CFG_Info":{
            "param_chk": "",
            "SDD": "",
            "SDF": "",
            "SLKH": "",
            "SLK": "",
            "SNC": "",
            "STS": "",
            "ST": "",
            "SGP": "",
            "SG": ""
        }
    },
    ...
}
```
`cfg0`, `cfg1`, etc. are of the form `CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG11`

* **QC_PWR_CYCLE**
```json
{
    "logs":{
        "date": "",
        "testsite": "",
        "env": "",
        "note": "",
        "WIB_slot": ""
    },
    "PwrCycle_0":{
        "V": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "I": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "P": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": []
    },
    "PwrCycle_1":{
        "V": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "I": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "P": {
            "VDDA": val,
            "VDDO": val,
            "VDDP": val
        },
        "pedestal": [],
        "rms": [],
        "pospeak": [],
        "negpeak": []
    },
    ...
}
```

* **QC_RMS**
```json
{
    "logs":{
        "date": "",
        "testsite": "",
        "env": "",
        "note": "",
        "DAT_SN": "",
        "WIB_slot": ""
    },
    "config0": {
        "CFG": {
            "SDD": "",
            "SDF": "",
            "SLKH": "",
            "SLK": "",
            "SNC": "",
            "STS": "",
            "ST": "",
            "SGP": "",
            "SG": ""
        },
        "pedestal": [],
        "rms": []
    },
    "config1": {
        "CFG": {
            "SDD": "",
            "SDF": "",
            "SLKH": "",
            "SLK": "",
            "SNC": "",
            "STS": "",
            "ST": "",
            "SGP": "",
            "SG": ""
        },
        "pedestal": [],
        "rms": []
    },
    ...
}
```

* **QC_CALIBRATION**: the class used to decode the raw data is **QC_CALI**
    * **ASICDAC_CALI :** the output of this script is the amplitude of the positive peak = (max - pedestal).
    ```json
    {
        "logs":{
            "date": "",
            "testsite": "",
            "env": "",
            "note": "",
            "DAT_SN": "",
            "WIB_slot": ""
        }
        ,
        "SNC0": {
            "CH0": [
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1": [
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ]
        },
        "SNC1": {
            "CH0": [
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1": [
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": 0,
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ]
        }
    }
    ```
    * **DATDAC_CALI :** decodes the DATDAC and DIRECT pulse calibration data
    ```json
    {
        "logs":{
            "date": "",
            "testsite": "",
            "env": "",
            "note": "",
            "DAT_SN": "",
            "WIB_slot": ""
        },
        "SNC0": {
            "CH0" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            ...
        },
        "SNC1": {
            "CH0" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            ...
        }
    }
    ```

    * **DIRECT_CALI :** decodes the DATDAC and DIRECT pulse calibration data
    ```json
    {
        "logs":{
            "date": "",
            "testsite": "",
            "env": "",
            "note": "",
            "DAT_SN": "",
            "WIB_slot": ""
        },
        "SNC0": {
            "CH0" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            ...
        },
        "SNC1": {
            "CH0" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            "CH1" : [
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                {
                    "DAC": "",
                    "pedestal": 0,
                    "std": 0,
                    "posAmp": 0,
                    "negAmp": 0
                },
                ...
            ],
            ...
        }
    }
    ```
* **QC_Cap_Meas**
    ```json
    {
        "CALI": {
            "FECHN00" : {
                "0600mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                },
                "1400mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                }
            },
            "FECHN01" : {
                "0600mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                },
                "1400mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                }
            },
            ...
        },
        "INPUT": {
            "FECHN00" : {
                "1400mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                },
                "1550mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                }
            },
            "FECHN00" : {
                "1400mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                },
                "1550mV": {
                    "ppeak": 0,
                    "npeak": 0,
                    "pedestal": 0,
                    "rms": 0
                }
            },
            ...
        }
    }
    ```

* **QC_DLY_RUN :**
```json
{
    "logs" : {
        "date" : "",
        "testsite" : "",
        "env" : "",
        "note" : "",
        "DAT_SN" : "",
        "WIB_slot" : ""
    },
    "Phase0_Period1000": {
        "phase"  : 0,
        "period" : 1000,
        "CH0" : {
            "pospeak" : 0,
            "negpeak" : 0,
            "pedestal" : 0,
            "rms" : 0
        },
        "CH1" : {
            "pospeak" : 0,
            "negpeak" : 0,
            "pedestal" : 0,
            "rms" : 0
        },
        ...
    },
    "Phase1_Period1000": {
        "phase"  : 1,
        "period" : 1000,
        "CH0" : {
            "pospeak" : 0,
            "negpeak" : 0,
            "pedestal" : 0,
            "rms" : 0
        },
        "CH1" : {
            "pospeak" : 0,
            "negpeak" : 0,
            "pedestal" : 0,
            "rms" : 0
        },
        ...
    },
    ...
}
```