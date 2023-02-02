# NSBrute
 NSBrute is a command line utility built using Python that allows you to gain access to the vulnerable domain by exploiting NS Takeover vulnerability. If you want to know about NS Takeover feel free to refer [this](https://medium.com/@shivsahni2/aws-ns-takeover-356d2a293bca).

## Prerequisites
* Programmatic access to AWS account
* Support for Python 3


## Executing

Clone the repo
```
git clone https://github.com/cowsaymoe/NSBrute.git
```
Install the dependencies
```
pip install -r requirements.txt
```

Once the script is cloned, and the requirements have been successfully installed, run the script using your AWS Access Key and Secret Key as shown below:
```bash
python NSBrute.py -d domain -a accessKey -s secretKey 

```
If you want to force delete the failed zones you made during testing, you can ran a command similar to this (provide a `-f` at the end):
```bash
python NSBrute.py -d domain -a accessKey -s secretKey -f
```

The script would be indefinitely creating the zones for the vulnerable domains in your AWS account until it finds a zone with a common nameserver.

<img src="https://github.com/shivsahni/RawContent/blob/master/1.png" align="middle" width="700" height="400">

Once the script creates a zone with a common nameserver you can log in to your AWS account to create the resource records for the domain to have the complete control over the domain.

<img src="https://github.com/shivsahni/RawContent/blob/master/21.png" align="middle" width="700" height="400">

If you want to terminate the script while it is still running, control + c will cause it to stop running and you will be prompted to provide `y` to force delete any stale hosted zones or literally any other character sequence to just quit immediately.
