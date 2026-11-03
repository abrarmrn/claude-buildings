@tool
extends EditorScenePostImport

## Post-import script for the roadside store prototypes (.glb).
##
## How to use (per .glb): select the .glb in the FileSystem dock -> Import dock ->
## "Import Script" -> pick this file -> click "Reimport".
##
## What it does:
##  * Finds the <PREFIX>_LOD0 / _LOD1 / _LOD2 nodes. Their visibility ranges are read from the
##    glTF node extras (imported by Godot as the "extras" metadata) and, if that metadata is not
##    present, from the node-name suffix using DEFAULT_RANGES below.
##  * Applies visibility_range_begin / _end (+ hysteresis margins) to every GeometryInstance3D
##    below each LOD node, so only one LOD is drawn at a time.
##  * Adds the optional imported night lights to the "roadside_store_night_lights" group so the
##    game can toggle them (e.g. get_tree().call_group(...)) or remove them.
##
## NOTE: written for Godot 4.x; it has NOT been run inside Godot by the author of these assets.

const DEFAULT_RANGES := {
	0: Vector2(0.0, 60.0),
	1: Vector2(60.0, 170.0),
	2: Vector2(170.0, 900.0),
}
const DEFAULT_MARGIN := 6.0
const NIGHT_LIGHT_GROUP := "roadside_store_night_lights"

var _lod_re := RegEx.new()


func _post_import(scene: Node) -> Object:
	_lod_re.compile("_LOD(\\d)$")
	_walk(scene, -1, Vector2.ZERO, DEFAULT_MARGIN)
	return scene


func _walk(node: Node, lod: int, rng: Vector2, margin: float) -> void:
	var info: Array = _lod_info(node)
	if info.size() == 3:
		lod = info[0]
		rng = info[1]
		margin = info[2]
	if lod >= 0 and node is GeometryInstance3D:
		var gi := node as GeometryInstance3D
		gi.visibility_range_begin = rng.x
		gi.visibility_range_end = rng.y
		gi.visibility_range_begin_margin = margin if rng.x > 0.0 else 0.0
		gi.visibility_range_end_margin = margin
		gi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if node is Light3D:
		node.add_to_group(NIGHT_LIGHT_GROUP, true)
	for child in node.get_children():
		_walk(child, lod, rng, margin)


func _lod_info(node: Node) -> Array:
	if node.has_meta("extras"):
		var extras = node.get_meta("extras")
		if extras is Dictionary and extras.has("lod_level"):
			var l: int = int(extras["lod_level"])
			var fallback: Vector2 = DEFAULT_RANGES.get(l, Vector2(0.0, 0.0))
			var b: float = float(extras.get("visibility_range_begin", fallback.x))
			var e: float = float(extras.get("visibility_range_end", fallback.y))
			var m: float = float(extras.get("visibility_range_margin", DEFAULT_MARGIN))
			return [l, Vector2(b, e), m]
	var match_result := _lod_re.search(String(node.name))
	if match_result:
		var l2: int = int(match_result.get_string(1))
		if DEFAULT_RANGES.has(l2):
			return [l2, DEFAULT_RANGES[l2], DEFAULT_MARGIN]
	return []
