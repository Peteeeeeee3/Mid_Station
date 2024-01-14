In this project we came across an issue in our testing that left correctly scaling the RTMP Server not feasible.
The issue is that even with each RTMP server on a separate thread in a map, since they are serving the same location,
0.0.0.0:1935, no two RTMP Servers could be on the same pod, or we needed to implement dynamic port allocation.
To have each RTMP server on a separate pod would require having the server be a separate docker image and deployment,
as well as having a specific service. This would all require a "rolling" ingress. By this I mean an ingress that paths
a user specific RTMP URL for the user to their specific RTMP Server service. Using dynamic port allocation will allow for
many RTMP severs on a single pod, and would be near the same as explained, but the service and ingress path would have
the generated port. The only issue with this implementation is the firewall. Needing to also dynamically create and delete
firewall rules for each port used.

Additionally, we aimed and have left code that indicates an attempt at having a HTML5 live preview of the live stream.
The issue with this unfortunately was that we could only get the MP4 file format to actually display video, but this
format does not support real-time encoding, or at least didn't work. And formats like flv, mkv, ogg and webm didn't
work at all.
