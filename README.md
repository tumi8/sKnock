# sKnock: Scalable Port-Knocking
Port-knocking is the concept of hiding remote services behind a firewall which allows access to the services’ listening ports only after the client has successfully authenticated to the firewall.
This helps in preventing scanners from learning what services are currently available on a host and also serves as a defense against zero-day attacks.
sKnock differs from other port-knocking solutions in that it uses x509 certificates to authenticate clients instead of using pre-shared secrets.
This helps to scale the port-knocking solution to services hosted at multiple locations as the sKnock only requires a CA certificate and periodic CRL updates to authenticate valid clients.

# Getting Started

1. Setup python2.7

   16.04 comes with python2.7 installed as default python2.7. We just need to install couple of packages required for the sKnock server to function. Let's install them one by one.
    * Install pip: apt-get install python-pip. We will install further packages using pip
    * Install python-iptables: sudo pip install python-iptables
    * We need to have python header files for the pip to compile some packages. Install them by apt-get install python-dev
    * Install m2crypto: sudo apt-get install python-m2crypto
    * Install python-cryptography; sudo apt-get install python-cryptography
    * Install six: sudo pip install six
    * Install hkdf: sudo pip install hkdf
    * Install schedule: sudo apt-get install python-schedule
2. Setup PYTHONPATH to the sKnock directory
3. Alternatively, you can also run the setup_pythonpath.sh script in the main directory. Check to ensure that PYTHONPATH environment variable is set after the script is executed.
4. Start the sKnock server: python server/knock-server.py

# Configuration
The configuration for sknock server is in server/config.ini file. The options are described below:


* `KNOCKPACKET_MIN_LENGTH`: The minimum length of the knock packet that is expected from the clients. This is used to quickly filter out all packets which are not knock packets. The value is configured to be 800. *This option is available for experimental use only and should not be changed*.
* `PORT_OPEN_DURATION_IN_SECONDS`: Number of seconds the sknock server waits before closing the port after a client has successfully portknocked for that port to be open. Any connection attempt from the client which has portknocked successfully will after these many seconds after port-knocking.
* `TIMESTAMP_THRESHOLD_IN_SECONDS`: sKnock clients put a timestamp in every knock packet they send. This is used to defend against replay attacks. Since we have to account for, latency in the Internet, unsynchronized clocks, and clock skew between the client and the server, the server accepts a knock packet as valid even if the timestamp in the packet is within the interval `[t – threshold, t + threshold]` where t is the current time at the server. This option sets the threshold.
* `CRL_UPDATE_INTERVAL_IN_MINUTES`: The interval after which the server checks for a CRL update
* `SIGNATURE_SIZE`: Expected length of signature in the knock packet. *Experimental use only.*
* `RECV_BUFFER`: The size of the buffer allocated by the server to copy knock packets. *Experimental use only.*
* `crlFile`: Path to the local CRL file. The file is updated when a new CRL is published and later fetched by the server.
* `crlUrl`: URL where the CRL is published. The server perodically downloads CRL from this URL for CRL updates.
* `serverPFXFile`: Path of the PKCS#12 file containing server private key, server certificate, and the CA certificate. PKCS#12 files typically have .pfx as extension.
    * `PFXPasswd`: The password for decrypting the serverPFXFile. A password must be given.
    * `firewallPolicy`: The firewall policy to handle all traffic which do not match to any rules configured in the firewall before sknock server started, and also to any rules which the sknock server inserts upon sucessful port-knocking requests. The valid options are: `none`, `reject`, and `drop`.  `none` causes all traffic to be allowed by default, even if it didn't match any rules; this is the default to prevent first-time users from locking themselves. Also, as a precaution sKnock server allows all connections to SSH service 22 by default irrespective of this setting. `reject` causes the firewall to respond with an ICMP port unreachable message; this lets sknock clients know whether they successfully portknocked or not. `drop` causes the packets to be dropped without telling the client why.

Since sKnock client in intended to be used as a library, it does not have any configuration file. Instead the required certificates, private key are given as arguments to the corresponding library functions.

sKnock, however contains a proof-of-concept program which uses the sKnock client library to portknock sKnock server. This program is available as a python script: `client/knock-client.py`. This program utilises `client/certificates/devclient.pfx` as the PKCS#12 bundle containing the client private key, client certificate and the CA certificate. It assumes that this bundle file is encrypted with password `portknocking`. Furthermore, it assumes that the certificate of the sKnock server is present at `client/certificates/devserver.cer`. These values are hardcoded into the code as it is only intended to be used as proof-of-concept.

# Caveats

Before testing, make sure you are running a TCP server on the ports the client certificate is allowed to access. The certificates present in the sknock repository authorize the client to access TCP ports 2000, 3000 and UDP port 8000 only.
