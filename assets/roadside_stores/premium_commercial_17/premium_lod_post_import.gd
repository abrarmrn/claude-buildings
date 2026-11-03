@tool
extends EditorScenePostImport

## Post-import script for the Premium Commercial 17 assets (.glb).
## Derived from ../prototypes/roadside_lod_post_import.gd (unchanged original kept in place) - same LOD logic,
## plus groups for the premium node tree.
##
## How to use (per .glb): select the .glb in the FileSystem dock -> Import dock -> "Import Script" -> pick this file
## -> "Reimport".
##
## What it does:
##  * Finds every node whose glTF extras contain "lod_level" (<P>_LOD0/_LOD1/_LOD2 and <P>_PLACEHOLDER_CARS) and applies
##    visibility_range_begin / _end (+ margins) from the extras to every GeometryInstance3D below it.  Falls back to the
##    node-name suffix _LOD<n> with DEFAULT_RANGES.
##  * Lights under <P>_INTERIOR_LIGHTING -> group "premium_interior_lights";
##    lights under <P>_EXTERIOR_LIGHTING -> group "premium_exterior_night_lights" (toggle at dusk).
##  * <P>_PLACEHOLDER_CARS -> group "premium_placeholder_cars" so all generic cars can be freed in one call:
##      get_tree().call_group("premium_placeholder_cars", "queue_free")
##
## NOTE: written for Godot 4.x; it has NOT been run inside Godot by the author of these assets.

const DEFAULT_RANGES := {
	0: Vector2(0.0, 90.0),
	1: Vector2(90.0, 260.0),
	2: Vector2(260.0, 1600.0),
}
const DEFAULT_MARGIN := 8.0
const INTERIOR_GROUP := "premium_interior_lights"
const EXTERIOR_GROUP := "premium_exterior_night_lights"
const CARS_GROUP := "premium_placeholder_cars"

var _lod_re := RegEx.new()


func _post_import(scene: Node) -> Object:
	_lod_re.compile("_LOD(\\d)$")
	_walk(scene, -1, Vector2.ZERO, DEFAULT_MARGIN, "")
	return scene


func _walk(node: Node, lod: int, rng: Vector2, margin: float, light_group: String) -> void:
	var info: Array = _lod_info(node)
	if info.size() == 3:
		lod = info[0]
		rng = info[1]
		margin = info[2]
	var nm := String(node.name)
	if nm.ends_with("_INTERIOR_LIGHTING"):
		light_group = INTERIOR_GROUP
	elif nm.ends_with("_EXTERIOR_LIGHTING"):
		light_group = EXTERIOR_GROUP
	elif nm.ends_with("_PLACEHOLDER_CARS"):
		node.add_to_group(CARS_GROUP, true)
	if lod >= 0 and node is GeometryInstance3D:
		var gi := node as GeometryInstance3D
		gi.visibility_range_begin = rng.x
		gi.visibility_range_end = rng.y
		gi.visibility_range_begin_margin = margin if rng.x > 0.0 else 0.0
		gi.visibility_range_end_margin = margin
		gi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if node is Light3D and light_group != "":
		node.add_to_group(light_group, true)
	for child in node.get_children():
		_walk(child, lod, rng, margin, light_group)


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
