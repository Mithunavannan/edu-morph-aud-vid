# src/renderers/flowchart_render.py
from graphviz import Digraph
from pathlib import Path

def render_simple_flowchart(steps: list[str], out_path="flowchart.png") -> str:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dot = Digraph(format="png")
    dot.attr(rankdir="TB")

    prev = None
    for i, s in enumerate(steps, 1):
        node_id = f"N{i}"
        dot.node(node_id, s[:60])
        if prev:
            dot.edge(prev, node_id)
        prev = node_id

    # graphviz render writes without extension sometimes
    file_base = out_path.with_suffix("")
    dot.render(str(file_base), cleanup=True)
    final_path = str(file_base) + ".png"
    return final_path
