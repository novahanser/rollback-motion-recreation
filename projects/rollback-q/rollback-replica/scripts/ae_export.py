"""Scene -> After Effects project JSON (schema v2 of the aftereffects MCP `ae_project_import_json`).

Structure
  RB_WORLD  14400x2600  every world-space element, laid out as one long panorama (+ per-element animation)
  RB_MAIN   1920x1080   background solids  ->  RB_WORLD (camera move = position/scale keys)  ->  overlays / adjustments
World point (x, y) sits at RB_WORLD pixel (x + OX, y + OY).
"""
import json, os
from lib import FPS, NFRAMES, W, H, LIN, HOLD, BEZ

INTERP = {'linear': 6612, 'bezier': 6613, 'hold': 6614}
LABELS = {'BG': 1, 'A': 9, 'B': 8, 'C': 10, 'D': 11, 'INTRO': 2, 'FX': 14, 'RULER': 6, 'CAM': 16, 'SCR': 13}
OX, OY = 1800, 760
WORLD_W, WORLD_H = 14400, 2600
COMPS_DIR, FOOTAGE_DIR, SOLIDS_DIR = '01_合成', '02_素材', '03_纯色'
# footage sub-folders by file-name prefix (first match wins; the last entry is the fallback)
GROUPS = [('A_', 'A_开场与环组'), ('B_', 'B_黑场与窗口'), ('C_', 'C_线稿与胶片'), ('D_', 'D_结尾标题'),
          ('F_', 'F_胶片小人'), ('', 'X_标尺与全局效果')]


def group_of(pathname):
    base = os.path.basename(pathname)
    for pre, gname in GROUPS:
        if base.startswith(pre):
            return gname


def _t(f):
    return round(f / FPS, 6)


def _kf(f, v, interp, dims=1):
    k = {'time': _t(f), 'value': v}
    if isinstance(interp, tuple):          # ('bez', in_influence, out_influence)
        _, ii, oi = interp
        k['inInterp'] = k['outInterp'] = INTERP['bezier']
        k['inEase'] = [{'speed': 0, 'influence': ii}] * dims
        k['outEase'] = [{'speed': 0, 'influence': oi}] * dims
    elif interp == BEZ:
        k['inInterp'] = k['outInterp'] = INTERP['bezier']
        k['inEase'] = [{'speed': 0, 'influence': 33}] * dims
        k['outEase'] = [{'speed': 0, 'influence': 33}] * dims
    elif interp == HOLD:
        k['inInterp'] = INTERP['linear']
        k['outInterp'] = INTERP['hold']
    else:
        k['inInterp'] = k['outInterp'] = INTERP['linear']
    return k


def _prop(match, vtype, value, keys=None, dims=1):
    p = {'matchName': match, 'propertyValueType': vtype, 'value': value}
    if keys:
        p['keyframes'] = [_kf(f, v, i, dims) for (f, v, i) in keys]
        p['value'] = keys[0][1]
    return p


def _transform(anchor, pos, scale, rot, op, keys, k=1.0, off=(0.0, 0.0)):
    def P(v):
        return [v[0] + off[0], v[1] + off[1], 0]

    def S(v):
        return [v[0] / k, v[1] / k, 100]

    pk = [(f, P(v), i) for (f, v, i) in keys.get('position', [])]
    sk = [(f, S(v), i) for (f, v, i) in keys.get('scale', [])]
    return {'matchName': 'ADBE Transform Group', 'properties': [
        _prop('ADBE Anchor Point', 'ThreeD_SPATIAL', [anchor[0], anchor[1], 0]),
        _prop('ADBE Position', 'ThreeD_SPATIAL', P(pos), pk or None, 1),
        _prop('ADBE Scale', 'ThreeD', S(scale), sk or None, 3),
        _prop('ADBE Rotate Z', 'OneD', rot, keys.get('rotation') or None, 1),
        _prop('ADBE Opacity', 'OneD', op, keys.get('opacity') or None, 1),
    ], 'groups': []}


def _effects(effects):
    if not effects:
        return None
    groups = []
    for e in effects:
        props = []
        for mn, v in e['props'].items():
            if isinstance(v, list) and v and isinstance(v[0], tuple):       # keyframes
                first = v[0][1]
                if isinstance(first, list):
                    vt = 'COLOR' if len(first) == 4 else 'TwoD_SPATIAL'
                    props.append(_prop(mn, vt, first, v, 1 if vt == 'TwoD_SPATIAL' else 4))
                else:
                    props.append(_prop(mn, 'OneD', first, v, 1))
            elif isinstance(v, list):
                props.append(_prop(mn, 'COLOR' if len(v) == 4 else 'TwoD_SPATIAL', v))
            else:
                props.append(_prop(mn, 'OneD', v))
        g = {'matchName': e['match'], 'properties': props, 'groups': []}
        groups.append(g)
    return {'matchName': 'ADBE Effect Parade', 'properties': [], 'groups': groups}


def export(scene, cam, path, folder='RB_REPLICA'):
    items = []
    nid = [0]

    def new_id():
        nid[0] += 1
        return nid[0]

    # project panel layout: comps / footage (one sub-folder per section, see GROUPS) / solids
    root = new_id()
    items.append({'id': root, 'name': folder, 'type': 'FolderItem', 'parentFolderId': 0})
    f_comps = new_id()
    items.append({'id': f_comps, 'name': COMPS_DIR, 'type': 'FolderItem', 'parentFolderId': root})
    f_assets = new_id()
    items.append({'id': f_assets, 'name': FOOTAGE_DIR, 'type': 'FolderItem', 'parentFolderId': root})
    f_group = {}
    for _, gname in GROUPS:
        if gname not in f_group:
            f_group[gname] = new_id()
            items.append({'id': f_group[gname], 'name': gname, 'type': 'FolderItem', 'parentFolderId': f_assets})
    f_solids = new_id()
    items.append({'id': f_solids, 'name': SOLIDS_DIR, 'type': 'FolderItem', 'parentFolderId': root})

    file_ids = {}

    def footage(pathname, size):
        key = os.path.abspath(pathname)
        if key not in file_ids:
            i = new_id()
            file_ids[key] = i
            items.append({'id': i, 'name': os.path.basename(pathname), 'type': 'FootageItem', 'parentFolderId': f_group[group_of(pathname)],
                          'sourceKind': 'file', 'file': key.replace('\\', '/'), 'width': size[0], 'height': size[1], 'duration': 0})
        return file_ids[key]

    def solid(name, color, w, h):
        i = new_id()
        items.append({'id': i, 'name': name, 'type': 'FootageItem', 'parentFolderId': f_solids, 'sourceKind': 'solid',
                      'color': [c / 255.0 for c in color], 'sourceWidth': int(w), 'sourceHeight': int(h),
                      'width': int(w), 'height': int(h), 'duration': 0})
        return i

    dur = NFRAMES / FPS
    post = {'blend': [], 'adjust': [], 'collapse': [['RB_MAIN', 'RB_WORLD']]}

    def layer_json(L, idx, off, comp_name):
        if L.kind == 'footage':
            src = footage(L.file, L.size)
        else:
            src = solid(L.name, L.color, L.size[0], L.size[1])
        k = L.k
        anchor = [(L.pivot[0] - L.x) * k, (L.pivot[1] - L.y) * k]
        lay = {'index': idx, 'name': L.name, 'type': 'AVLayer', 'enabled': True,
               'inPoint': _t(L.t_in), 'outPoint': _t(min(L.t_out, NFRAMES)), 'startTime': 0, 'stretch': 100,
               'parentIndex': None, 'sourceId': src, 'label': L.label or LABELS.get(L.sec, 0),
               'transformGroup': _transform(anchor, [L.pivot[0], L.pivot[1]], L.static.get('scale', [100.0, 100.0]),
                                            L.static.get('rotation', 0.0), L.static.get('opacity', 100.0), L.keys, k, off)}
        eg = _effects(L.effects)
        if eg:
            lay['effectsGroup'] = eg
        if L.blend != 'normal':
            post['blend'].append([comp_name, L.name, L.blend])
        if L.kind == 'adjust':
            post['adjust'].append([comp_name, L.name])
        return lay

    world = [L for L in scene.layers if not L.screen]
    first_world = min([i for i, L in enumerate(scene.layers) if not L.screen] or [len(scene.layers)])
    below = [L for i, L in enumerate(scene.layers) if L.screen and (i < first_world or L.below)]
    above = [L for i, L in enumerate(scene.layers) if L.screen and i > first_world and not L.below]

    # ---- RB_WORLD
    wl = [layer_json(L, n + 1, (OX, OY), 'RB_WORLD') for n, L in enumerate(reversed(world))]
    world_id = new_id()
    items.append({'id': world_id, 'name': 'RB_WORLD', 'type': 'CompItem', 'parentFolderId': f_comps, 'width': WORLD_W,
                  'height': WORLD_H, 'frameRate': FPS, 'duration': dur, 'bgColor': [0.2, 0.2, 0.2], 'workAreaStart': 0,
                  'workAreaDuration': dur, 'pixelAspect': 1, 'layers': wl})

    # ---- RB_MAIN
    ml = []
    idx = 1
    for L in reversed(above):
        ml.append(layer_json(L, idx, (0, 0), 'RB_MAIN'))
        idx += 1
    pos_keys = [(c['f'], [960 - c['cx'] * c['s'], 540.0], LIN) for c in cam]
    sc_keys = [(c['f'], [100 * c['s'], 100 * c['s']], LIN) for c in cam]
    ml.append({'index': idx, 'name': 'RB_WORLD', 'type': 'AVLayer', 'enabled': True, 'inPoint': 0, 'outPoint': dur,
               'startTime': 0, 'stretch': 100, 'parentIndex': None, 'sourceId': world_id, 'label': LABELS['CAM'],
               'transformGroup': _transform([OX, OY + 540.0], pos_keys[0][1], [100, 100], 0, 100,
                                            dict({'position': pos_keys, 'scale': sc_keys}, **getattr(scene, 'world_keys', {})))})
    idx += 1
    for L in reversed(below):
        ml.append(layer_json(L, idx, (0, 0), 'RB_MAIN'))
        idx += 1
    main_id = new_id()
    items.append({'id': main_id, 'name': 'RB_MAIN', 'type': 'CompItem', 'parentFolderId': f_comps, 'width': W, 'height': H,
                  'frameRate': FPS, 'duration': dur, 'bgColor': [0, 0, 0], 'workAreaStart': 0, 'workAreaDuration': dur,
                  'pixelAspect': 1, 'layers': ml})
    doc = {'schemaVersion': 2, 'project': {'bitsPerChannel': 8}, 'items': items}
    json.dump(doc, open(path, 'w'))
    json.dump(post, open(os.path.splitext(path)[0] + '_post.json', 'w'), indent=1)
    return doc, post
