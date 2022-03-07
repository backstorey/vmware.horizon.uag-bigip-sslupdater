# Automated SSL cert replacement for UAGs

To take some of the grunt work out of replacing SSL certificates on Horizon UAG Servers and Horizon F5 iApps, this shell + python script automation will take care of this.  It assumes you're running this on a mac which has openssl and python installed.

# Setup Instructions

- Clone the repo and install python requirements `pip install -r requirements.txt`
- Set the shell script to executable - `chmod +x ./replace-uag-certs.sh`
- Update the `.env` file with the passwords / creds for UAGs and BIG-IP devices.
- Review and edit the list of UAGs FQDNs you want to replace certificates on in the file `uag-servers.txt` i.e.:
```
myuag1.domain.com
myuag2.domain.com
myuag3.domain.com
```
- Review and edit the JSON data file of BIG-IP devices and associated iApps on each BIG-IP - `f5_apps.json`  i.e.:
```{
    "big_ip_devices": [ 
        {
            "hostname": "big-ip69.mydomain.com",
            "iapps": [
                "horizon-iapp-internal",
                "horizon-iapp-external"
            ]
        },        
        {
            "hostname": "big-ip79.mydomain.com",
            "iapps": [
                "horizon-iapp-internal",
                "horizon-iapp-external"
            ]
        },        
        {
            "hostname": "big-ip89.mydomain.com",
            "iapps": [
                "horizon-iapp-internal",
                "horizon-iapp-external"
            ]
        }
    ]
}
```

- Obtain a copy of the new cert in PFX format and place in the same directory as the repo.
- Upload the PFX file to each BIG-IP device you'd like to update iApps on, and note the name used in BIG-IP's certificate management section.  [Maybe one day we'll automate this step too](#TODO)
- Run the shell script, passing the PFX file as an argument `./replace-uag-certs.sh ./new-pfx.pfx`
- When prompted, enter the PFX export passsword, used to secure the cert bundle.

# Script Actions
The script will perform the following steps:

- Extract the certificate chain from the PFX and write to `cert.pem`
- Extract the private key from the PFX and write to `key.pem`
- Convert the private key to RSA format and write to `key-rsa.pem`
- Extract the SHA1 thumbprint and write to a file `thumbprint.txt` (prep for setting the UAG thumbprint on the UAGs, after setting F5 iApp endpoints).
- Convert both the certificate chain and the private key to a single string, adding newline characters, naming them `oneline-cert.pem` and `oneline-key.pem` respectively (prep for passing the certificate within a JSON payload)
- Updates the SSL certficate for both the admin interface and the end user / internet facing interface
- Updates iApps on each BIG-IP with new certificate
- Updates UAGs with SHA1 certificate thumbprint.
- Cleans up PEM and thumbprint files created during automation run.

# TODO

- Improve error handling
- Automate upload of PFX into BIG-IP's certificate management store.