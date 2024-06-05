
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

1. **QC_INIT_CHK:**
##### Input data:
* QC_INIT_CHK.bin
* qc_selection.json
##### Output format for each chipID :
* **QC_INIT_CHK**
```json
{
    "WIB_PWR" : {},
    "WIB_LINK" : {},
    "FE_PWRON" : {
        "V": {"data": [VDDA_V, VDDO_V, VDDP_V], "qc_result": [], "unit": "V" ,"link_to_img": ""},
        "I": {"data": [VDDA_I, VDDO_I, VDDP_I], "qc_result": [], "unit": "mA", "link_to_img": ""},
        "P": {"data": [VDDA_P, VDDO_P, VDDP_P], "qc_result": [], "unit": "mW", "link_to_img": ""},
    },
    "ADC_PWRON" : {},
    "ASICDAC_CALI_CHK" : {
                            "pedestal": {"data": [], "result_qc": [], "link_to_img":""},
                            "rms" : {"data": [], "result_qc": [], "link_to_img": ""},
                            "pulseResponse": {
                                    "pospeak": {"data": [], "result_qc": [], "link_to_img": ""},
                                    "negpeak": {"data": [], "result_qc": [], "link_to_img": ""}
                            }
    },
    "DIRECT_PLS_CHK" : {
                        "pedestal": {"data": [], "result_qc": [], "link_to_img":""},
                        "rms" : {"data": [], "result_qc": [], "link_to_img": ""},
                        "pulseResponse": {
                                "pospeak": {"data": [], "result_qc": [], "link_to_img": ""},
                                "negpeak": {"data": [], "result_qc": [], "link_to_img": ""}
                        }
    }
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
    "V": {"200mV": {"config0": val, "config1": val, "config2": val},
          "900mV": {"config0": val, "config1": val, "config2": val},
          "unit": "V",
          //"result_qc": "",
          "link_to_img": ""
         },
    "I": {"200mV": {"config0": val, "config1": val, "config2": val},
          "900mV": {"config0": val, "config1": val, "config2": val},
          "unit": "mA",
          //"result_qc": "",
          "link_to_img": ""
         },
    "P": {"200mV": {"config0": val, "config1": val, "config2": val},
          "900mV": {"config0": val, "config1": val, "config2": val},
          "unit": "P",
          //"result_qc": "",
          "link_to_img": ""
         }
}
```