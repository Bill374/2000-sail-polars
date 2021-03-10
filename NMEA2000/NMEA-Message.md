## NEMA2000 Message Format

There are two NMEA2000 message formats; single and fast.  Single is a single CAN message frame of upto 8 bytes of data.  Fast is a longer message that spans across multiple frames for up to 223 bytes of data.

### Message header

The NMEA2000 message format is a specialization of the ISO11783 message format which is in turn a specialization of the Controller Area Network (CAN) message format.  More details of the CAN, ISO11783 and NMEA2000 standards are covered in other documents in this folder.  CAN and ISO11783 specifications are in the public domain, unfortunately the NMEA2000 standard is proprietory and full details of it have been pieced together from research and by trial and error.  Whilst what is covered here is substantially correct, there is always a chance that some part of it is not.  The software in this project is intended for use measuring sailing performance.  **It should not be used for navigation or any circumstances where vessel or personal safety depends on it.**

NMEA2000 breaks the 29 bit CAN Arbitration ID into separate fields with the following bit masks
```
PRIORITY  = 0b11100_00000000_00000000_00000000
PDU_F     = 0b00000_11111111_00000000_00000000
PDU_S     = 0b00000_00000000_11111111_00000000
SHORT_PGN = 0b00011_11111111_00000000_00000000
LONG_PGN  = 0b00011_11111111_11111111_00000000
SOURCE    = 0b00000_00000000_00000000_11111111
```
Some program group numbers (PGN) are ten bits long and some are eighteen bits long.  Short PGNs are intended for a specific destination device on the network.  Long PGNs are broadcast for all devices.  Some logic is required to determine if an arbitration ID contains a short PGN or a long PGN.
```
if PDU_F <= 239:
    PGN = SHORT_PGN
    DESTINATION = PDU_S # destination device number
else:
    PGN = LONG_PGN
    DESTINATION = 255   # Broadcast, no specific destination
```
The final important part of the CAN message header is the four bit Data Length Code (DLC).  This specifies how many bytes of data follow the header.  All valid NMEA2000 messages have the maximum eight bytes of data.

There is no field in the header that specifically identifies if a message is Fast or Single, we must *know* based on observation of each PGN.  For this project we are relying heavily on the research done in the canboat project https://github.com/canboat/canboat to identify the details of many NMEA2000 PGNs.

### Single

Single frame messages have eight bytes of data.  Most of the messages we need sailing performance analysis are single frame, they are usually broadcast to the NMEA bus multiple times per second.  Examples of important single frame messages are:
```
PGN    Message
127245 Rudder
127250 Vessel Heading
127251 Rate of Turn
127252 Heave
127257 Attitude
128259 Speed
129025 Position Rapid Update
129026 COG & SOG, Rapid Update
130306 Wind Data
```

### Fast

All frames that make up a fast message have the same header repeated.  The separate frames that make up the complete message are likely to be received in the correct order, but there is no guarantee that they will be in a continuos sequence.  It is quite likely that other messages will be received before complete sequence of frames for the whole fast message is received.

#### Fast Message Frame 1

Data Byte 1
000 - Sequence identifier (first 3 bits).
All frames that make up a fast message have the same sequence identifier.
A subsequent message of the same type will have a different sequence identifier to avoid confusion.
00000 - Frame identifier (last 5 bits).
Zero for the first frame

Data Byte 2
The number of bytes of data in the message across all frames in the sequence.

Data Bytes 3 - 8
The first six data bytes of the fast message.

#### Frames 2 and up

Data Byte 1
000 - Sequence identifier (first 3 bits).
All frames that make up a fast message have the same sequence identifier.
A subsequent message of the same type will have a different sequence identifier to avoid confusion.
00000 - Frame identifier (last 5 bits).
Increments for each frame in the message

Data Bytes 2 - 8
Seven bytes of data.
