# CDN
As described on the project page:

“A content delivery network (CDN) is an interconnected system of computers on the Internet that provides Web content rapidly to numerous users by duplicating the content on multiple servers and directing the content to users based on proximity.” 

# Credits
This project was made for a Computer Networks' project on Instituto Superior Técnico (IST) by:

 - Daniel Machado de Castro Figueira
 - Luís Filipe Pookatham Ribeiro Gomes
 - Paulo Jorge Louseiro Gouveia

#Full Description
As described on the project page:

"The goal is to develop an application for content distribution, with several servers replicating the available contents, with the user requests being answered by the “nearest” server.

We consider one Central Server (CS), which will be the users’ contact point both to ask about the available contents as well as to make new contents available in the system. It is assumed that the user knows the URL where the central sever is available.

The interaction with the CS allows the user to get a list of the available contents and to get the identification of the Storage Server (SS) more suitable to retrieve contents from. The user application can then solicit the transfer of a given content from that SS server to a local directory.

The system also allows to upload new contents to the system, by contact with the central server, which then replicates the contents to all the available SS servers.

For the implementation, the application layer protocols operate according to the client-server paradigm, using the transport layer services made available by the socket interface, using the TCP and UDP protocols.

The central server accepts content list requests using the UDP protocol, identifies the SS server to be used for retrieving files, using the TCP protocol, by a given user. The central server accepts new contents via a TCP connection established by the user, and then replicates those contents to the SS servers using TCP connections."
