# src/renderers/mindmap_render.py
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

def render_mindmap(root: str, branches: dict, out_path="mindmap.png") -> str:
    """
    branches = {
        "Inputs": ["CO2", "Water"],
        "Process": ["Light reaction", "Calvin cycle"]
    }
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    G = nx.DiGraph()
    G.add_node(root)

    for main, subs in branches.items():
        G.add_edge(root, main)
        for s in subs:
            G.add_edge(main, s)

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=2000, font_size=9, arrows=False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    return str(out_path)
