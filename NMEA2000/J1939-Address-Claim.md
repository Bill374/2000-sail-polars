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

[^1]: In case no address has been claimed as of yet the source address could be set to 254.

[^2]: The commanded address, since it is longer than 8 bytes, it must be sent using a Fast Format Message.

## Request For Address Claimed

The Request for Address Claimed message (PGN 59904) is identical to the Request message type as described in SAE J1939/21 and chapter Parameter Group Numbers in this book.

|Parameter Group Name|Request|
|--------------------|-------|
|Parameter Group Number|59904|
|Definition|Requests a Parameter Group from a singe device or all devices in the network|
|Transmission Rate|User defined (no more than 2 or 3 times a second is recommended)|
|Data Length|3 Bytes (CAN dlc = 3)|
|Extended Data Page(R)|0|
|Data Page|0|
|PDU Format|234|
|PDU Specific|Destination Address (Global or Peer to Peer)|
|Default Priority|6|
|Data Description|Requested Parameter Group Number = PGN 90628|

The _Request for Address Claimed_ message is used to request the sending of an Address Claimed message from either a particular node in the network or from all nodes (use of global destination address = 255). The Address Claimed message (as described in the following chapter) will provide the requested information, i.e. address and NAME of the responding node(s).

The purpose of sending such a request may be for several reasons, for instance:
* A node is checking whether or not it can claim a certain address.
* A node is checking for the existence of another node (Controller Application) with a certain function.

The response to a Request for Address Claimed message can be multiple:
* Any addressed node that has already claimed an address will respond with an Address Claimed message.
* Any addressed node that was unable to claim an address will respond with a Cannot Claim Address message.
* Any addressed node that has not yet claimed an address should do so by responding with their own Address Claimed message where the source address is set to NULL (254).
A node sending the Request for Address Claimed message should respond to its own request in case the global destination address (255) was used.

## Address Claimed / Cannot Claim

The _Address Claimed_ message is used either, as the name indicates, to claim a message or to respond to a Request for Address Claimed message.

The following rules apply:
* The Address Claimed message, for the purpose of claiming an address, should always be addressed to the global address (255).
* The Address Claimed message, for the purpose of claiming an address, should be sent during the initialization of the network or as soon as the node is connecting to a running network.
* As soon as a node has successfully claimed an address, it may begin with regular network activities, i.e. sending messages or responding to messages.
* If a node (Controller Application) receives an Address Claimed message it should first compare the claimed address with its own. If the addresses are identical, the node should compare its own NAME to the NAME of the claiming node. In case its own NAME has a higher priority (lower numeric value) it will then transmit an Address Claimed message containing its NAME and address. If its own NAME is of a lower priority the node, depending on its capabilities, should either send a Cannot Claim Address message or claim another address.
* In case a node loses its address through the previously described procedure and was also in the process of sending a Transport Protocol message (see chapter Transport Protocol Functions) it should cease the transmission immediately, however, without sending a Transport Protocol Abort message. The receiver of the Transport Protocol message will detect the interruption through the corresponding timeout process.
