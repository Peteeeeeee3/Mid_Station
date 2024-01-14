For EC branch on GitHub, refer to: EC-main (
Main was left untouched since last submission

In this project we came across an issue in our testing that left correctly scaling the RTMP Server not feasible.
The issue is that even with each RTMP server on a separate thread in a map, since they are serving the same location,
0.0.0.0:1935, we needed to implement dynamic port allocation. To give each RTMP server a specific service, which would
all require a "rolling" ingress. By this we mean an ingress that paths a user specific RTMP URL for the user to their
specific RTMP Server service. This ingress would link each port to a path, for example, 'mid-station.com/user1', which
would link to an internal port such as 8080.

That said. We were able to get two RTMP servers running at the same time, it just so happened we were of course on two
separate pods. Issues did occur, we streamed from OBS to each others RTMP Server. This makes sense as each server is
aimlessly accepting data entry from port 1935, there is no targeting for the correct RTMP server, which can be done
explained above.

Additionally, we aimed and have left code that indicates an attempt at having a HTML5 live preview of the live stream.
The issue with this unfortunately was that we could only get the MP4 file format to actually display video, but this
format does not support real-time encoding, or at least didn't work. And formats like flv, mkv, ogg and webm didn't
work at all.

--------------------------------------------------------------------------------------------------------------------------
UI Capabilities
--------------------------------------------------------------------------------------------------------------------------

On the stream page the user can create new stream settings and stream targets. The user can click the pen icon next to these
to edit them, which also provides an option for the user to delete them. Individual stream settings can be toggled on or off,
but only one can be activated at a time. Users can also hide or expand the targets of a stream setting. A user can press the
"Go Live" button to start an RTMP server (restreaming the incoming video feed to the defined stream targets) or the "Go Offline"
button to shut down the RTMP server and hence stop streaming. Lastly the user is also able to log out of their account taking
them back to the home page.
