#!/usr/bin/env python3
import mackee
import csv
import time
from threading import Lock

videosProcessed = 0
counter_lock = Lock()
data_lock = Lock()

row_list = [ ['video_id','master_size','renditions_size'] ]

def showProgress(progress):
	mackee.sys.stderr.write(f'\r{progress} processed...\r')
	mackee.sys.stderr.flush()

#===========================================
# function to get size of master
#===========================================
def getMasterStorage(video):
	masterSize = 0
	response = None

	if(video.get('has_digital_master')):
		try:
			response = mackee.cms.GetDigitalMasterInfo(videoID=video.get('id'))
		except Exception as e:
			response = None
			masterSize = -1

		if(response and response.status_code == 200):
			masterSize = response.json().get('size')

	return masterSize

#===========================================
# function to get size of all renditions
#===========================================
def getRenditionSizes(video):
	renSize = 0
	response = None

	try:
		delivery_type = video.get('delivery_type')
		if(delivery_type == 'static_origin'):
			response = mackee.cms.GetRenditionList(videoID=video.get('id'))
		elif(delivery_type == 'dynamic_origin'):
			response = mackee.cms.GetDynamicRenditions(videoID=video.get('id'))
	except Exception as e:
		response = None
		renSize = -1

	if(response and response.status_code in mackee.cms.success_responses):
		renditions = response.json()
		for rendition in renditions:
			renSize += rendition.get('size')

	return renSize

#===========================================
# callback getting storage sizes
#===========================================
def findStorageSize(video):
	global videosProcessed
	row = []

	shared = video.get('sharing')
	if(shared and shared.get('by_external_acct')):
		row = [ video.get('id'), 0, 0 ]
	else:
		row = [ video.get('id'), getMasterStorage(video), getRenditionSizes(video) ]

	# add a new row to the CSV data
	with data_lock:
		row_list.append(row)

	# increase processed videos counter
	with counter_lock:
		videosProcessed += 1

	# display counter every 100 videos
	if(videosProcessed%100==0):
		showProgress(videosProcessed)

#===========================================
# only run code if it's not imported
#===========================================
if __name__ == '__main__':
	s = time.perf_counter()
	mackee.main(findStorageSize)
	showProgress(videosProcessed)

	#write list to file
	try:
		with open('report.csv' if not mackee.args.o else mackee.args.o, 'w', newline='', encoding='utf-8') as file:
			try:
				writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=',')
				writer.writerows(row_list)
			except Exception as e:
				mackee.eprint(f'\nError writing CSV data to file: {e}')
	except Exception as e:
		mackee.eprint(f'\nError creating outputfile: {e}')

	elapsed = time.perf_counter() - s
	mackee.eprint(f"\n{__file__} executed in {elapsed:0.2f} seconds.")	
