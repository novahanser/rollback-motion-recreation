"""v12: the bracelet becomes a per-frame rendered rotating ring (scripts/chain3d.py)"""
p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_b.py'
s = open(p, encoding='utf-8').read()

old = """    # The bracelet is glued to the SCREEN from 105 to 136 (same place and size while the camera pans and pulls back; it is
    # uncovered from the right on 105-107 and changes its outline a little on 125 / 132); from 137 it stays in the world, twice
    # as large, drifting 2 px per frame.  Boxes = (centre x, centre y, width, height) in screen px, read off the source.
    box = {105: (842.0, 422.0, 306.0, 174.0), 125: (820.5, 424.5, 266.0, 173.0), 126: (824.5, 427.0, 271.0, 176.0), 127: (823.0, 424.0, 266.0, 173.0),
           128: (826.5, 419.5, 277.0, 165.0), 132: (843.5, 431.0, 283.0, 164.5), 134: (841.0, 439.5, 282.0, 165.0), 135: (830.5, 440.5, 283.0, 163.0),
           136: (810.0, 440.5, 278.0, 163.0)}
    chain = sc.add('B_chain', bead_chain2, 4115.5 - CHAIN_W / 2, 392.0 - CHAIN_H / 2)
    chain.span(105)
    cur, kp, ksc = box[105], [], []
    for f in range(105, 137):
        cur = box.get(f, cur)
        kp.append((f, list(s2w(f, cur[0], cur[1])), HOLD))
        ksc.append((f, [cur[2] / zoom(f) / CHAIN_W * 100.0, cur[3] / zoom(f) / CHAIN_H * 100.0], HOLD))
    kp += [(137, [4115.5, 392.0], LIN), (150, [4140.0, 392.0], LIN)]
    ksc += [(137, [393.0 / CHAIN_W * 100.0, 238.0 / CHAIN_H * 100.0], HOLD)]
    chain.key('position', kp).key('scale', ksc)
    chain.static['scale'] = [393.0 / CHAIN_W * 100.0, 238.0 / CHAIN_H * 100.0]
    chain.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(105, 40.8, HOLD), (106, 17.6, HOLD), (107, 1.3, HOLD), (108, 0.0, HOLD)],
                                    'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
"""
new = """    # The bracelet is a ring of 13 fused chrome pearls that TURNS (chain3d.py: 0.194 bead pitch per 30-fps source frame, conformed
    # to 24 fps, near row to the right).  Placement, fitted to the highlight blobs of the source (tools/chain_track.py):
    # glued to the SCREEN at (842,422) and full size on 105-131, shrinking to 0.913 and sliding on 132-136, and from 137 fixed in
    # the WORLD at about (4125,390).  It is uncovered from the right on 105-107.  One layer per frame (each a different pose).
    import chain3d
    place = {132: (850.0, 429.6, 0.973), 133: (850.5, 433.8, 0.937), 134: (846.5, 436.7, 0.913), 135: (830.2, 436.7, 0.913),
             136: (806.4, 436.4, 0.912)}
    trk = {137: 249.5, 138: 234.3, 139: 222.1, 140: 212.1, 141: 203.5, 142: 196.1, 143: 189.6, 144: 113.1, 145: 107.8, 146: 103.2,
           147: 99.0, 148: 95.0, 149: 91.4, 150: 87.8}
    wlast = sum(s2w(f, trk[f], 436.7)[0] for f in range(146, 151)) / 5.0
    BW, BH = chain3d.BOX[2], chain3d.BOX[3]
    wipe = {105: 41.6, 106: 20.5, 107: 5.7}
    for f in range(105, 164):
        if f <= 131:
            cx_, cy_, s_ = 842.0, 422.0, 1.0
        elif f <= 136:
            cx_, cy_, s_ = place[f]
        else:
            s_ = 0.913
            wx_ = s2w(f, trk[f], 436.7)[0] if f in trk else wlast
            cx_, cy_ = w2s(f, wx_, s2w(140, 0.0, 436.7)[1])
        z_ = zoom(f)
        wx0, wy0 = s2w(f, cx_ - BW * s_ / 2.0, cy_ - BH * s_ / 2.0)
        L = sc.add('B_chain_%03d' % f, chain3d.chain_frame, wx0, wy0, chain3d.src_index(f), chain3d.version(), k=chain3d.OUTK * z_ / s_, crop=False)
        L.span(f, f + 1).set(pano=(f == 140))
        if f in wipe:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': wipe[f], 'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
"""
assert s.count(old) == 1
s = s.replace(old, new)
if 'w2s' not in s.split('def ')[0]:
    old_imp = [ln for ln in s.split('\n') if ln.startswith('from gen_util import')][0]
    assert 'w2s' not in old_imp
    s = s.replace(old_imp, old_imp + ', w2s')
open(p, 'w', encoding='utf-8').write(s)
print('patched', [ln for ln in s.split('\n') if ln.startswith('from gen_util import')])
