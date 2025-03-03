# SCTP_lOADBalancer
Implementation of loab balancer which listen to sctp traffic and dispatch the tcp traffic towards the edge nodes.

solution 1:
    Deploy this sctp listner to ec2 instance and start listening on sctp connection
    The client will send sctp packet to this instance.

High Avaialability for loadbalancer:
    Inorder to have this LoadBalancer highly available i would suggest to go for Active/Standby approach . 
    Have one more instance of this sctp loadbalancer and associate both the load balancer with Virtual ip.
    Use Keepalived to assign same virtual ip to both the instance , so that client can use the virtual ip
    to send the data. Install KeepAlive_master.conf on Active node and Install KeepAlive_slave.conf on standby node.
    start and enable keepalived on each node using below:
    systemctl start keepalived
    systemctl enable keepalivd.

    Node which hold the VIP will only receive the SCTP packet.

solution 2:
we can also use open source load balancer such as HAproxy to handle sctp connection and configure it to listen to
SCTP connection and forward it to edge node in TCP format. we can deploy this HA proxy in EC2 instance and install 
keepAlived to make it highly available.
