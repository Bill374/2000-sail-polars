# J1939 Address Claim
Information from https://copperhilltech.com/blog/tag/Address+Claim<br>
No guarantee this is the same process as NMEA2000 but it seems likely

The SAE J1939 network management messages have the same characteristics as all other J1939 messages. These messages are:
|Message|PGN|PF|PS|SA|Data Length|Data|
|-------|---|--|--|--|-----------|----|
|Request for address claimed|59904|234|DA[^1]|3 bytes|PGN 60928|
|Address claimed|238|255|SA|8 bytes|Name|
|Cannot claim source address|238|255|254|8 bytes|Name|
|Commanded address|65240|254|216|SA|9 bytes[^2]|Name, new SA|

[^1]:In case no address has been claimed as of yet the source address could be set to 254.
[^2]:The commanded address, since it is longer than 8 bytes, it must be sent using a Fast Format Message.

## Request For Address Claimed

The Request for Address Claimed message (PGN 59904) is identical to the Request message type as described in SAE J1939/21 and chapter Parameter Group Numbers in this book.

|Parameter Group Name|Request|

The _Request for Address Claimed_ message is used to request the sending of an Address Claimed message from either a particular node in the network or from all nodes (use of global destination address = 255). The Address Claimed message (as described in the following chapter) will provide the requested information, i.e. address and NAME of the responding node(s).

The purpose of sending such a request may be for several reasons, for instance:

A node is checking whether or not it can claim a certain address.
A node is checking for the existence of another node (Controller Application) with a certain function.
The response to a Request for Address Claimed message can be multiple:

Any addressed node that has already claimed an address will respond with an Address Claimed message.
Any addressed node that was unable to claim an address will respond with a Cannot Claim Address message.
Any addressed node that has not yet claimed an address should do so by responding with their own Address Claimed message where the source address is set to NULL (254).
A node sending the Request for Address Claimed message should respond to its own request in case the global destination address (255) was used.
