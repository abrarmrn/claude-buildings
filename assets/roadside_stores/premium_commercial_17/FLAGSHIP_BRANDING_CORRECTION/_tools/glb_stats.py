"""Tiny GLB inspector (no dependencies): per-node triangle counts, embedded images, material names.

python glb_stats.py file.glb [other.glb]   -> prints JSON; with two files prints a node-by-node diff.
"""
import json, struct, sys


def load(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'glTF'
    jl = struct.unpack_from('<I', b, 12)[0]
    return json.loads(b[20:20 + jl])


def stats(path):
    g = load(path)
    acc = g.get('accessors', [])
    mesh_tris = []
    for m in g.get('meshes', []):
        t = 0
        for p in m['primitives']:
            if p.get('mode', 4) != 4:
                continue
            t += (acc[p['indices']]['count'] if 'indices' in p else acc[p['attributes']['POSITION']]['count']) // 3
        mesh_tris.append(t)
    nodes = {}
    for n in g.get('nodes', []):
        if 'mesh' in n:
            nodes[n.get('name', '?')] = mesh_tris[n['mesh']]
    return dict(nodes=nodes, total=sum(nodes.values()), images=len(g.get('images', [])),
                materials=sorted(m.get('name', '') for m in g.get('materials', [])),
                lights=len(g.get('extensions', {}).get('KHR_lights_punctual', {}).get('lights', [])))


if __name__ == '__main__':
    a = stats(sys.argv[1])
    if len(sys.argv) == 2:
        print(json.dumps(a, indent=1)); sys.exit()
    b = stats(sys.argv[2])
    sig = lambda k: 'SIGNAGE' in k
    changed = {k: (a['nodes'].get(k), b['nodes'].get(k)) for k in set(a['nodes']) | set(b['nodes'])
               if a['nodes'].get(k) != b['nodes'].get(k)}
    out = dict(total_before=a['total'], total_after=b['total'],
               non_signage_changed={k: v for k, v in changed.items() if not sig(k)},
               signage_changed=changed and {k: v for k, v in changed.items() if sig(k)},
               non_signage_nodes_identical=all(sig(k) for k in changed),
               images=(a['images'], b['images']), lights=(a['lights'], b['lights']))
    print(json.dumps(out, indent=1))
