# Set up RSA key on the local PC (only need to do it ONCE when first time to setup)
PC side: Open a terminal. click “Enter” 3 times, you can find private key id_rsa and public key id_rsa.pub under  $/.ssh
```
ssh-keygen.exe 

```

WIB side (ssh to WIB):
```
mkdir ~/.ssh/
Copy id_rsa.pub to WIB, save it at ~/.ssh/
mv ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys

```

You now can log in WIB without typing password. If it doesn’t, reboot the WIB and try again. 


# 2. LArASIC QC based on DAT board (manual operation)
```
python3 top_femb_powering.py <on/off> <on/off> <on/off> <on/off>
```
The four arguments correspond to the four slots 
#### 3. FEMBs quick checkout



