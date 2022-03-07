def update_uag_ssl_cert(pem_cert_file, pem_privkey_file, uag_servers_file, uag_admin_passwd, update_enduser, update_admin):
    """
    Update SSL certificates on a UAG's END_USER and/or ADMIN interfaces.

    The function requires the paths to the following files:
    - certficate and private key as PEMs
    - a text file list of UAG FQDNs
    - admin password for the UAGs (function assumes all servers will use the same creds for all UAGs in the uag text file)

    """
    import requests,json

    # Load in Certificates
    with open(pem_cert_file) as certfile:
        cert = certfile.read()

    with open(pem_privkey_file) as privkeyfile:
        privkey = privkeyfile.read()

    headers = { "Content-Type": 'application/json' }

    body = {
        "privateKeyPem": privkey,
        "certChainPem": cert
    }

    # Tidy up line escape characters that get thrown in by default json.dumps() behaviuor
    json_body = json.dumps(body).replace('\\\\','\\')

    # Read in uag server list from text file, and strip out newlines using split method.
    with open(uag_servers_file) as uags:
        uaglist = uags.read().split('\n')

    for uag_server in uaglist:

        print(f"Replacing SSL cert on UAG {uag_server} ...")

        uag_url_set_user_ssl_admin = f"https://{uag_server}:9443/rest/v1/config/certs/ssl/admin"
        uag_url_set_user_ssl_enduser = f"https://{uag_server}:9443/rest/v1/config/certs/ssl/end_user"

        if update_enduser:
            try:
                response_put_enduser = requests.put(f"{uag_url_set_user_ssl_enduser}",verify=False,data=json_body,headers=headers,auth=('admin', uag_admin_passwd))
                if response_put_enduser.ok == True:
                    print(f"SSL Cert was updated on the END_USER endpoint on uag {uag_server}")
                else:
                    print(f"There was a problem updating the cert on the END_USER endpoint on {uag_server}")
            except:
                print(f"There was a problem setting certs on the END USER interface on {uag_server}")
        
        if update_admin:
            try:
                response_put_admin = requests.put(f"{uag_url_set_user_ssl_admin}",verify=False,data=json_body,headers=headers,auth=('admin', uag_admin_passwd))    
                if response_put_admin.ok == True:
                    print(f"SSL Cert was updated on the ADMIN endpoint on uag {uag_server}")
                else:
                    print(f"There was a problem updating the cert on the ADMIN endpoint on {uag_server}")
            except:
                print(f"There was a problem setting certs on the ADMIN interface on {uag_server}")


def update_uag_cert_thumbprint(thumbprint_file,uag_servers_file,uag_admin_passwd):
    """
    Updates a UAG's cert thumbprint.
    Assumes the cert thumbprint file was generated using the SHA1 fingerprinting algo - ie:
        openssl x509 -noout -fingerprint -sha1 -inform pem -in ./cert.pem > ./thumbprint.txt
    """
    import requests,json

    with open(thumbprint_file) as tp:
        thumbprint = tp.read().replace('SHA1 Fingerprint','sha1')

    headers = { "Content-Type": 'application/json' }

    # Read in uag server list from text file, and strip out newlines using split method.
    with open(uag_servers_file) as uags:
        uaglist = uags.read().split('\n')

    for uag_server in uaglist:

        print(f"Setting Cert Thumbprint on UAG {uag_server} ...")

        uag_url_horizon_edgeservice_get = f"https://{uag_server}:9443/rest/v1/config/edgeservice"
        uag_url_horizon_edgeservice_set = f"https://{uag_server}:9443/rest/v1/config/edgeservice/view"

        try:
            response_get_edgeservice = requests.get(f"{uag_url_horizon_edgeservice_get}",verify=False,headers=headers,auth=('admin', uag_admin_passwd))
            edgeservice_dict = response_get_edgeservice.json()['edgeServiceSettingsList'][0]
            edgeservice_dict['proxyDestinationUrlThumbprints'] = thumbprint
            json_body = json.dumps(edgeservice_dict).replace('\\\\','\\')   
        except:
            print(f"There was a problem getting the endpoint details...")

        try:
            response_put = requests.put(f"{uag_url_horizon_edgeservice_set}",verify=False,data=json_body,headers=headers,auth=('admin', uag_admin_passwd))
            if response_put.ok == True:
                print(f"Successfully set SSL thumbprint on {uag_server}")
            else:
                print(f"There was a problem setting the SSL thumbprint on {uag_server}")
        except:
            print(f"There was a problem setting SSL thumbprint on {uag_server}")


def update_f5_ltm_ssl_cert(cert_name,f5_username,f5_passwd,iapp_json_file):
    """
    Updates the certificate set on an F5 iApp.
    This function assumes you have already uploaded the certficate and key to the BIG-IP device already.
    """
    import requests,json

    headers = { "Content-Type": 'application/json' }

    with open(iapp_json_file) as iapps_file:
        iapps = json.load(iapps_file)

    for big_ip_device in iapps['big_ip_devices']:
        big_ip_hostname = big_ip_device['hostname']
        big_ip_rest_endpoint_url = f'https://{big_ip_hostname}'
        for iapp in big_ip_device['iapps']:
            big_ip_rest_endpoint_url_iapp = f'{big_ip_rest_endpoint_url}/mgmt/tm/cloud/services/iapp/{iapp}'
            
            try:
                get = requests.get(big_ip_rest_endpoint_url_iapp,auth=(f5_username,f5_passwd),headers=headers,verify=False)
                payload = get.json()
                payload['vars']['iapp_ssl_cert'] = cert_name
                payload['vars']['iapp_ssl_key'] = cert_name
                payload['vars']['ssl__cert'] = f"/Common/{cert_name}"
                payload['vars']['ssl__key'] = f"/Common/{cert_name}"
                json_body = json.dumps(payload)
            except:
                print(f"There was a problem getting iApp details from the iApp {iapp}")
            
            try:
                print(f"Setting iApp {iapp} on BIG-IP host {big_ip_hostname} to use certificate {cert_name}")
                post = requests.put(big_ip_rest_endpoint_url_iapp,auth=(f5_username,f5_passwd),data=json_body,headers=headers,verify=False)
            except:
                print(f"There was a problem updating the iApp {iapp} on BIG-IP device {big_ip_hostname}")