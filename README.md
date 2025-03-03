# SCTP_lOADBalancer
Implementation of loab balancer which listen to sctp traffic and dispatch the tcp traffic towards the edge nodes.

solution 1:
    Deploy this sctp listner to ec2 instance and start listening on sctp connection
    The client will send sctp packet to this instance.

    Inorder to have this LoadBalancer highly available i would suggest to go for Active/Standby approach . 
    Have one more instance of this sctp loadbalancer and associate both the load balancer with Virtual ip.
    Use Keepalived to assign same virtual ip to both the instance , so that client can use the virtual ip
    to send the data.
