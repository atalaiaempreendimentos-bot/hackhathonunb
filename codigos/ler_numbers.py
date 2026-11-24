"""Leitor mínimo de tabelas do Apple Numbers (.numbers, formato IWA) sem dependências externas.
Uso: python3 -I ler_numbers.py pasta_extraida saida.csv
"""
import csv, os, struct, sys, glob


def snappy_decompress(buf):
    # comprimento descomprimido (varint)
    pos, shift, ulen = 0, 0, 0
    while True:
        b = buf[pos]; pos += 1
        ulen |= (b & 0x7F) << shift
        if b < 0x80: break
        shift += 7
    out = bytearray()
    while pos < len(buf):
        tag = buf[pos]; pos += 1
        t = tag & 3
        if t == 0:
            ln = tag >> 2
            if ln < 60:
                ln += 1
            else:
                nb = ln - 59
                ln = int.from_bytes(buf[pos:pos + nb], "little") + 1; pos += nb
            out += buf[pos:pos + ln]; pos += ln
        else:
            if t == 1:
                ln = ((tag >> 2) & 7) + 4
                off = ((tag >> 5) << 8) | buf[pos]; pos += 1
            elif t == 2:
                ln = (tag >> 2) + 1
                off = int.from_bytes(buf[pos:pos + 2], "little"); pos += 2
            else:
                ln = (tag >> 2) + 1
                off = int.from_bytes(buf[pos:pos + 4], "little"); pos += 4
            for _ in range(ln):
                out.append(out[-off])
    return bytes(out)


def iwa_decompress(data):
    out, pos = bytearray(), 0
    while pos < len(data):
        assert data[pos] == 0
        ln = int.from_bytes(data[pos + 1:pos + 4], "little")
        out += snappy_decompress(data[pos + 4:pos + 4 + ln])
        pos += 4 + ln
    return bytes(out)


def varint(b, p):
    r, s = 0, 0
    while True:
        x = b[p]; p += 1
        r |= (x & 0x7F) << s
        if x < 0x80: return r, p
        s += 7


def pb(b):
    """protobuf genérico: {campo: [valores]} (bytes para length-delimited)."""
    d, p = {}, 0
    while p < len(b):
        k, p = varint(b, p)
        f, wt = k >> 3, k & 7
        if wt == 0:
            v, p = varint(b, p)
        elif wt == 1:
            v = b[p:p + 8]; p += 8
        elif wt == 2:
            ln, p = varint(b, p); v = b[p:p + ln]; p += ln
        elif wt == 5:
            v = b[p:p + 4]; p += 4
        else:
            raise ValueError("wire type %d" % wt)
        d.setdefault(f, []).append(v)
    return d


def objetos(path):
    data = iwa_decompress(open(path, "rb").read())
    p, objs = 0, []
    while p < len(data):
        ln, p = varint(data, p)
        info = pb(data[p:p + ln]); p += ln
        ident = info.get(1, [0])[0]
        for mi in info.get(2, []):
            m = pb(mi)
            mlen = m[3][0]
            objs.append((ident, m[1][0], data[p:p + mlen])); p += mlen
    return objs


def dec128(buf):
    exp = ((buf[15] & 0x7F) << 7) | (buf[14] >> 1)
    exp -= 0x1820
    mant = buf[14] & 1
    for i in range(13, -1, -1):
        mant = mant * 256 + buf[i]
    if buf[15] & 0x80:
        mant = -mant
    return float(mant * (10 ** exp)) if exp < 0 else float(mant * 10 ** exp)


def main():
    pasta, saida = sys.argv[1], sys.argv[2]
    # tabelas de strings: DataLists com entradas que têm campo 3 (string)
    strings = {}
    for f in glob.glob(os.path.join(pasta, "Index/Tables/DataList-*.iwa")):
        for ident, typ, msg in objetos(f):
            d = pb(msg)
            tab = {}
            for e in d.get(3, []):
                ed = pb(e)
                if 3 in ed:
                    tab[ed[1][0]] = ed[3][0].decode("utf-8", "replace")
            if tab:
                strings[ident] = tab
    print("tabelas de strings:", {k: len(v) for k, v in strings.items()})
    linhas = {}
    for f in sorted(glob.glob(os.path.join(pasta, "Index/Tables/Tile-*.iwa"))):
        for ident, typ, msg in objetos(f):
            d = pb(msg)
            for ri in d.get(5, []):
                r = pb(ri)
                row = r[1][0]
                buf = r.get(6, [b""])[0] if 6 in r else b""
                offs = r.get(7, [b""])[0] if 7 in r else b""
                wide = r.get(8, [0])[0] if 8 in r else 0
                if not buf:
                    continue
                cells = {}
                for col in range(len(offs) // 2):
                    o = struct.unpack_from("<H", offs, col * 2)[0]
                    if o == 0xFFFF:
                        continue
                    if wide:
                        o *= 4
                    c = buf[o:]
                    ctype = c[1]
                    flags = struct.unpack_from("<I", c, 8)[0]
                    q = 12
                    val = None
                    dval = num = sid = rid = None
                    if flags & 0x1:
                        num = dec128(c[q:q + 16]); q += 16
                    if flags & 0x2:
                        dval = struct.unpack_from("<d", c, q)[0]; q += 8
                    if flags & 0x4:
                        secs = struct.unpack_from("<d", c, q)[0]; q += 8
                        import datetime
                        val = (datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=secs)).strftime("%Y-%m-%d")
                    if flags & 0x8:
                        sid = struct.unpack_from("<i", c, q)[0]; q += 4
                    if flags & 0x10:
                        rid = struct.unpack_from("<i", c, q)[0]; q += 4
                    if val is None:
                        if sid is not None:
                            val = ("S", sid)
                        elif num is not None:
                            val = num
                        elif dval is not None:
                            val = dval
                        elif rid is not None:
                            val = ("R", rid)
                    cells[col] = (ctype, val)
                linhas[(ident, row)] = cells
    # escolhe a tabela de strings mais usada
    st = max(strings.values(), key=len) if strings else {}
    maxcol = max((max(c.keys()) for c in linhas.values() if c), default=-1)
    with open(saida, "w", encoding="utf-8", newline="") as fo:
        w = csv.writer(fo)
        for key in sorted(linhas):
            cells = linhas[key]
            row = []
            for col in range(maxcol + 1):
                if col not in cells:
                    row.append(""); continue
                ctype, v = cells[col]
                if isinstance(v, tuple) and v[0] == "S":
                    row.append(st.get(v[1], "<str %d>" % v[1]))
                elif isinstance(v, tuple):
                    row.append("<rich %d>" % v[1])
                elif isinstance(v, float):
                    row.append(("%.2f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v)))
                else:
                    row.append("" if v is None else str(v))
            w.writerow(row)
    print("linhas:", len(linhas), "colunas:", maxcol + 1)


if __name__ == "__main__":
    main()
