import inkex
import math
from inkex import PathElement, Circle, Rectangle, Marker

class FeynmanLogic(inkex.EffectExtension):
    # ... (patterns et add_arguments identiques) ...
    patterns = {
        "photon": {"d": "m 0,0 c 5,-10 10,10 15,0", "normal_offset": 0},
        "gluon": {
            "d": "m 136.21414,149.28102 c 1.74575,0 3.48637,-0.35809 4.92564,-0.9913 1.43978,-0.63322 2.56945,-1.53971 3.23396,-2.51027 0.66399,-0.97151 0.85872,-2.00049 0.64082,-2.85517 -0.2179,-0.85371 -0.84532,-1.52555 -1.63863,-1.86289 -0.7938,-0.33734 -1.74525,-0.33639 -2.53956,0 -0.7938,0.33734 -1.4202,1.00918 -1.63862,1.86289 -0.21892,0.85468 -0.0226,1.88366 0.64083,2.85517 0.66348,0.97151 1.79417,1.87609 3.23342,2.51027 1.43928,0.63415 3.17989,0.9913 4.92565,0.9913",
            "normal_offset": -4.23
        },
        '''
        "boson": {
            "d": "m 319.09978,117.07641 c 0.10515,-0.008 0.21031,-0.008 0.31551,-2e-5 0.21025,0.0157 0.4205,0.063 0.6309,0.14114 0.21024,0.0779 0.42049,0.18705 0.63089,0.32544 0.21025,0.13839 0.4205,0.30637 0.6309,0.50168 0.21025,0.19513 0.42064,0.41775 0.6309,0.66462 0.21025,0.24687 0.42064,0.51832 0.63089,0.81046 0.21026,0.2923 0.42065,0.60546 0.6309,0.93543 0.21025,0.32997 0.42065,0.67692 0.6309,1.03599 0.21025,0.35924 0.42065,0.73076 0.6309,1.10988 0.21025,0.37912 0.42064,0.76584 0.6309,1.15498 0.21039,0.38915 0.42064,0.78088 0.6309,1.17002 0.21039,0.38914 0.42064,0.77586 0.63089,1.15498 0.2104,0.37897 0.42065,0.75049 0.6309,1.10973 0.21039,0.35923 0.42064,0.70602 0.6309,1.03615 0.21039,0.32997 0.42064,0.64313 0.63089,0.93527 0.2104,0.2923 0.42065,0.56359 0.63105,0.81062 0.21025,0.24687 0.4205,0.46933 0.63089,0.66463 0.21026,0.19531 0.42051,0.36312 0.6309,0.50167 0.21025,0.13839 0.4205,0.24736 0.6309,0.32545 0.21025,0.0781 0.4205,0.12529 0.6309,0.14113 0.21025,0.0157 0.4205,-1.6e-4 0.63089,-0.0472 0.21026,-0.047 0.42065,-0.12546 0.6309,-0.2341 0.21025,-0.10849 0.42065,-0.24752 0.6309,-0.41485 0.21025,-0.16734 0.42065,-0.36328 0.6309,-0.58509 0.21025,-0.22166 0.42065,-0.4695 0.6309,-0.73998 0.21025,-0.27047 0.42064,-0.56358 0.63089,-0.87577 0.2104,-0.31202 0.42065,-0.64313 0.6309,-0.98894 0.21039,-0.34566 0.42065,-0.70603 0.6309,-1.07641 0.21039,-0.3704 0.42065,-0.75066 0.63089,-1.13608 0.2104,-0.38542 0.42065,-0.77586 0.6309,-1.1663 0.21026,-0.39043 0.42065,-0.78086 0.6309,-1.16612 0.21025,-0.38543 0.42065,-0.76585 0.6309,-1.13607 0.21025,-0.37039 0.42065,-0.73076 0.6309,-1.07657 0.21039,-0.34565 0.42065,-0.67676 0.6309,-0.98879 0.21039,-0.31218 0.42064,-0.60546 0.63089,-0.87593 0.2104,-0.27048 0.42065,-0.51816 0.6309,-0.73998 0.21039,-0.2218 0.42065,-0.4176 0.6309,-0.58492 0.21039,-0.1675 0.42065,-0.30637 0.63104,-0.41501 0.21025,-0.10864 0.4205,-0.18689 0.6309,-0.23394 0.10512,-0.0236 0.21025,-0.0393 0.31539,-0.0472",
            "normal_offset": 0
        },
        '''
        "boson": {"d": "m 0,0 c 5,-10 10,10 15,0", "normal_offset": 0},
        "ghost": {"d": "m 0,0 h 10", "normal_offset": 0, "dash": "1, 3"},
        "scalar": {"d": "m 0,0 h 10", "normal_offset": 0, "dash": "5, 5"},
    }
    
    def add_arguments(self, pars):
        pars.add_argument("--tabs", type=str, dest="tab")
        pars.add_argument("--p_type", type=str, default="photon")
        pars.add_argument("--amplitude", type=float, default=5.0)
        pars.add_argument("--v_style", type=str, default="none")
        pars.add_argument("--v_size", type=float, default=3.0)
        pars.add_argument("--v_location", type=str, default="both")
        pars.add_argument("--v_apply_all", type=inkex.Boolean, default=False)
        pars.add_argument("--arrow_type", type=str, default="none")
        pars.add_argument("--momentum_arrow", type=str, default="none")
        pars.add_argument("--momentum_offset", type=float, default=12.0)
        pars.add_argument("--momentum_length", type=float, default=12.0)
        pars.add_argument("--momentum_label", type=str, default="")
        pars.add_argument("--gen_syntax", type=str, default="")
        pars.add_argument("--gen_scale", type=float, default=1.0)
        pars.add_argument("--label_latex", type=inkex.Boolean, default=False)

    def effect(self):
        # 1. Vérification du mode Auto-Draw
        syntax = self.options.gen_syntax.strip()
        if syntax:
            try:
                import pyfeyngen
                # Ici, on appelle ta bibliothèque externe
                data = pyfeyngen.quick_geometry(syntax) 
                self.generate_diagram(data)
                return # On arrête ici pour ne pas traiter la sélection
                
            except Exception as e:
                inkex.errormsg(f"Erreur de génération : {str(e)}")
                return
            
        for elem in self.svg.selection:
            if isinstance(elem, inkex.PathElement):
                # 1. Nettoyage ciblé : on cherche l'ID stocké dans l'attribut
                self.remove_linked_ghost(elem)
                if self.options.p_type != "no_change":
                    # 2. Reset du LPE
                    self.reset_path(elem)
                    # 3. Application visuelle
                    self.apply_particle_lpe(elem)
                self.apply_vertices(elem)
                
                # 4. Création de la flèche
                if self.options.arrow_type != "none":
                    self.options.arrow_type = self.get_arrow_direction(elem, self.options.arrow_type)
                    self.apply_separate_arrow(elem)
                # 5. Flèche de flux (décalée et courte)
                # On suppose que l'option s'appelle "show_momentum"
                if self.options.momentum_arrow != "none" or self.options.momentum_label:

                    self.options.momentum_arrow = self.get_arrow_direction(elem, self.options.momentum_arrow)

                    self.apply_momentum_flow(elem)

    def remove_linked_ghost(self, elem):
        """Supprime le ghost, la flèche de flux et le label associé"""
        for attr in ['data-feynman-ghost', 'data-feynman-ghost-arrow', 'data-feynman-label']:
            ghost_id = elem.get(attr)
            if ghost_id:
                ghost_elem = self.svg.getElementById(ghost_id)
                if ghost_elem is not None:
                    ghost_elem.delete()

    def reset_path(self, elem):
        NS_INK = "http://www.inkscape.org/namespaces/inkscape"
        original_d = elem.attrib.get(f"{{{NS_INK}}}original-d")
        if original_d:
            elem.set("d", original_d)
            if f"{{{NS_INK}}}path-effect" in elem.attrib:
                del elem.attrib[f"{{{NS_INK}}}path-effect"]
            del elem.attrib[f"{{{NS_INK}}}original-d"]

    def apply_separate_arrow(self, elem):
        if self.options.arrow_type == "none": return
            
        # 1. On récupère le chemin avec toutes ses transformations appliquées
        # Cela convertit les coordonnées "locaux + transform" en coordonnées "réelles"
        path_instance = elem.path.transform(elem.composed_transform())
        csp = path_instance.to_superpath()
        
        if len(csp[0]) >= 2:
            p0, h0, h1, p1 = csp[0][0][1], csp[0][0][2], csp[0][-1][0], csp[0][-1][1]
            def lerp(a, b, t=0.5): return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
            m0, m1, m2 = lerp(p0, h0), lerp(h0, h1), lerp(h1, p1)
            q0, q1 = lerp(m0, m1), lerp(m1, m2)
            mid_p = lerp(q0, q1)
            csp[0].insert(1, [q0, mid_p, q1])

        ghost = PathElement()
        new_ghost_id = self.svg.get_unique_id("ghost")
        ghost.set('id', new_ghost_id)
        #ghost.set('sodipodi:insensitive', 'true')
        ghost.set('d', str(inkex.Path(inkex.CubicSuperPath(csp))))
        
        # IMPORTANT : On ne copie PAS le transform du parent ici car 
        # .transform(elem.composed_transform()) a déjà "aplati" les coordonnées.
        # Le ghost est donc déjà aux bonnes coordonnées mondiales.
        
        elem.set('data-feynman-ghost', new_ghost_id)
        
        marker_id = self.ensure_arrow_marker()
        ghost.style = {
            'fill': 'none',
            'stroke': elem.style.get('stroke', 'black'),
            'stroke-width': '0.1',
            'stroke-opacity': '0',
            'marker-mid': f"url(#{marker_id})",
            'pointer-events': 'none'
        }
        
        # On ajoute le ghost à la racine du calque actuel pour éviter les doubles transformations
        elem.getparent().add(ghost)

    def apply_particle_lpe(self, elem):
        p_type = self.options.p_type
        if p_type == "fermion": return
        NS_INK = "http://www.inkscape.org/namespaces/inkscape"
        pattern_info = self.patterns.get(p_type, {"d": "m 0,0 h 10", "normal_offset": 0}) 
        pattern_id = self.ensure_pattern(p_type)
        lpe_id = self.svg.get_unique_id("lpe")
        lpe_node = inkex.etree.SubElement(self.svg.defs, f"{{{NS_INK}}}path-effect")
        lpe_node.set('id', lpe_id)
        lpe_node.set('effect', 'skeletal')
        lpe_node.set('pattern', '#' + pattern_id)
        lpe_node.set('copytype', 'repeated_stretched')
        lpe_node.set('width', str(self.options.amplitude))
        lpe_node.set('normal_offset', str(pattern_info["normal_offset"]))
        lpe_node.set('is_fittopath', 'true')
        lpe_node.set('is_upper_case', 'true')

        # --- GESTION DES POINTILLÉS / TIRETS ---
        if "dash" in pattern_info:
            elem.style['stroke-dasharray'] = pattern_info["dash"]
        else:
            elem.style['stroke-dasharray'] = 'none'
        # ---------------------------------------

        if p_type in ["scalar", "ghost", "fermion"]:
            # Pour ces types, on ne met pas de LPE, juste le style de ligne
            elem.attrib[f"{{{NS_INK}}}original-d"] = elem.get("d")
            return
        
        elem.attrib[f"{{{NS_INK}}}original-d"] = elem.get("d")
        elem.set(f"{{{NS_INK}}}path-effect", "#" + lpe_id)

    def apply_vertices(self, elem):
        v_style, v_loc = self.options.v_style, self.options.v_location
        elem.style['marker-start'] = elem.style['marker-end'] = elem.style['marker-mid'] = 'none'
        if v_style == "none": return
        marker_url = f"url(#{self.ensure_vertex_marker(v_style)})"
        
        start, end = self.get_start_end_from_elem(elem)
        x1, y1 = start
        # 3. Le point d'arrivée (end) est la coordonnée de la dernière commande du tracé
        x2, y2 = end
        
        if v_loc == "both": elem.style['marker-start'] = elem.style['marker-end'] = marker_url
        elif v_loc == "start": elem.style['marker-start'] = marker_url
        elif v_loc == "end": elem.style['marker-end'] = marker_url
        elif v_loc == "left": elem.style['marker-start' if x1 < x2 else 'marker-end'] = marker_url
        elif v_loc == "right": elem.style['marker-start' if x1 > x2 else 'marker-end'] = marker_url
        elif v_loc == "up": elem.style['marker-start' if y1 < y2 else 'marker-end'] = marker_url
        elif v_loc == "down": elem.style['marker-start' if y1 > y2 else 'marker-end'] = marker_url

    def ensure_pattern(self, p_type):
        p_id = f"fref_{p_type}"
        if self.svg.getElementById(p_id) is not None: return p_id
        info = self.patterns.get(p_type, {"d": "m 0,0 h 10"})
        new_p = PathElement()
        new_p.set('d', info["d"]); new_p.set('id', p_id)
        new_p.style = {'stroke': 'black', 'stroke-width': '1', 'fill': 'none'}
        self.svg.defs.add(new_p); return p_id

    def ensure_vertex_marker(self, v_style):
        m_id = f"fmarker_{v_style}_{self.options.v_size}"
        if self.svg.getElementById(m_id) is not None: return m_id
        size = self.options.v_size
        marker = Marker()
        marker.set('id', m_id); marker.set('orient', 'auto'); marker.set('markerUnits', 'userSpaceOnUse')
        if v_style in ["dot", "blob"]:
            r = size if v_style == "dot" else size * 2.5
            shape = Circle(cx="0", cy="0", r=str(r))
        else:
            shape = Rectangle(x=str(-size), y=str(-size), width=str(size*2), height=str(size*2))
        shape.style = {'fill': 'context-stroke', 'stroke': 'none'}
        marker.add(shape); self.svg.defs.add(marker); return m_id

    def ensure_arrow_marker(self, momentum = False):
        if momentum:
            type = 'forward'
            m_id = f"farrow_momentum_{self.options.momentum_arrow}"
        else:
            type = self.options.arrow_type
            m_id = f"farrow_{self.options.arrow_type}"

        if self.svg.getElementById(m_id) is not None: return m_id
        marker = Marker()
        marker.set('id', m_id); marker.set('orient', 'auto')
        marker.set('refX', '5'); marker.set('refY', '4')
        marker.set('markerWidth', '10'); marker.set('markerHeight', '8'); marker.set('markerUnits', 'userSpaceOnUse')
        d = "M 0,0 L 10,4 L 0,8 L 2,4 Z" if type == "forward" else "M 10,0 L 0,4 L 10,8 L 8,4 Z"
        arrow = PathElement(); arrow.set('d', d)
        arrow.style = {'fill': 'context-stroke', 'stroke': 'none'}
        marker.add(arrow); self.svg.defs.add(marker); return m_id

    def apply_momentum_flow(self, elem):
        # 1. Calcul de la géométrie de base (nécessaire pour la flèche ET le label)
        path_instance = elem.path.transform(elem.composed_transform())
        csp = path_instance.to_superpath()
        if len(csp[0]) < 2: return

        p0, c0, c1, p1 = csp[0][0][1], csp[0][0][2], csp[0][-1][0], csp[0][-1][1]
        def lerp(a, b, t=0.5): return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
        m1, m2, m3 = lerp(p0, c0), lerp(c0, c1), lerp(c1, p1)
        q1, q2 = lerp(m1, m2), lerp(m2, m3)
        mid_p = lerp(q1, q2)

        tx, ty = q2[0] - q1[0], q2[1] - q1[1]
        t_len = (tx**2 + ty**2)**0.5
        if t_len == 0: return
        ux, uy = tx/t_len, ty/t_len
        nx, ny = -uy, ux 

        # 2. AFFICHAGE DE LA FLÈCHE (si activée)
        if self.options.momentum_arrow != "none":
            a_len, offset = self.options.momentum_length, self.options.momentum_offset
            ax, ay = mid_p[0] + (nx * offset) - (ux * a_len/2), mid_p[1] + (ny * offset) - (uy * a_len/2)
            bx, by = mid_p[0] + (nx * offset) + (ux * a_len/2), mid_p[1] + (ny * offset) + (uy * a_len/2)

            flow_ghost = PathElement()
            fid = self.svg.get_unique_id("flow")
            flow_ghost.set('id', fid)
            
            if self.options.momentum_arrow == "forward":
                flow_ghost.set('d', f"M {ax},{ay} L {bx},{by}")
            else:
                flow_ghost.set('d', f"M {bx},{by} L {ax},{ay}")

            mid = self.ensure_arrow_marker(momentum=True)
            flow_ghost.style = {
                'fill': 'none', 
                'stroke': elem.style.get('stroke', 'black'), 
                'stroke-width': '0.7', 
                'marker-end': f"url(#{mid})",
                'pointer-events': 'none'
            }
            elem.addnext(flow_ghost)
            elem.set('data-feynman-ghost-arrow', fid)

        # 3. AFFICHAGE DU LABEL (Indépendant de la flèche)
        if self.options.momentum_label:
            label = inkex.TextElement()
            lid = self.svg.get_unique_id("label")
            label.set('id', lid)
            
            # Calcul de l'angle pour l'orientation
            angle = math.degrees(math.atan2(ty, tx))
            if angle > 90: angle -= 180
            if angle < -90: angle += 180
            
            # Si la flèche n'est pas là, on réduit peut-être un peu l'offset 
            # pour que le texte soit plus proche du propagateur
            current_offset = self.options.momentum_offset
            text_margin = 8 if self.options.momentum_arrow != "none" else 5
            t_off = current_offset + (text_margin if current_offset >= 0 else -text_margin)
            
            lx, ly = mid_p[0] + (nx * t_off), mid_p[1] + (ny * t_off)
            
            label.set('transform', f"translate({lx},{ly}) rotate({angle})")
            if self.options.label_latex:
                label.text = '$'+ self.options.momentum_label + '$'
            else:
                label.text = self.options.momentum_label
            label.style = {
                'font-size': '10px', 
                'text-anchor': 'middle', 
                'dominant-baseline': 'middle', 
                'fill': elem.style.get('stroke', 'black'),
                'font-family': 'sans-serif'
            }
            elem.addnext(label)
            elem.set('data-feynman-label', lid)
    
    def get_arrow_direction(self, elem, orientation):
        """
        Détermine si le marqueur doit être 'forward' (A->B) ou 'backward' (B->A)
        en fonction de l'orientation souhaitée.
        """
        if (orientation == "forward") or (orientation == "backward"):
            return orientation
        
        

        # 2. Le point de départ (start) est toujours la coordonnée de la 1ère commande (Move)
        # path[0] est la commande 'M', .end est son point de destination
        start, end = self.get_start_end_from_elem(elem)

        x1, y1 = start
        
        # 3. Le point d'arrivée (end) est la coordonnée de la dernière commande du tracé
        x2, y2 = end

        eps = 0.001 # Tolérance pour les arrondis
        
        if orientation == "right":
            # On veut que la pointe soit à droite. 
            # Si x2 (fin) est à droite de x1 (début), c'est forward.
            return "forward" if x2 > x1 + eps else "backward"
            
        elif orientation == "left":
            # On veut que la pointe soit à gauche.
            return "forward" if x2 < x1 - eps else "backward"
            
        elif orientation == "up":
            # Inkscape Y+ est vers le bas. "Haut" signifie Y décroissant.
            # Si y2 est plus petit que y1, on monte bien : forward.
            return "forward" if y2 < y1 - eps else "backward"
            
        elif orientation == "down":
            # "Bas" signifie Y croissant.
            return "forward" if y2 > y1 + eps else "backward"
        
        return "forward"

    def generate_diagram(self, data):
        """
        Génère le diagramme à partir des données pyfeyngen.
        Utilise des markers pour les sommets avec une logique anti-doublon.
        """
        layer = self.svg.get_current_layer()
        scale = 1.0  
        offset_x, offset_y = 50, 50 

        # Suivi des nœuds déjà marqués pour éviter les superpositions de Blobs
        nodes_already_marked = set()
        # Identification des nœuds qui doivent avoir un style spécial
        special_nodes = {nid for nid, info in data['nodes'].items() if info.get('style') == 'blob'}

        for edge in data['edges']:
            # 1. Calcul des coordonnées mondiales
            x1 = edge['start'][0] * scale + offset_x
            y1 = edge['start'][1] * scale + offset_y
            x2 = edge['end'][0] * scale + offset_x
            y2 = edge['end'][1] * scale + offset_y
            
            # 2. Création du chemin SVG
            path_elem = PathElement()
            
            # Récupération de la courbure envoyée par la bibliothèque
            # On considère que si bend == 0, c'est une ligne droite.
            bend = edge.get('bend', 0.0)
            
            if bend != 0:
                # 1. Calcul du milieu (M)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                
                # 2. Vecteur directeur (V)
                dx, dy = (x2 - x1), (y2 - y1)
                dist = (dx**2 + dy**2)**0.5
                
                if dist > 0.001:
                    # 3. Calcul du point de contrôle (Q)
                    # Le décalage est perpendiculaire : (-dy, dx)
                    # On multiplie par 'bend' pour l'amplitude
                    cx = mx - (dy / dist) * (dist * bend)
                    cy = my + (dx / dist) * (dist * bend)
                    
                    path_elem.set('d', f"M {x1},{y1} Q {cx},{cy} {x2},{y2}")
                else:
                    # Sécurité si les points sont superposés
                    path_elem.set('d', f"M {x1},{y1} L {x2},{y2}")
            else:
                # Ligne droite classique
                path_elem.set('d', f"M {x1},{y1} L {x2},{y2}")
            
            path_elem.style = {'stroke': 'black', 'stroke-width': '1', 'fill': 'none'}
            layer.add(path_elem)
            
            # 3. Sauvegarde et configuration temporaire des options
            original_opts = {
                'p_type': self.options.p_type,
                'momentum_label': self.options.momentum_label,
                'arrow_type': self.options.arrow_type,
                'v_style': self.options.v_style,
                'v_location': self.options.v_location,
                'momentum_arrow': self.options.momentum_arrow
            }
            
            # Configuration selon les données de l'edge
            self.options.p_type = edge['type']
            self.options.momentum_label = edge.get('label', '')
            self.options.momentum_arrow = "none"

            # Gestion de l'orientation de la flèche (Fermions / Anti-particules)
            if edge['type'] == 'fermion':
                self.options.arrow_type = "backward" if edge.get('is_anti', False) else "forward"
            else:
                self.options.arrow_type = "none"

            # --- LOGIQUE ANTI-DOUBLON POUR LES MARKERS ---
            s_node, e_node = edge['start_node'], edge['end_node']
            
            # Un marker n'est posé que si le nœud est un 'blob' ET n'a pas encore été marqué
            start_needs_blob = (s_node in special_nodes and s_node not in nodes_already_marked)
            end_needs_blob = (e_node in special_nodes and e_node not in nodes_already_marked)
            
            if start_needs_blob and end_needs_blob:
                self.options.v_style, self.options.v_location = "blob", "both"
                nodes_already_marked.update([s_node, e_node])
            elif start_needs_blob:
                self.options.v_style, self.options.v_location = "blob", "start"
                nodes_already_marked.add(s_node)
            elif end_needs_blob:
                self.options.v_style, self.options.v_location = "blob", "end"
                nodes_already_marked.add(e_node)
            else:
                self.options.v_style = "none"

            # 4. Application des traitements visuels existants
            self.apply_particle_lpe(path_elem)
            self.apply_vertices(path_elem)
            
            if self.options.arrow_type != "none":
                self.apply_separate_arrow(path_elem)
            
            if self.options.momentum_label:
                self.apply_momentum_flow(path_elem)

            # 5. Restauration des options de l'interface utilisateur
            for key, val in original_opts.items():
                setattr(self.options, key, val)

    def get_start_end_from_elem(self, elem):

        path = elem.path.to_superpath()

        start_raw = path[0][0][1]
        end_raw = path[0][-1][1]

        # On applique la matrice de transformation de l'objet pour avoir les vrais X/Y
        start_pt = elem.transform.apply_to_point(start_raw)
        end_pt = elem.transform.apply_to_point(end_raw)

        x1, y1 = start_pt.x, start_pt.y
        x2, y2 = end_pt.x, end_pt.y
        
        return (x1, y1), (x2, y2)

if __name__ == '__main__':
    FeynmanLogic().run()