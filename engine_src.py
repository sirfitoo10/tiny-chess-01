import json, os, sys, urllib.request, urllib.error
ENV = os.environ.get('MAKEFUN_ENV_URL') or sys.exit('no env')

def post(path, body):
    req = urllib.request.Request(ENV + path, data=json.dumps(body).encode(), headers={'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f'{path}: HTTP {e.code}')
P, N, B, R, Q, K = (1, 2, 3, 4, 5, 6)
VAL = (0, 100, 320, 330, 500, 900, 0, 0, 0, 100, 320, 330, 500, 900, 0)
N_OFF = (21, 19, 12, 8, -21, -19, -12, -8)
K_OFF = (11, -11, 10, -10, 9, -9, 1, -1)
B_DIRS = (11, -11, 9, -9)
R_DIRS = (10, -10, 1, -1)
CENTER = (0, 1, 2, 3, 3, 2, 1, 0)

def pst(pc, i):
    f, r = (i % 10 - 1, 11 - i // 10 - 1)
    c = CENTER[f] + CENTER[7 - r]
    t = pc if pc < 8 else pc - 8
    s = 1 if pc < 8 else -1
    if t == P:
        return s * ((6 - r if pc < 8 else r - 1) * 8 + c * 2)
    if t == N:
        return s * c * 8
    if t == B:
        return s * c * 5
    if t == R:
        return s * c * 3
    if t == Q:
        return s * c * 2
    return s * c * 3

class Pos:
    __slots__ = ('b', 'side', 'cast', 'ep', 'half', 'hist')

def parse(fen):
    p = Pos()
    p.b = [7] * 120
    for i in range(21, 99):
        if 0 < i % 10 < 9:
            p.b[i] = 0
    rows = fen.split()[0].split('/')
    for ri, row in enumerate(rows):
        f = 0
        for c in row:
            if c.isdigit():
                f += int(c)
            else:
                p.b[21 + ri * 10 + f] = 'PNBRQK'.index(c.upper()) + 1 + (8 if c.islower() else 0)
                f += 1
    rest = fen.split()
    p.side = rest[1] == 'b'
    p.cast = rest[2]
    p.ep = 0
    if rest[3] != '-':
        p.ep = 21 + (8 - int(rest[3][1])) * 10 + 'abcdefgh'.index(rest[3][0])
    p.half = int(rest[4]) if len(rest) > 4 else 0
    p.hist = []
    return p

def fen(p):
    rows = []
    for ri in range(8):
        row, empty = ('', 0)
        for f in range(8):
            pc = p.b[21 + ri * 10 + f]
            if pc == 0:
                empty += 1
            else:
                if empty:
                    row += str(empty)
                    empty = 0
                ch = 'PNBRQK'[pc % 8 - 1]
                row += ch if pc < 8 else ch.lower()
        if empty:
            row += str(empty)
        rows.append(row)
    ep = '-' if not p.ep else 'abcdefgh'[p.ep % 10 - 1] + str(10 - p.ep // 10)
    return '/'.join(rows) + (' b ' if p.side else ' w ') + p.cast + ' ' + ep + ' ' + str(p.half)

def at(p, sq, by_white):
    """Is square sq attacked by the side by_white?"""
    b = p.b
    if by_white:
        for d in (9, 11):
            if 21 <= sq + d < 99 and b[sq + d] == P:
                return True
        kn, bi, ro, qu, ki = (N, B, R, Q, K)
    else:
        for d in (-9, -11):
            if 21 <= sq + d < 99 and b[sq + d] == 9:
                return True
        kn, bi, ro, qu, ki = (N + 8, B + 8, R + 8, Q + 8, K + 8)
    for d in N_OFF:
        if b[sq + d] == kn:
            return True
    for d in B_DIRS:
        t = sq + d
        while b[t] == 0:
            t += d
        if b[t] == bi or b[t] == qu:
            return True
    for d in R_DIRS:
        t = sq + d
        while b[t] == 0:
            t += d
        if b[t] == ro or b[t] == qu:
            return True
    for d in K_OFF:
        if b[sq + d] == ki:
            return True
    return False

def mv(p, caps_only=False):
    """Pseudo-lg moves as (frm, to, flag): flag 0 quiet, 1 capture/ep, 2 castle."""
    b, mine, out = (p.b, (1, 6) if not p.side else (9, 14), [])
    lo, hi = (1, 6) if not p.side else (9, 14)
    for sq in range(21, 99):
        pc = b[sq]
        if pc == 0 or pc == 7 or (not lo <= pc <= hi):
            continue
        t = pc if pc < 8 else pc - 8
        if t == P:
            d = -10 if pc < 8 else 10
            start = 81 if pc < 8 else 31
            nxt = sq + d
            promo = nxt // 10 in (2, 9)
            if b[nxt] == 0 and (not caps_only):
                out += [(sq, nxt, f) for f in (6, 5, 4, 3)] if promo else [(sq, nxt, 0)]
                if start <= sq <= start + 7 and b[nxt + d] == 0:
                    out.append((sq, nxt + d, 0))
            for dd in (-1, 1):
                cap = nxt + dd
                tgt = b[cap]
                if tgt != 0 and tgt != 7 and ((tgt < 8) != (pc < 8)) or (cap == p.ep and p.ep):
                    out += [(sq, cap, f) for f in (6, 5, 4, 3)] if promo else [(sq, cap, 1)]
        elif t == N or t == K:
            for d in N_OFF if t == N else K_OFF:
                to = sq + d
                tgt = b[to]
                if tgt == 7:
                    continue
                if tgt == 0:
                    if not caps_only:
                        out.append((sq, to, 0))
                elif (tgt < 8) != (pc < 8):
                    out.append((sq, to, 1))
            if t == K and (not caps_only):
                if pc == K and 'K' in p.cast and (b[96] == 0) and (b[97] == 0) and (b[98] == R) and (not at(p, 95, False)) and (not at(p, 96, False)) and (not at(p, 97, False)):
                    out.append((sq, 97, 2))
                if pc == K and 'Q' in p.cast and (b[94] == 0) and (b[93] == 0) and (b[92] == 0) and (b[91] == R) and (not at(p, 95, False)) and (not at(p, 94, False)) and (not at(p, 93, False)):
                    out.append((sq, 93, 2))
                if pc == K + 8 and 'k' in p.cast and (b[26] == 0) and (b[27] == 0) and (b[28] == R + 8) and (not at(p, 25, True)) and (not at(p, 26, True)) and (not at(p, 27, True)):
                    out.append((sq, 27, 2))
                if pc == K + 8 and 'q' in p.cast and (b[24] == 0) and (b[23] == 0) and (b[22] == 0) and (b[21] == R + 8) and (not at(p, 25, True)) and (not at(p, 24, True)) and (not at(p, 23, True)):
                    out.append((sq, 23, 2))
        else:
            dirs = B_DIRS if t == B else R_DIRS if t == R else K_OFF
            for d in dirs:
                to = sq + d
                while b[to] == 0:
                    if not caps_only:
                        out.append((sq, to, 0))
                    to += d
                tgt = b[to]
                if tgt != 7 and tgt != 0 and ((tgt < 8) != (pc < 8)):
                    out.append((sq, to, 1))
    return out

def kq(p, white):
    k = K if white else K + 8
    for i in range(21, 99):
        if p.b[i] == k:
            return i
    return 0

def lg(p):
    out = []
    for m in mv(p):
        mk(p, m)
        if not at(p, kq(p, p.side), not p.side):
            out.append(m)
        um(p)
    return out

def mk(p, m):
    frm, to, fl = m
    b = p.b
    pc = b[frm]
    cap = b[to]
    p.hist.append((m, cap, p.cast, p.ep, p.half))
    p.ep = 0
    b[to] = pc
    b[frm] = 0
    t = pc if pc < 8 else pc - 8
    rank = to // 10
    if t == P and (rank == 2 or rank == 9):
        b[to] = (Q if fl >= 6 else N if fl == 3 else B if fl == 4 else R) + (0 if pc < 8 else 8)
    if fl == 2:
        if to == 97:
            b[98], b[96] = (0, R)
        elif to == 93:
            b[91], b[94] = (0, R)
        elif to == 27:
            b[28], b[26] = (0, R + 8)
        elif to == 23:
            b[21], b[24] = (0, R + 8)
    if t == P and to == p.hist[-1][3] and (cap == 0) and (frm % 10 != to % 10):
        b[to + (10 if pc < 8 else -10)] = 0
    if t == K:
        p.cast = p.cast.replace('K', '').replace('Q', '') if pc < 8 else p.cast.replace('k', '').replace('q', '')
    if t == R:
        if frm == 28:
            p.cast = p.cast.replace('k', '')
        elif frm == 21:
            p.cast = p.cast.replace('q', '')
        elif frm == 98:
            p.cast = p.cast.replace('K', '')
        elif frm == 91:
            p.cast = p.cast.replace('Q', '')
    if t == P and abs(to - frm) == 20:
        p.ep = (frm + to) // 2
    if cap != 0 or t == P:
        p.half = 0
    else:
        p.half += 1
    p.side = not p.side

def um(p):
    m, cap, cast, ep, half = p.hist.pop()
    frm, to, fl = m
    b = p.b
    pc = b[to]
    b[frm] = pc
    b[to] = cap
    t = pc if pc < 8 else pc - 8
    if fl >= 3:
        b[frm] = P if pc < 8 else P + 8
    if fl == 2:
        if to == 97:
            b[96], b[98] = (0, R)
        elif to == 93:
            b[94], b[91] = (0, R)
        elif to == 27:
            b[26], b[28] = (0, R + 8)
        elif to == 23:
            b[24], b[21] = (0, R + 8)
    if t == P and to == ep and (cap == 0) and (frm % 10 != to % 10):
        b[to + (10 if pc < 8 else -10)] = 9 if pc < 8 else 1
    p.cast, p.ep, p.half = (cast, ep, half)
    p.side = not p.side

def ev(p):
    """Material + PST from the side to move's perspective."""
    s = 0
    b = p.b
    for i in range(21, 99):
        pc = b[i]
        if pc == 0 or pc == 7:
            continue
        if pc < 8:
            s += VAL[pc] + pst(pc, i)
        else:
            s -= VAL[pc] + pst(pc, i)
    return -s if p.side else s
ND = 0
LM = 40000
KL = [set() for _ in range(10)]

def qs(p, a, be):
    global ND
    ND += 1
    s = ev(p)
    if s >= be:
        return be
    if s > a:
        a = s
    for m in mv(p, True):
        mk(p, m)
        if not at(p, kq(p, not p.side), p.side):
            v = -qs(p, -be, -a)
            um(p)
            if v >= be:
                return be
            if v > a:
                a = v
        else:
            um(p)
    return a

def sx(p, d, a, be):
    global ND
    ND += 1
    if ND > LM:
        return a
    if d == 0:
        return qs(p, a, be)
    ms = lg(p)
    if not ms:
        return -30000 if at(p, kq(p, not p.side), p.side) else 0
    kl = KL[d]
    ms.sort(key=lambda m: (-((VAL[p.b[m[1]]] if p.b[m[1]] else 0) - VAL[p.b[m[0]]] // 10), 0 if m[:2] in kl else 1))
    best = -99999
    for m in ms:
        mk(p, m)
        ext = 1 if at(p, kq(p, not p.side), p.side) else 0
        v = -sx(p, d - 1 + ext, -be, -a)
        um(p)
        if v > best:
            best = v
        if v > a:
            a = v
        if a >= be:
            if p.b[m[1]] == 0:
                kl.add(m[:2])
            break
    return best

def cm(p, bu=200000):
    global ND, LM
    ms = lg(p)
    if not ms:
        return None
    bm = ms[0]
    LM = bu
    ND = 0
    KL[:] = [set() for _ in range(10)]
    prev = {}
    for d in range(1, 6):
        ms.sort(key=lambda m: -prev.get(m, -99999))
        sc = []
        for m in ms:
            mk(p, m)
            v = -sx(p, d - 1, -99999, 99999)
            um(p)
            sc.append((v, m))
            if ND > LM:
                break
        prev = {m: v for v, m in sc}
        if sc and ND <= LM:
            sc.sort(key=lambda x: (-x[0], x[1]))
            bm = sc[0][1]
        elif sc:
            break
        if ND > LM:
            break
    return bm

def main():
    while True:
        g = post('/game', {})
        if g['status'] == 'done':
            break
        while g['status'] == 'your_move':
            p = parse(g['fen'])
            m = cm(p)
            if m is None:
                post('/resign', {'game': g['game']})
                break
            frm, to, fl = m
            uci = 'abcdefgh'[frm % 10 - 1] + str(10 - frm // 10) + 'abcdefgh'[to % 10 - 1] + str(10 - to // 10)
            pc = p.b[to] if False else None
            if p.b[frm] % 8 == P and (to // 10 == 2 or to // 10 == 9):
                uci += 'q'
            g = post('/move', {'game': g['game'], 'move': uci})
main()