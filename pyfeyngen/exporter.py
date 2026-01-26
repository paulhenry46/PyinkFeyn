from .physics import get_info
def generate_physical_tikz(graph, user_dict=None):
    tikz_lines = []
    vertex_usage = {}
    # Set to track vertices already declared with a style
    styled_vertices = set()

    # 1. PRE-FILTERING AND COUNTING
    path_totals = {}
    valid_edges = []
    for edge in graph.edges:
        src, dst, particle = edge
        if isinstance(particle, str):
            valid_edges.append(edge)
            path_id = tuple(sorted((src, dst)))
            path_totals[path_id] = path_totals.get(path_id, 0) + 1

    path_current_count = {}

    # 2. TIKZ LINE GENERATION
    for src, dst, particle in valid_edges:
        info = get_info(particle, user_dict)
        style = info['style']
        label = info['label']
        path_id = tuple(sorted((src, dst)))
        
        # --- Vertex style management (single injection) ---
        src_attr = ""
        if src in graph.vertex_styles and src not in styled_vertices:
            src_attr = f"[{graph.vertex_styles[src]}]"
            styled_vertices.add(src)
        
        dst_attr = ""
        if dst in graph.vertex_styles and dst not in styled_vertices:
            dst_attr = f"[{graph.vertex_styles[dst]}]"
            styled_vertices.add(dst)
        
        # --- Multi-bending management ---
        bend_style = ""
        total_lines = path_totals[path_id]
        if total_lines > 1:
            idx = path_current_count.get(path_id, 0)
            path_current_count[path_id] = idx + 1
            max_bend = 50 
            step = (max_bend * 2) / (total_lines - 1)
            angle = -max_bend + (step * idx)
            if info['is_anti'] and style == 'fermion': angle = -angle
            if abs(angle) > 0.1:
                side = "left" if angle > 0 else "right"
                bend_style = f"bend {side}={abs(int(angle))}"
        
        # --- Label side management ---
        count_usage = vertex_usage.get(src, 0)
        label_side = "'" if count_usage % 2 != 0 else "" 
        vertex_usage[src] = count_usage + 1
        
        # --- Edge options construction ---
        label_cmd = fr"edge label{label_side}=\({label}\)" if label else ""
        options = [style]
        if bend_style: options.append(bend_style)
        if label_cmd: options.append(label_cmd)
        options_str = ", ".join(options)

        # --- Final assembly (unique vertex[style] syntax) ---
        if info['is_anti'] and style == 'fermion':
            line = fr"  {dst}{dst_attr} -- [{options_str}] {src}{src_attr}"
        else:
            line = fr"  {src}{src_attr} -- [{options_str}] {dst}{dst_attr}"
            
        tikz_lines.append(line)
    
    header = "\\feynmandiagram [horizontal=inx1 to fx1] {"
    footer = "};"
    
    return header + "\n" + ",\n".join(tikz_lines) + "\n" + footer