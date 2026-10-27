import struct
import hashlib
import sys
import os
import argparse
from pathlib import Path
import usb.core
import usb.util
from miassistant import core

# Read-only phone diagnostics; backups are written only to the local PC.
core.USB_TIMEOUT_MS = 3000
allowed_paths = ('/prop.default', '/proc/self/status', '/sys/fs/selinux/enforce', '/sys/class/block/sda9/uevent', '/proc/partitions', '/dev/block/sda9')
parser = argparse.ArgumentParser(description='Read-only diagnostics for the validated Mi 9T recovery profile')
parser.add_argument('path', nargs='?', default='/prop.default', choices=allowed_paths)
parser.add_argument('--backup', type=Path, help='New local file required when reading the FRP partition')
parser.add_argument('--serial', help='Expected USB serial; required for a partition backup')
args = parser.parse_args()
requested_path = args.path
if requested_path == '/dev/block/sda9' and (args.backup is None or not args.serial):
    parser.error('Partition backup requires --backup and --serial')
if requested_path not in allowed_paths:
    raise SystemExit('Path not allowed by this diagnostic')
CLSE = int.from_bytes(b'CLSE', 'little')
d = usb.core.find(idVendor=0x18d1, idProduct=0x4e11)
if d is None:
    raise SystemExit('DEVICE_NOT_FOUND')
try:
    if args.serial and usb.util.get_string(d, d.iSerialNumber) != args.serial:
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
            print('CONNECTED', data.decode(errors='replace'), flush=True)
            break
    else:
        raise RuntimeError('No CNXN response')
    local = 83
    remote = None
    core.send_packet(t, core.ADB_OPEN, local, 0, b'sync:\0')
    for _ in range(8):
        cmd, a, b, data = core.read_packet(t)
        if b == local and cmd == CLSE:
            raise RuntimeError('Recovery rejected sync service')
        if b == local and cmd == core.ADB_OKAY:
            remote = a
            break
    if remote is None:
        raise RuntimeError('No sync acknowledgement')
    print('SYNC_OPEN', flush=True)
    path = requested_path.encode()
    core.send_packet(t, core.ADB_WRTE, local, remote, struct.pack('<4sI', b'RECV', len(path)) + path)
    pending = b''
    contents = b''
    done = False
    for _ in range(512):
        cmd, a, b, data = core.read_packet(t)
        if b != local:
            continue
        if cmd == CLSE:
            raise RuntimeError('Stream closed before file completed')
        if cmd != core.ADB_WRTE:
            continue
        core.send_packet(t, core.ADB_OKAY, local, a)
        pending += data
        while len(pending) >= 8:
            kind, size = struct.unpack('<4sI', pending[:8])
            if kind == b'DONE':
                done = True
                break
            if kind not in (b'DATA', b'FAIL') or size > 65536:
                raise RuntimeError('Unexpected sync response')
            if len(pending) < 8 + size:
                break
            payload = pending[8:8+size]
            pending = pending[8+size:]
            if kind == b'FAIL':
                raise RuntimeError('RECV failed: ' + payload.decode(errors='replace'))
            contents += payload
            if len(contents) > 1048576:
                raise RuntimeError('Configuration exceeds read limit')
        if done:
            break
    core.send_packet(t, CLSE, local, remote)
    if not done:
        raise RuntimeError('Read incomplete')
    print('READ_OK bytes=', len(contents), 'sha256=', hashlib.sha256(contents).hexdigest())
    if requested_path == '/dev/block/sda9':
        if len(contents) != 524288:
            raise RuntimeError('Unexpected FRP partition size; no backup saved')
        backup_path = args.backup
        fd = os.open(backup_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as out:
            out.write(contents)
            out.flush()
            os.fsync(out.fileno())
        print('BACKUP_SAVED', backup_path)
        raise SystemExit(0)
    for line in contents.decode(errors='replace').splitlines():
        if requested_path in ('/sys/fs/selinux/enforce', '/sys/class/block/sda9/uevent', '/proc/partitions') or line.startswith(('Name:', 'Uid:', 'Gid:', 'CapEff:', 'NoNewPrivs:', 'Seccomp:', 'ro.build.version.', 'ro.product.device=', 'ro.adb.secure=', 'ro.debuggable=')):
            print(line)
finally:
    usb.util.dispose_resources(d)
