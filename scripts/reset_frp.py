"""Reset only the previously identified FRP partition, with verified local backup."""
import hashlib
import struct
import argparse
from pathlib import Path
import usb.core
import usb.util
from miassistant import core

parser = argparse.ArgumentParser(description='Reset FRP only for the validated Mi 9T davinci profile; destructive')
parser.add_argument('--serial', required=True, help='Expected USB serial')
parser.add_argument('--backup', type=Path, required=True, help='Fresh original partition backup from this device')
parser.add_argument('--backup-sha256', required=True, help='SHA256 recorded when creating that backup')
parser.add_argument('--execute', action='store_true', help='Explicitly enable the destructive operation')
args = parser.parse_args()
if not args.execute:
    parser.error('No operation performed: --execute is required')
backup = args.backup.read_bytes()
if len(backup) != 524288:
    raise SystemExit('Unexpected backup size')
if hashlib.sha256(backup).hexdigest() != args.backup_sha256.lower():
    raise SystemExit('Backup hash mismatch')
core.USB_TIMEOUT_MS = 5000
CLSE = int.from_bytes(b'CLSE', 'little')
d = usb.core.find(idVendor=0x18d1, idProduct=0x4e11)
if d is None:
    raise SystemExit('Phone not detected')
local = 91
remote = None
try:
    if usb.util.get_string(d, d.iSerialNumber) != args.serial:
        raise RuntimeError('Unexpected device')
    it = d.get_active_configuration()[(0, 0)]
    usb.util.claim_interface(d, it.bInterfaceNumber)
    t = {'kind': 'pyusb',
         'out_ep': usb.util.find_descriptor(it, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == 0),
         'in_ep': usb.util.find_descriptor(it, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == 128)}
    core.send_packet(t, core.ADB_CNXN, core.ADB_VERSION, core.ADB_MAX_DATA, b'host::\0')
    for _ in range(8):
        cmd, a, b, data = core.read_packet(t)
        if cmd == core.ADB_CNXN:
            break
    else:
        raise RuntimeError('No connection')
    core.send_packet(t, core.ADB_OPEN, local, 0, b'sync:\0')
    for _ in range(8):
        cmd, a, b, data = core.read_packet(t)
        if b == local and cmd == core.ADB_OKAY:
            remote = a
            break
        if b == local and cmd == CLSE:
            raise RuntimeError('Sync rejected')
    if remote is None:
        raise RuntimeError('No sync acknowledgement')
    incoming = bytearray()
    def send_sync(payload):
        core.send_packet(t, core.ADB_WRTE, local, remote, payload)
        for _ in range(16):
            cmd, a, b, data = core.read_packet(t)
            if b != local:
                continue
            if cmd == core.ADB_WRTE:
                core.send_packet(t, core.ADB_OKAY, local, a)
                incoming.extend(data)
                if incoming[:4] == b'FAIL':
                    raise RuntimeError('Recovery rejected operation: ' + bytes(incoming[8:]).decode(errors='replace'))
            elif cmd == core.ADB_OKAY:
                return
            elif cmd == CLSE:
                raise RuntimeError('Stream closed')
        raise RuntimeError('Missing write acknowledgement')
    def recv_file(path):
        incoming.clear()
        p = path.encode()
        send_sync(struct.pack('<4sI', b'RECV', len(p)) + p)
        result = bytearray()
        for _ in range(512):
            while len(incoming) >= 8:
                kind, size = struct.unpack('<4sI', incoming[:8])
                if kind == b'DONE':
                    incoming.clear()
                    return bytes(result)
                if kind != b'DATA' or size > 65536:
                    raise RuntimeError('Unexpected read response')
                if len(incoming) < 8 + size:
                    break
                result.extend(incoming[8:8+size])
                del incoming[:8+size]
                if len(result) > 1048576:
                    raise RuntimeError('Read limit exceeded')
            cmd, a, b, data = core.read_packet(t)
            if b == local and cmd == core.ADB_WRTE:
                core.send_packet(t, core.ADB_OKAY, local, a)
                incoming.extend(data)
            elif b == local and cmd == CLSE:
                raise RuntimeError('Read stream closed')
        raise RuntimeError('Read incomplete')
    identity = recv_file('/sys/class/block/sda9/uevent')
    if b'PARTNAME=frp\n' not in identity:
        raise RuntimeError('Partition identity mismatch')
    if recv_file('/dev/block/sda9') != backup:
        raise RuntimeError('Partition differs from backup; stopping')
    print('IDENTITY_AND_BACKUP_VERIFIED', flush=True)
    target = b'/dev/block/sda9,384'
    send_sync(struct.pack('<4sI', b'SEND', len(target)) + target)
    block = bytes(4096)
    for _ in range(128):
        send_sync(struct.pack('<4sI', b'DATA', len(block)) + block)
    send_sync(struct.pack('<4sI', b'DONE', 0))
    for _ in range(16):
        if len(incoming) >= 8:
            break
        cmd, a, b, data = core.read_packet(t)
        if b == local and cmd == core.ADB_WRTE:
            core.send_packet(t, core.ADB_OKAY, local, a)
            incoming.extend(data)
    if bytes(incoming[:8]) != struct.pack('<4sI', b'OKAY', 0):
        raise RuntimeError('No successful sync completion: ' + repr(bytes(incoming[:80])))
    print('WRITE_ACCEPTED', flush=True)
    check = recv_file('/dev/block/sda9')
    if check != bytes(524288):
        raise RuntimeError('Verification mismatch; do not reboot')
    print('VERIFIED_ZEROED_524288_BYTES', flush=True)
    core.send_packet(t, CLSE, local, remote)
finally:
    usb.util.dispose_resources(d)
