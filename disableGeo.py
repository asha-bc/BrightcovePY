#!/usr/bin/env python3
import sys
from mackee import main, GetCMS, eprint
from threading import Lock

counter_lock = Lock()
videos_processed = 0

def show_progress(progress):
	sys.stderr.write(f'\r{progress} processed...\r')
	sys.stderr.flush()

#===========================================
# callback to disable Geo restrictions
#===========================================
def disable_geo(video):
	global videos_processed
	# does video have Geo restrictions?
	if video.get('geo'):
		# get the video ID
		video_id = str(video.get('id'))
		# create the JSON body
		json_body = ('{ "geo": null }')
		# make the PATCH call
		r = GetCMS().UpdateVideo(video_id=video_id, json_body=json_body)
		# check if all went well
		if r.status_code not in [200,202]:
			eprint(f'Error code {r.status_code} disabling Geo for video ID {video_id}:')
			eprint(r.text)

	with counter_lock:
		videos_processed += 1

	if videos_processed%100==0:
		show_progress(videos_processed)

#===========================================
# only run code if it's not imported
#===========================================
if __name__ == '__main__':
	main(disable_geo)
	show_progress(videos_processed)
