import requests,json,os
import update_uag_cert_functions
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from dotenv import load_dotenv
load_dotenv()

uag_server_list_file = './uag-servers.txt'
uag_admin_passwd = os.environ.get('UAG_ADMIN_PASSWD')
pem_file_cert = './oneline-cert.pem'
pem_file_rsa = './oneline-key-rsa.pem'
sha1_thumbprint_file = './thumbprint.txt'

f5_admin_user = os.environ.get('F5_USERNAME')
f5_admin_passwd = os.environ.get('F5_PASSWD')
f5_cert_name = 'view-ssl'
f5_iapp_json = './f5_iapps.json'

update_uag_cert_functions.update_uag_ssl_cert(pem_file_cert, pem_file_rsa, uag_server_list_file, uag_admin_passwd, update_enduser=True, update_admin=True)
update_uag_cert_functions.update_f5_ltm_ssl_cert(f5_cert_name, f5_admin_user, f5_admin_passwd, f5_iapp_json)
update_uag_cert_functions.update_uag_cert_thumbprint(sha1_thumbprint_file, uag_server_list_file, uag_admin_passwd)