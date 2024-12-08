import logging
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

Tile = Tuple[str, str]
TileKey = Tuple[Tuple[Tile, ...], Tuple[Tile, ...]]


def serialize_tiles(map_tiles: List[Tile], static_tiles: List[Tile]) -> TileKey:
    """Serialize map and static tiles into a hashable key."""
    sorted_map = tuple(sorted(map_tiles))
    sorted_static = tuple(sorted(static_tiles))
    return sorted_map, sorted_static


def extract_tiles(element: Optional[ET.Element], tile_tag: str) -> List[Tile]:
    """Extract tile data from a given XML element.

    Args:
        element: XML Element containing tile definitions.
        tile_tag: Tag name ('MapTile' or 'StaticTile') to extract.

    Returns:
        A list of (TileID, AltIDMod) tuples.
    """
    if element is not None:
        return [
            (tile.get("TileID", "0"), tile.get("AltIDMod", "0"))
            for tile in element.findall(tile_tag)
        ]
    return []


def write_tile_table(
    content: List[str], tile_counts: Counter[Tile], empty_label: str
) -> None:
    """Write a tile table (map or static) to the content list.

    Args:
        content: List of strings representing lines in the markdown content.
        tile_counts: A Counter of tile occurrences.
        empty_label: A markdown label to use if there are no tiles.
    """
    total = sum(tile_counts.values())
    if total > 0:
        # Create the table header
        content.append("| ID Hex | ID Dec | Alt Mod | Chance |")
        content.append("|:------:|:------:|:--------:|:------:|")
        for (tile_id, alt_id_mod), count in sorted(
            tile_counts.items(), key=lambda x: int(x[0][0])
        ):
            tile_id_hex = _format_tile_id_hex(tile_id)
            chance_str = f"{(count / total) * 100:.0f}%"
            content.append(
                f"| {tile_id_hex} | {tile_id} | {alt_id_mod} | {chance_str} |"
            )
        content.append("")
    else:
        content.append(empty_label)
        content.append("")


def _format_tile_id_hex(tile_id: str) -> str:
    """Format a tile ID into a hexadecimal string."""
    try:
        return f"0x{int(tile_id):04X}"
    except ValueError:
        return "Invalid ID"


def generate_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file."""
    filename = xml_path.stem
    if "_To_" not in filename:
        generate_index_markdown_from_xml(xml_path, output_dir)
    else:
        generate_transition_markdown_from_xml(xml_path, output_dir)


def generate_index_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file for the index."""
    filename = xml_path.stem
    source = filename.replace("_", " ")

    if "-" not in source:
        logging.debug(f"Skipping '{xml_path}': Missing '-' in source part.")
        return
    source_prefix, source_name = source.split("-", 1)

    md_dir = output_dir / source_name
    md_dir.mkdir(parents=True, exist_ok=True)
    md_path = md_dir / "index.md"

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        logging.error(f"Error parsing '{xml_path}': {e}")
        return

    root_xml = tree.getroot()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    front_matter = f"""---
title: {source_name}
parent: Transitions
layout: home
nav_order: {source_prefix}
---

# {source_name}

_Generated on {timestamp}_
"""

    groups: Dict[TileKey, List[str]] = defaultdict(list)

    # Group TransInfo elements by their (map_tiles, static_tiles) combination
    for trans_info in root_xml.findall("TransInfo"):
        description = trans_info.get("Description", "Unknown")
        map_tiles_element = trans_info.find("MapTiles")
        static_tiles_element = trans_info.find("StaticTiles")

        map_tiles = extract_tiles(map_tiles_element, "MapTile")
        static_tiles = extract_tiles(static_tiles_element, "StaticTile")

        group_key = serialize_tiles(map_tiles, static_tiles)
        groups[group_key].append(description)

    content = [front_matter]

    for group_key, _ in groups.items():
        map_tiles_group, static_tiles_group = group_key

        content.append("## Tiles")
        content.append("")

        write_tile_table(
            content,
            Counter(map_tiles_group),
            "| _No MapTiles_ | _N/A_ | _N/A_ | _N/A_ |",
        )

        content.append("## Statics")
        content.append("")

        write_tile_table(content, Counter(static_tiles_group), "_None_")

    try:
        md_path.write_text("\n".join(content), encoding="utf-8")
        logging.info(f"Generated '{md_path}'")
    except IOError as e:
        logging.error(f"Error writing to '{md_path}': {e}")


def generate_transition_markdown_from_xml(xml_path: Path, output_dir: Path) -> None:
    """Parse an XML file and generate a corresponding Markdown file for a transition."""
    filename = xml_path.stem
    source_part, target_part = filename.split("_To_", 1)
    source = source_part.replace("_", " ")
    target = target_part.replace("_", " ")

    if "-" not in source:
        logging.debug(f"Skipping '{xml_path}': Missing '-' in source part.")
        return
    _, source_name = source.split("-", 1)

    if "-" not in target:
        logging.debug(f"Skipping '{xml_path}': Missing '-' in target part.")
        return
    target_prefix, target_name = target.split("-", 1)

    md_dir = output_dir / source_name
    md_dir.mkdir(parents=True, exist_ok=True)
    md_path = md_dir / f"{target_name}.md"

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        logging.error(f"Error parsing '{xml_path}': {e}")
        return

    root_xml = tree.getroot()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    front_matter = f"""---
title: {target_name}
parent: {source_name}
layout: home
nav_order: {target_prefix}
---

# {source_name} to {target_name}

_Generated on {timestamp}_
"""

    groups: Dict[TileKey, List[str]] = defaultdict(list)

    # Group TransInfo elements by their (map_tiles, static_tiles) combination
    for trans_info in root_xml.findall("TransInfo"):
        description = trans_info.get("Description", "Unknown")
        map_tiles_element = trans_info.find("MapTiles")
        static_tiles_element = trans_info.find("StaticTiles")

        map_tiles = extract_tiles(map_tiles_element, "MapTile")
        static_tiles = extract_tiles(static_tiles_element, "StaticTile")

        group_key = serialize_tiles(map_tiles, static_tiles)
        groups[group_key].append(description)

    content = [front_matter]

    for group_key, descriptions in groups.items():
        map_tiles_group, static_tiles_group = group_key

        # Just get all unique descriptions and join them by comma
        unique_descriptions = list(dict.fromkeys(descriptions))
        description_str = ", ".join(unique_descriptions)

        section_title = f"## {description_str}"
        content.append(section_title)
        content.append("")
        content.append("### Tiles")
        content.append("")

        write_tile_table(
            content,
            Counter(map_tiles_group),
            "| _No MapTiles_ | _N/A_ | _N/A_ | _N/A_ |",
        )

        content.append("### Statics")
        content.append("")
        write_tile_table(content, Counter(static_tiles_group), "_None_")

    try:
        md_path.write_text("\n".join(content), encoding="utf-8")
        logging.info(f"Generated '{md_path}'")
    except IOError as e:
        logging.error(f"Error writing to '{md_path}': {e}")


def traverse_and_generate(input_base: Path, output_base: Path) -> None:
    """Traverse the input directory to find XML files and generate Markdown documentation."""
    for root, _, files in os.walk(input_base):
        for file in files:
            if file.lower().endswith(".xml"):
                xml_path = Path(root) / file
                generate_markdown_from_xml(xml_path, output_base)


def main() -> None:
    """Entry point of the script."""
    input_dir = Path("../../data/transitions")
    output_dir = Path("../transitions")

    if not input_dir.exists():
        logging.error(f"Input directory '{input_dir}' does not exist.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    traverse_and_generate(input_dir, output_dir)
    logging.info("Documentation generation completed.")


if __name__ == "__main__":
    main()
