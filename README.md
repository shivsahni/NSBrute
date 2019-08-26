# NSBrute
 NSBrute is a command line utility built using Python that allows you to gain access to the vulnerable doamin by exploiting NS Takeover vulnerability. If you want to know about NS Takeover feel free to refer [this](https://medium.com/@shivsahni2/aws-ns-takeover-356d2a293bca).

## Prerequisites
* Programmatic access to AWS account
* Support for Python 2.7


## Executing

Clone the repo
```
git clone https://github.com/shivsahni/NSBrute.git
```
Once the script is cloned, run the script using your AWS Access Key and Secret Key as shown below:
```
python NSTakeover.py -d domain -a accessKey -s secretKey

```
The script would be indefinitely creating the zones for the vulnerable domains in your AWS account until it finds a zone with a common nameserver.

<img src="https://github.com/shivsahni/RawContent/blob/master/1.png" width="400" height="400">

Once the script creates a zone with a common nameserver you can log in to your AWS account to create the resource records for the domain to have the complete control over the domain.

<img src="https://github.com/shivsahni/RawContent/blob/master/21.png" width="400" height="400">