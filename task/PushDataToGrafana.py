import socket
import pickle
import struct
import time

# IP and port of Grafana VM
GRAFANA_DESTINATION = ('10.102.22.29', 2004)
# Destination of the data in database
PATH = 'device.talice.debug.test.'
# Activate print in console
DEBUG = False
# Sampling rate
DELAY = 1  # seconds


def SendGraphitePayload(destination, header, payload):
    sock = socket.socket()
    try:
        sock.connect(destination)
        sock.sendall(header)
        sock.sendall(payload)
    except:
        print "Could not reach graphite database at:", destination
        return False

    return True


def GetMemoryUsage(pid):
    # FIXME: Run command to find memory usage
    return 3 * pid


def GetProcessLoad(pid):
    # FIXME: Run command to find process load
    return 10 * pid


def GetNetworkTrafic():
    # FIXME: Run command to calculate network trafic
    return 50


def NetworkMonitoring():
    # Get current time
    now = int(time.time())

    # Get the data
    net = (PATH + 'network', (now, GetNetworkTrafic()))

    # Format for Graphite database
    payload = pickle.dumps(net, protocol=2)
    header = struct.pack("!L", len(payload))

    # Send it
    if SendGraphitePayload(GRAFANA_DESTINATION, header, payload):
        if DEBUG:
            print 'Sent: ', net


def ProcessMonitoring(pid):
    # Get current time
    now = int(time.time())

    # Get the data
    # FIXME: Add process name in front of .mem, .cpu
    mem = (PATH + pid[1] + '.mem', (now, GetMemoryUsage(pid[0])))
    cpu = (PATH + pid[1] + '.cpu', (now, GetProcessLoad(pid[0])))

    # Format for Graphite database
    payload = pickle.dumps([mem, cpu], protocol=2)
    header = struct.pack("!L", len(payload))

    # Send it
    if SendGraphitePayload(GRAFANA_DESTINATION, header, payload):
        if DEBUG:
            print 'Sent: ', [mem, cpu]


def main():
    # FIXME: Find pid of process to monitor
    pid_list = [(1, 'bmxs'), (2, 'modbus')]

    while True:
        # Check and send process monitoring
        for pid in pid_list:
            ProcessMonitoring(pid)

        # Check network
        NetworkMonitoring()

        # Wait some time
        time.sleep(DELAY)


if __name__ == '__main__':
    main()
