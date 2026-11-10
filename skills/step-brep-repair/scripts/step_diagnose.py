#!/usr/bin/env python3
"""Read-only STEP B-rep diagnostic; run with FreeCAD's Python. No repairs."""
import argparse
import collections
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path


def vector(v):
    return [float(v.x), float(v.y), float(v.z)]


def bounds(shape):
    try:
        b = shape.BoundBox
        return [float(b.XMin), float(b.YMin), float(b.ZMin), float(b.XMax), float(b.YMax), float(b.ZMax)]
    except Exception:
        return None


def inspect_units(path):
    # Inspect file text, do not guess from coordinate values; multiple contexts are possible.
    try:
        with open(path, 'rb') as f:
            data = f.read().decode('latin1')
        units = []
        for prefix in re.findall(r'LENGTH_UNIT\s*\(\s*\)\s*NAMED_UNIT\s*\(\s*\*\s*\)\s*SI_UNIT\s*\(\s*(\.[A-Z]+\.|\$)\s*,\s*\.METRE\.\s*\)', data, re.I):
            label = {'$': 'm', '.MILLI.': 'mm', '.CENTI.': 'cm', '.MICRO.': 'µm', '.KILO.': 'km'}.get(prefix.upper(), prefix + ' metre')
            if label not in units:
                units.append(label)
        if 'CONVERSION_BASED_UNIT' in data.upper():
            units.append('conversion-based unit present; verify STEP context')
        return units or ['unknown: inspect STEP length unit context']
    except Exception as exc:
        return ['unknown: ' + str(exc)]


def main():
    parser = argparse.ArgumentParser(description='Read-only STEP B-rep audit using FreeCAD Python')
    parser.add_argument('input', help='STEP/STP input file')
    parser.add_argument('--json', help='new JSON output path (never overwrite existing file)')
    parser.add_argument('--point', nargs=3, type=float, metavar=('X', 'Y', 'Z'), help='approximate location in model coordinates')
    parser.add_argument('--radius', type=float, default=2.0, help='point search radius in model units, default 2')
    parser.add_argument('--limit', type=int, default=60, help='max detailed records per category, default 60')
    parser.add_argument('--mesh', action='store_true', help='optional diagnostic tessellation, not a repair')
    parser.add_argument('--deflection', type=float, default=0.2, help='linear tessellation deflection in model units')
    parser.add_argument('--angle', type=float, default=0.35, help='angular tessellation deflection in radians')
    args = parser.parse_args()
    if args.radius <= 0 or args.limit < 1 or args.deflection <= 0 or args.angle <= 0:
        parser.error('radius, limit, deflection and angle must be positive')
    source = Path(args.input).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in ('.step', '.stp'):
        parser.error('input must be an existing .step or .stp file')
    target = Path(args.json).expanduser().resolve() if args.json else None
    if target and (target == source or target.exists()):
        parser.error('JSON output must be new and must not overwrite the input or another file')
    try:
        import FreeCAD as App
        import Part
    except ImportError as exc:
        print('FreeCAD/Part unavailable. Run this script with FreeCAD Python: ' + str(exc), file=sys.stderr)
        return 2
    digest = hashlib.sha256()
    with open(source, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    errors = []
    report = {'input': str(source), 'sha256': digest.hexdigest(), 'bytes': source.stat().st_size,
              'length_unit_contexts': inspect_units(source), 'freecad_version': list(App.Version()),
              'limitations': ['Topology indices apply only to this read; reimport may change them.',
                  'B-rep validity/closed flags alone do not establish geometric closure or target-CAD acceptance.',
                  'Bounds may be conservative. Mesh is an approximate diagnostic, not a repaired CAD model.'],
              'errors': errors}
    try:
        shape = Part.read(str(source))
        if shape.isNull():
            raise ValueError('reader produced a null shape')
    except Exception as exc:
        print('STEP read failed: ' + str(exc), file=sys.stderr)
        return 3
    report['shape'] = {'type': shape.ShapeType, 'valid': bool(shape.isValid()), 'bounds': bounds(shape),
        'faces': len(shape.Faces), 'edges': len(shape.Edges), 'vertices': len(shape.Vertexes),
        'shells': len(shape.Shells), 'solids': len(shape.Solids)}
    report['shells'] = [{'index': i, 'faces': len(sh.Faces), 'closed_flag': bool(sh.isClosed()),
        'valid': bool(sh.isValid()), 'bounds': bounds(sh)} for i, sh in enumerate(shape.Shells, 1)]
    report['solids'] = [{'index': i, 'valid': bool(sh.isValid()), 'closed_flag': bool(sh.isClosed()),
        'volume': float(sh.Volume), 'bounds': bounds(sh)} for i, sh in enumerate(shape.Solids, 1)]
    for name, typ in [('vertices', Part.Vertex), ('edges', Part.Edge), ('faces', Part.Face)]:
        try:
            report.setdefault('tolerance_summary', {})[name] = {'max': float(shape.getTolerance(1, typ)),
                'mean': float(shape.getTolerance(0, typ))}
        except Exception as exc:
            errors.append('tolerance ' + name + ': ' + str(exc))
    # isSame identifies shared topology; face adjacency is not the same as edge use count
    # on a periodic seam, hence it is reported only as adjacency.
    abnormal, adjacent = [], []
    for i, edge in enumerate(shape.Edges, 1):
        try:
            n = len(shape.ancestorsOfType(edge, Part.Face))
            adjacent.append(n)
            if n != 2 or edge.Degenerated:
                record = {'index': i, 'adjacent_faces': n, 'degenerate': bool(edge.Degenerated),
                    'length': float(edge.Length), 'bounds': bounds(edge),
                    'vertices': [vector(v.Point) for v in edge.Vertexes]}
                if len(abnormal) < args.limit:
                    abnormal.append(record)
        except Exception as exc:
            errors.append('edge %d: %s' % (i, exc))
    report['edge_face_adjacency_counts'] = dict(sorted(collections.Counter(adjacent).items()))
    report['abnormal_edges_limited'] = abnormal
    report['edge_note'] = 'adjacency counts unique face ancestors, not oriented edge uses; seam/degenerate cases require manual review'
    # FreeCAD sortEdges accepts topological free edges but can fail on malformed or disconnected groups.
    try:
        free = [e for e in shape.Edges if len(shape.ancestorsOfType(e, Part.Face)) == 1 and not e.Degenerated]
        groups = Part.sortEdges(free)
        chains = []
        for group in groups[:args.limit]:
            try:
                wire = Part.Wire(group)
                chains.append({'edge_count': len(group), 'closed_flag': bool(wire.isClosed()),
                               'length': float(wire.Length), 'bounds': bounds(wire)})
            except Exception as exc:
                chains.append({'edge_count': len(group), 'error': str(exc)})
        report['free_boundary'] = {'nondegenerate_single_face_edges': len(free), 'groups': len(groups), 'chains_limited': chains,
             'warning': 'Not a complete open/closed-wire analysis; malformed topology and disconnected shapes need independent OCCT checks.'}
    except Exception as exc:
        errors.append('free boundary: ' + str(exc))
    if args.point:
        p = App.Vector(*args.point)
        pv = Part.Vertex(p)
        nearest = []
        for i, edge in enumerate(shape.Edges, 1):
            if edge.Degenerated:
                continue
            try:
                d = float(pv.distToShape(edge)[0])
                if d <= args.radius:
                    face_refs = shape.ancestorsOfType(edge, Part.Face)
                    face_ids = [j for j, f in enumerate(shape.Faces, 1) if any(f.isSame(x) for x in face_refs)]
                    nearest.append({'edge_index': i, 'distance': d, 'length': float(edge.Length),
                        'bounds': bounds(edge), 'vertices': [vector(v.Point) for v in edge.Vertexes], 'adjacent_face_indices': face_ids})
            except Exception as exc:
                errors.append('point distance edge %d: %s' % (i, exc))
        nearest.sort(key=lambda item: item['distance'])
        nearv = sorted([{'vertex_index': i, 'distance': float(v.Point.distanceToPoint(p)),
                          'coordinates': vector(v.Point)} for i, v in enumerate(shape.Vertexes, 1)], key=lambda x: x['distance'])
        report['point_search'] = {'coordinates': args.point, 'radius': args.radius,
            'edges_found': len(nearest), 'edges_limited': nearest[:args.limit],
            'closest_vertices': nearv[:min(args.limit, 10)],
            'warning': 'Distance is subject to geometry and kernel tolerances; point may lie on an edge, not a vertex.'}
    if args.mesh:
        try:
            import MeshPart
            m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=args.deflection,
                                       AngularDeflection=args.angle, Relative=False)
            pts, tris = m.Topology
            incidence = collections.Counter(tuple(sorted((int(a), int(b)))) for t in tris
                for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])))
            report['mesh_diagnostic'] = {'linear_deflection': args.deflection, 'angular_deflection_radians': args.angle,
                'vertices': len(pts), 'triangles': len(tris), 'components': m.countComponents(),
                'solid_flag': bool(m.isSolid()), 'edge_incidence_counts': dict(sorted(collections.Counter(incidence.values()).items())),
                'warning': 'Diagnostic tessellation only; non-watertight result can reflect representation or tessellation. Not an STL repair.'}
        except Exception as exc:
            errors.append('mesh: ' + str(exc))
    rendered = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if target:
        try:
            with open(target, 'x', encoding='utf-8', newline='\n') as f:
                f.write(rendered + '\n')
        except Exception as exc:
            print('Cannot write new report: ' + str(exc), file=sys.stderr)
            return 4
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print(rendered)
    return 0


if __name__ == '__main__':
    sys.exit(main())
