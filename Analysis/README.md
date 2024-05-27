
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
```json
{
    "WIB_PWR" : {},
    "WIB_LINK" : {},
    "FE_PWRON" : {},
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