import sqlserverport
# test data
server_name = "192.168.1.45"
instance_name = "SQLEXPRESS"

try:
    result = r"Instance {0}\{1} is listening on port {2}.".format(
        server_name,
        instance_name,
        sqlserverport.lookup(server_name, instance_name),
    )
except sqlserverport.BrowserError as err:
    result = err.message
except sqlserverport.NoTcpError as err:
    result = err.message

serverspec = '{0},{1}'.format(
    server_name,
    sqlserverport.lookup(server_name, instance_name))

print(serverspec)

print(result)