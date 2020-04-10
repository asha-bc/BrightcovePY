#!/usr/bin/env python3
import mackee

#===========================================
# callback to enable Offline Playback
#===========================================
def enableOffline(video):
	# does video have DRM?
	isOfflineEnabled = video.get('offline_enabled')
	if(isOfflineEnabled is not None and isOfflineEnabled==False):
		# get the video ID
		videoID = video['id']
		# create the JSON body
		jsonBody = ('{ "offline_enabled": true }')
		# make the PATCH call
		r = mackee.cms.UpdateVideo(videoID=videoID, jsonBody=jsonBody)
		# check if all went well
		if(r.status_code in [200,202]):
			print(('Enabled Offline Playback for video ID {videoid} with status {status}.').format(videoid=videoID, status=r.status_code))
		# otherwise report the error
		else:
			print(('Error code {error} enabling Offline Playback for video ID {videoid}:').format(error=r.status_code, videoid=videoID))
			print(r.text)

#===========================================
# only run code if it's not imported
#===========================================
if __name__ == '__main__':
	mackee.main(enableOffline)
