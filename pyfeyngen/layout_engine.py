class LayeredLayout:
    def __init__(self, graph, x_spacing=150, y_spacing=100):
        self.graph = graph
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.positions = {}

    def _assign_columns(self):
        columns = {}
        # 1. On identifie TOUS les nœuds présents dans les arêtes pour ne rien oublier
        all_nodes = set(self.graph.nodes)
        all_targets = set()
        for e in self.graph.edges:
            all_nodes.add(e[0])
            all_nodes.add(e[1])
            all_targets.add(e[1])

        # 2. Les sources sont les nœuds qui ne sont jamais des cibles
        sources = [n for n in all_nodes if n not in all_targets]
        
        # Si pas de sources (graphe circulaire), on prend le premier nœud
        if not sources and all_nodes:
            sources = [list(all_nodes)[0]]

        queue = [(n, 0) for n in sources]
        while queue:
            node_id, col = queue.pop(0)
            columns[node_id] = max(columns.get(node_id, 0), col)
            
            # Enfants
            children = [e[1] for e in self.graph.edges if e[0] == node_id]
            for child in children:
                # Éviter les boucles infinies au cas où
                if columns.get(child, -1) < col + 1:
                    queue.append((child, col + 1))
        
        # 3. Sécurité : on assigne la col 0 à tout nœud restant
        for node_id in all_nodes:
            if node_id not in columns:
                columns[node_id] = 0
        return columns

    def compute_layout(self):
        columns_map = self._assign_columns()
        layers = {}
        for node_id, col in columns_map.items():
            layers.setdefault(col, []).append(node_id)

        if not layers: return {}

        max_nodes = max(len(nodes) for nodes in layers.values())
        total_height = max_nodes * self.y_spacing

        for col, nodes in layers.items():
            x = col * self.x_spacing
            col_height = len(nodes) * self.y_spacing
            start_y = (total_height - col_height) / 2
            
            for i, node_id in enumerate(nodes):
                y = start_y + (i * self.y_spacing)
                self.positions[node_id] = (x, y)
        
        return self.positions

    def get_inkscape_data(self):
        if not self.positions:
            self.compute_layout()

        # 1. Enrichissement des nœuds (inchangé)
        node_data = {}
        for node_id, pos in self.positions.items():
            v_style = getattr(self.graph, 'vertex_styles', {}).get(node_id, "default")
            node_data[node_id] = {
                "x": pos[0],
                "y": pos[1],
                "style": v_style
            }

        # 2. Comptage pour la répartition des courbes
        edge_counts = {}
        for e in self.graph.edges:
            pair = tuple(sorted((e[0], e[1])))
            edge_counts[pair] = edge_counts.get(pair, 0) + 1

        processed_pairs = {}
        geometry_edges = []
        from .physics import get_info

        for src, dst, particle_name in self.graph.edges:
            pair = tuple(sorted((src, dst)))
            # On suit l'index de l'arête actuelle pour cette paire (1, 2, 3...)
            current_idx = processed_pairs.get(pair, 0) + 1
            processed_pairs[pair] = current_idx
            
            info = get_info(particle_name)
            total_edges = edge_counts[pair]
            
            is_curved = total_edges > 1
            bend_value = 0.0
            
            if is_curved:
                # Écartement entre les courbes (ajustable selon tes préférences)
                step = 0.4 
                # On centre les valeurs autour de 0
                # Ex pour 2 edges: 1 -> -0.2, 2 -> 0.2
                # Ex pour 3 edges: 1 -> -0.4, 2 -> 0, 3 -> 0.4
                bend_value = (current_idx - (total_edges + 1) / 2) * step

            geometry_edges.append({
                "start_node": src,
                "end_node": dst,
                "start": self.positions[src],
                "end": self.positions[dst],
                "type": info.get('style', 'fermion'),
                "label": info.get('label', particle_name),
                "is_anti": info.get('is_anti', False),
                "is_curved": is_curved,
                "bend": round(bend_value, 2) # On remplace bend_direction par bend
            })

        return {"nodes": node_data, "edges": geometry_edges}