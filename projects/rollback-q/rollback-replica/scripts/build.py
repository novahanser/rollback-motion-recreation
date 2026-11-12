"""Build everything: assets -> scene -> static panorama preview + AE project JSON.

    python build.py            # full build
    python build.py pano       # also write the static panorama preview
"""
import sys, os, json, importlib
import lib
from lib import Scene, ROOT
import cam as camlib
import ae_export
import base

SECTIONS = ['sec_a', 'sec_a2', 'sec_b', 'sec_c', 'sec_d', 'fx']


def build():
    sc = Scene()
    base.build(sc)
    mods = {}
    for name in SECTIONS:
        if os.path.exists(os.path.join(lib.HERE, name + '.py')):
            mods[name] = importlib.import_module(name)
    # world content (bottom -> top). `fx` (screen-space overlays / adjustments) goes last.
    for name in SECTIONS:
        if name in mods and name != 'fx':
            mods[name].build(sc)
    base.build_ruler(sc)
    for name in SECTIONS:
        if name in mods and hasattr(mods[name], 'build_top'):
            mods[name].build_top(sc)
    if 'fx' in mods:
        mods['fx'].build(sc)
    return sc


if __name__ == '__main__':
    sc = build()
    cam = camlib.build()
    json.dump(cam, open(os.path.join(lib.HERE, 'cam.json'), 'w'))
    out = os.path.join(ROOT, 'ae', 'project.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc, post = ae_export.export(sc, cam, out)
    print('layers:', len(sc.layers), '| items:', len(doc['items']), '| blend fixes:', len(post['blend']), '| adjust:', len(post['adjust']))
    if 'pano' in sys.argv:
        p = os.path.join(ROOT, 'out', 'pano_preview.jpg')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        sc.pano_preview(p)
        print('pano preview ->', p)
