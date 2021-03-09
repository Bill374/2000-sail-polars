## NEMA2000 Message Format
There are two NMEA2000 message formats; single and fast.  Single is a single CAN message frame of upto 8 bytes of data.
Fast is a longer message that spans across multiple frames for up to 223 bytes of data.

### Message header

### Single

### Fast
All frames that make up a fast message have the same header repeated

#### Frame 1

Byte 1
000 - Sequence identifier (first 3 bits).
All frames that make up a fast message have the same sequence identifier.
A subsequent message of the same type will have a different sequence identifier to avoid confusion.
00000 - Frame identifier (last 5 bits).
Zero for the first frame

Byte 2
The number of bytes of data in the message across all frames in the sequence.

Bytes 3 - 8
Data

#### Frames 2 and up

Byte 1
000 - Sequence identifier (first 3 bits).
All frames that make up a fast message have the same sequence identifier.
A subsequent message of the same type will have a different sequence identifier to avoid confusion.
00000 - Frame identifier (last 5 bits).
Increments for each frame in the message
