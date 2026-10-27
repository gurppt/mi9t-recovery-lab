import pathlib, struct, gzip, stat
root=pathlib.Path(__file__).resolve().parents[1]/'artifacts'
p=root/'firmware/recovery.img'
b=p.read_bytes()
assert b[:8]==b'ANDROID!', b[:16]
k,ka,r,ra,s,sa,t,page,version,osversion=struct.unpack_from('<10I',b,8)
print(dict(kernel_size=k,ramdisk_size=r,page_size=page,header_version=version))
off=page+((k+page-1)//page)*page
ram=b[off:off+r]
(root/'firmware/ramdisk.bin').write_bytes(ram)
print('Ramdisk magic',ram[:16].hex())
if ram[:2]!=b'\x1f\x8b': raise SystemExit('Non-gzip ramdisk; inspect separately')
data=gzip.decompress(ram)
(root/'firmware/ramdisk.cpio').write_bytes(data)
out=root/'ramdisk'
out.mkdir(exist_ok=True)
off=0
while off+110<=len(data):
    hdr=data[off:off+110]
    assert hdr[:6] in (b'070701',b'070702'), (off,hdr[:6])
    fields=[int(hdr[6+j*8:14+j*8],16) for j in range(13)]
    mode,size,namesize=fields[1],fields[6],fields[11]
    name=data[off+110:off+110+namesize-1].decode()
    start=(off+110+namesize+3)&~3
    body=data[start:start+size]
    off=(start+size+3)&~3
    if name=='TRAILER!!!': break
    rel=pathlib.PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts: raise ValueError(name)
    if stat.S_ISREG(mode):
        target=out/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)
        print(name,size)
    elif stat.S_ISLNK(mode):
        print('SYMLINK (not created)',name,body.decode(errors='replace'))
