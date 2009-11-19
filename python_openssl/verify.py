## Eperio data verification script
## Nov. 13, 2009

import csv, os, string, time, sys

#################################################
#
# openCSV -- IMPORT CSV FILE
#
def openCSV(fileName):
	data = []
	fileContents = open(fileName, 'r')
	for i in fileContents:
		data.append(i.strip().split(","))
	return data


###################################################################
#
# verifyFailure -- OUTPUT ERROR MESSAGE AND TERMINATE
#
def verifyFailed(errorMsg):
	print errorMsg
	sys.exit()

###################################################################
#
# verifyCommitment -- VERIFY COMMITMENT AND EXTRACT CSV COLUMN
#
def verifyCommitment(instance):
	os.system("openssl enc -d -aes-128-cbc -a -in " + instance[0] + ".enc -out " + instance[0] + ".csv -pass pass:" + instance[1])
	data = openCSV(instance[0].strip('"') + ".csv")
	col = []
	# Checks columns repeated three times as per the commitment scheme
	for i in data: 
		if i[0] != i[1] or i[0] != i[2]:
			verifyFailed("Invalid Commitment")
	return [i[0] for i in data]

	
################################################
#
# getMarks -- EXRACT CSV MARKS COLUMN
#
def getMarks(instance):
	marks = openCSV("./Marks/M"+ instance[0][2:4] + ".csv")
	return [i[0] for i in marks]


#Open common files
assReceipts = sorted(openCSV('./AssertedReceipts.csv'))
assTally = sorted(openCSV('./AssertedTally.csv'))
pwds = openCSV('./ChallengeKeys.csv')
linkageList = openCSV('./LinkageList.csv')

#Verify each committed instance
for i, instance in enumerate(pwds):
	merged=[]
	data = verifyCommitment(instance)
	marks = getMarks(instance)

	#Merge receipts {or} tally column with marks column 
	for index in range(len(data)): 
		merged.append([data[index], marks[index]])
	
	if instance[0][5] == "U" :
		#Verify print-audited ballots
		for ballot, linkage in enumerate(linkageList):	
			if linkageList[ballot][0] != merged[int(linkageList[ballot][i+2])-1][0] or merged[int(linkageList[ballot][i+2])-1][1] != "-1" :
				verifyFailed("Linkage list FAIL: Receipt instance #%d does not does not match linkage list" % (i+1))				
		#Verify decypted receipt instance is isomorphic to the asserted receipt list
		if assReceipts == sorted(merged):
			print "Instance %d verified" % (i+1)			
		else:
			verifyFailed("Verification FAIL: Receipt instance #%d does not match asserted receipt list!" % (i+1))
	elif instance[0][5] == "S":
		#Verify print-audited ballots		
		for ballot, linkage in enumerate(linkageList):	
			if linkageList[ballot][1] != merged[int(linkageList[ballot][i+2])-1][0] or merged[int(linkageList[ballot][i+2])-1][1] != "-1" :
				verifyFailed("Linkage list FAIL: Tally instance #%d does not does not match linkage list" % (i+1))
		#Verify decypted tally instance is isomorphic to the asserted tally list
		if assTally == sorted(merged):
			print "Instance %d verified" % (i+1)
		else:
			verifyFailed("Verification FAIL: Tally instance #%s does not match asserted tally list!" % (i+1))
	else:
		verifyFailed("Instance filename is incorrectly formatted")

