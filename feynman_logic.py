import math
import inkex
from inkex import PathElement, Circle, Rectangle, Marker

class FeynmanLogic(inkex.EffectExtension):
    #Helpers functions
    def lerp(self, a, b, t=0.5):
        '''Linear interpolation function for points'''
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]

    def casteljau_midpoint(self, p0, c0, c1, p1):
        """Compute the midpoint (t=0.5) of a cubic Bezier curve using De Casteljau's algorithm."""
        m1 = self.lerp(p0, c0)
        m2 = self.lerp(c0, c1)
        m3 = self.lerp(c1, p1)
        q1 = self.lerp(m1, m2)
        q2 = self.lerp(m2, m3)
        mid_p = self.lerp(q1, q2)
        return q1, mid_p, q2

    patterns = {
        "photon": {"d": "m 0,0 c 5,-10 10,10 15,0", "normal_offset": 0},
        "gluon": {
            "d": "m 136.21414,149.28102 c 1.74575,0 3.48637,-0.35809 4.92564,-0.9913 1.43978,-0.63322 2.56945,-1.53971 3.23396,-2.51027 0.66399,-0.97151 0.85872,-2.00049 0.64082,-2.85517 -0.2179,-0.85371 -0.84532,-1.52555 -1.63863,-1.86289 -0.7938,-0.33734 -1.74525,-0.33639 -2.53956,0 -0.7938,0.33734 -1.4202,1.00918 -1.63862,1.86289 -0.21892,0.85468 -0.0226,1.88366 0.64083,2.85517 0.66348,0.97151 1.79417,1.87609 3.23342,2.51027 1.43928,0.63415 3.17989,0.9913 4.92565,0.9913",
            "normal_offset": -4.23
        },
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
        pars.add_argument("--quiet_error", type=inkex.Boolean, default=False)
        pars.add_argument("--gen_x_spacing", type=int, default=150)
        pars.add_argument("--gen_y_spacing", type=int, default=100)

    def effect(self):
        """Main entry point for the extension. Handles both auto-draw and manual selection modes."""
        syntax = self.options.gen_syntax.strip()
        if syntax:
            try:
                import pyfeyngen
                data = pyfeyngen.quick_geometry(syntax, self.options.gen_x_spacing, self.options.gen_y_spacing)
                self.generate_diagram(data)
                return

            except Exception as e:
                if self.options.quiet_error:
                    label = inkex.TextElement()
                    lid = self.svg.get_unique_id("label")
                    label.set('id', lid)
                    label.text = f"Error : {str(e)}"
                    label.set('x', '50')
                    label.set('y', '50')
                    label.style = {
                        'font-size': '12px',
                        'fill': 'red',
                        'text-anchor': 'middle',
                        'dominant-baseline': 'middle',
                        'font-family': 'sans-serif'
                    }
                    self.svg.get_current_layer().add(label)
                else:
                    inkex.errormsg(f"Error/Warning when generating : {str(e)}")
                return
        direction_save = self.options.arrow_type
        direction_momentum_save = self.options.momentum_arrow
        for elem in self.svg.selection:
            self.options.arrow_type = direction_save
            self.options.momentum_arrow = direction_momentum_save
            if isinstance(elem, inkex.PathElement):
                self.remove_linked_ghost(elem)
                if self.options.p_type != "no_change":
                    self.reset_path(elem)
                    self.apply_particle_lpe(elem)
                self.apply_vertices(elem)

                if self.options.arrow_type != "none":
                    self.options.arrow_type = self.get_arrow_direction(elem, self.options.arrow_type)
                    self.apply_separate_arrow(elem)

                if self.options.momentum_arrow != "none" or self.options.momentum_label:
                    self.options.momentum_arrow = self.get_arrow_direction(elem, self.options.momentum_arrow)
                    self.apply_momentum_flow(elem)

    def remove_linked_ghost(self,  elem:inkex.PathElement):
        """Remove ghost, momemtum arrow and label"""
        for attr in ['data-feynman-ghost', 'data-feynman-ghost-arrow', 'data-feynman-label']:
            ghost_id = elem.get(attr)
            if ghost_id:
                ghost_elem = self.svg.getElementById(ghost_id)
                if ghost_elem is not None:
                    ghost_elem.delete()

    def reset_path(self, elem:inkex.PathElement):
        """Reset the path element to its original path data and remove any applied path effects."""
        NS_INK = "http://www.inkscape.org/namespaces/inkscape"
        original_d = elem.attrib.get(f"{{{NS_INK}}}original-d")
        if original_d:
            elem.set("d", original_d)
            if f"{{{NS_INK}}}path-effect" in elem.attrib:
                del elem.attrib[f"{{{NS_INK}}}path-effect"]
            del elem.attrib[f"{{{NS_INK}}}original-d"]

    def apply_separate_arrow(self, elem:inkex.PathElement):
        """Apply a separate arrow marker to the path element by adding a new path"""
        if self.options.arrow_type == "none":
            return

        path_instance = elem.path.transform(elem.composed_transform())
        csp = path_instance.to_superpath()

        if len(csp[0]) >= 2:
            # Extract the four key points of the cubic Bezier: start, first control, second control, end
            p0, h0, h1, p1 = csp[0][0][1], csp[0][0][2], csp[0][-1][0], csp[0][-1][1]
            # Use De Casteljau's algorithm to find the midpoint and control points
            q0, mid_p, q1 = self.casteljau_midpoint(p0, h0, h1, p1)
            # Insert a new segment at the midpoint to allow for a separate arrow marker
            csp[0].insert(1, [q0, mid_p, q1])

        ghost = PathElement()
        new_ghost_id = self.svg.get_unique_id("ghost")
        ghost.set('id', new_ghost_id)
        ghost.set('d', str(inkex.Path(inkex.CubicSuperPath(csp))))
        
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

        elem.getparent().add(ghost)

    def apply_particle_lpe(self, elem:inkex.PathElement):
        """Apply the appropriate Live Path Effect (LPE) or 
            style to the path element based on particle type."""
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

        # --- DASHED/DOTTED LINE MANAGEMENT ---
        if "dash" in pattern_info:
            elem.style['stroke-dasharray'] = pattern_info["dash"]
        else:
            elem.style['stroke-dasharray'] = 'none'
        # ---------------------------------------

        if p_type in ["scalar", "ghost", "fermion"]:
            # For these types, do not apply LPE, just set the line style
            elem.attrib[f"{{{NS_INK}}}original-d"] = elem.get("d")
            return

        elem.attrib[f"{{{NS_INK}}}original-d"] = elem.get("d")
        elem.set(f"{{{NS_INK}}}path-effect", "#" + lpe_id)

    def apply_vertices(self, elem:inkex.PathElement):
        """Apply vertex markers to the path element based on the selected style and location."""
        v_style, v_loc = self.options.v_style, self.options.v_location
        elem.style['marker-start'] = elem.style['marker-end'] = elem.style['marker-mid'] = 'none'
        if v_style == "none": return
        marker_url = f"url(#{self.ensure_vertex_marker(v_style)})"

        start, end = self.get_start_end_from_elem(elem)
        x1, y1 = start
        x2, y2 = end

        if v_loc == "both": elem.style['marker-start'] = elem.style['marker-end'] = marker_url
        elif v_loc == "start": elem.style['marker-start'] = marker_url
        elif v_loc == "end": elem.style['marker-end'] = marker_url
        elif v_loc == "left": elem.style['marker-start' if x1 < x2 else 'marker-end'] = marker_url
        elif v_loc == "right": elem.style['marker-start' if x1 > x2 else 'marker-end'] = marker_url
        elif v_loc == "up": elem.style['marker-start' if y1 < y2 else 'marker-end'] = marker_url
        elif v_loc == "down": elem.style['marker-start' if y1 > y2 else 'marker-end'] = marker_url

    def ensure_pattern(self, p_type : str):
        """Ensure the SVG pattern for the given particle type exists, and return its ID."""
        p_id = f"fref_{p_type}"
        if self.svg.getElementById(p_id) is not None: return p_id
        info = self.patterns.get(p_type, {"d": "m 0,0 h 10"})
        new_p = PathElement()
        new_p.set('d', info["d"]); new_p.set('id', p_id)
        new_p.style = {'stroke': 'black', 'stroke-width': '1', 'fill': 'none'}
        self.svg.defs.add(new_p); return p_id

    def ensure_vertex_marker(self, v_style : str):
        """Ensure the SVG marker for the given vertex style exists, and return its ID."""
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
        """Ensure the SVG marker for the arrow (or momentum arrow) exists, and return its ID."""
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
        marker.set('markerWidth', '10')
        marker.set('markerHeight', '8')
        marker.set('markerUnits', 'userSpaceOnUse')

        d = "M 0,0 L 10,4 L 0,8 L 2,4 Z" if type == "forward" else "M 10,0 L 0,4 L 10,8 L 8,4 Z"

        arrow = PathElement(); arrow.set('d', d)
        arrow.style = {'fill': 'context-stroke', 'stroke': 'none'}
        marker.add(arrow); self.svg.defs.add(marker); return m_id

    def apply_momentum_flow(self, elem:inkex.PathElement):
        """Draw a momentum flow arrow and/or label near the path element."""
        # 1. Compute base geometry (needed for both arrow and label)
        path_instance = elem.path.transform(elem.composed_transform())
        csp = path_instance.to_superpath()
        if len(csp[0]) < 2: return

        # Extract the four key points of the cubic Bezier: start, first control, second control, end
        p0, c0, c1, p1 = csp[0][0][1], csp[0][0][2], csp[0][-1][0], csp[0][-1][1]
        # Use De Casteljau's algorithm to find the midpoint and control points
        q1, mid_p, q2 = self.casteljau_midpoint(p0, c0, c1, p1)

        # Compute the tangent vector at the midpoint
        tx, ty = q2[0] - q1[0], q2[1] - q1[1]
        t_len = (tx**2 + ty**2)**0.5
        if t_len == 0: return  # Avoid division by zero if tangent is degenerate
        ux, uy = tx/t_len, ty/t_len  # Unit tangent vector
        nx, ny = -uy, ux  # Unit normal vector (perpendicular to tangent)

        # 2. DRAW THE ARROW (if enabled)
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

        # 3. DRAW THE LABEL (independent of the arrow)
        if self.options.momentum_label:
            label = inkex.TextElement()
            lid = self.svg.get_unique_id("label")
            label.set('id', lid)

            # Compute angle for label orientation
            angle = math.degrees(math.atan2(ty, tx))
            if angle > 90:
                angle -= 180
            if angle < -90:
                angle += 180

            # If the arrow is not present, reduce the offset
            # so the text is closer to the propagator
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

    def get_arrow_direction(self, elem:inkex.PathElement, orientation : str):
        """
        Determine if the marker should be 'forward' (A->B) or 'backward' (B->A)
        based on the desired orientation and the geometry of the path.
        """
        if orientation in ('forward', 'backward'):
            return orientation

        start, end = self.get_start_end_from_elem(elem)

        x1, y1 = start
        x2, y2 = end

        eps = 0.001 # Tolerance for rounding

        if orientation == "right":
            # We want the arrowhead to be on the right.
            # If x2 (end) is to the right of x1 (start), it's forward.
            return "forward" if x2 > x1 + eps else "backward"

        elif orientation == "left":
            # We want the arrowhead to be on the left.
            return "forward" if x2 < x1 - eps else "backward"

        elif orientation == "up":
            # Inkscape Y+ is downward. "Up" means decreasing Y.
            # If y2 is less than y1, we are going up: forward.
            return "forward" if y2 < y1 - eps else "backward"

        elif orientation == "down":
            # "Down" means increasing Y.
            return "forward" if y2 > y1 + eps else "backward"

        return "forward"

    def generate_diagram(self, data):
        """ Generate the diagram from pyfeyngen data.
            Uses markers for vertices with anti-duplication logic."""
        layer = self.svg.get_current_layer()
        scale = 1.0
        offset_x, offset_y = 50, 50

        # Track already marked nodes to avoid overlapping blobs
        nodes_already_marked = set()
        # Identify nodes that should have a special style
        special_nodes = {nid for nid, info in data['nodes'].items() if info.get('style') == 'blob'}

        for edge in data['edges']:
            # 1. Compute world coordinates
            x1 = edge['start'][0] * scale + offset_x
            y1 = edge['start'][1] * scale + offset_y
            x2 = edge['end'][0] * scale + offset_x
            y2 = edge['end'][1] * scale + offset_y

            # 2. Create the SVG path
            path_elem = PathElement()

            # Get the curvature sent by the library
            # If bend == 0, it's a straight line.
            bend = edge.get('bend', 0.0)

            if bend != 0:
                # 1. Compute the midpoint (M)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2

                # 2. Direction vector (V)
                dx, dy = (x2 - x1), (y2 - y1)
                dist = (dx**2 + dy**2)**0.5

                if dist > 0.001:
                    # 3. Compute the control point (Q)
                    # The offset is perpendicular: (-dy, dx)
                    # Multiply by 'bend' for amplitude
                    cx = mx - (dy / dist) * (dist * bend)
                    cy = my + (dx / dist) * (dist * bend)

                    path_elem.set('d', f"M {x1},{y1} Q {cx},{cy} {x2},{y2}")
                else:
                    # Safety: if points are overlapping
                    path_elem.set('d', f"M {x1},{y1} L {x2},{y2}")
            else:
                # Standard straight line
                path_elem.set('d', f"M {x1},{y1} L {x2},{y2}")

            path_elem.style = {'stroke': 'black', 'stroke-width': '1', 'fill': 'none'}
            layer.add(path_elem)

            # 3. Save and temporarily set options
            original_opts = {
                'p_type': self.options.p_type,
                'momentum_label': self.options.momentum_label,
                'arrow_type': self.options.arrow_type,
                'v_style': self.options.v_style,
                'v_location': self.options.v_location,
                'momentum_arrow': self.options.momentum_arrow
            }

            # Configure according to edge data
            self.options.p_type = edge['type']
            self.options.momentum_label = edge.get('label', '')
            self.options.momentum_arrow = "none"

            # Handle arrow orientation (Fermions / Anti-particles)
            if edge['type'] == 'fermion':
                self.options.arrow_type = "backward" if edge.get('is_anti', False) else "forward"
            else:
                self.options.arrow_type = "none"

            s_node, e_node = edge['start_node'], edge['end_node']

            # A marker is only placed if the node is a 'blob' AND has not already been marked
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

            # 4. Apply existing visual treatments
            self.apply_particle_lpe(path_elem)
            self.apply_vertices(path_elem)

            if self.options.arrow_type != "none":
                self.apply_separate_arrow(path_elem)

            if self.options.momentum_label:
                self.apply_momentum_flow(path_elem)

            # 5. Restore user interface options
            for key, val in original_opts.items():
                setattr(self.options, key, val)

    def get_start_end_from_elem(self, elem:inkex.PathElement):
        """Return the start and end coordinates of a path element, transformed to document coordinates."""

        path = elem.path.to_superpath()

        start_raw = path[0][0][1]
        end_raw = path[0][-1][1]

        # Apply the object's transformation matrix to get the real X/Y
        start_pt = elem.transform.apply_to_point(start_raw)
        end_pt = elem.transform.apply_to_point(end_raw)

        x1, y1 = start_pt.x, start_pt.y
        x2, y2 = end_pt.x, end_pt.y

        return (x1, y1), (x2, y2)



if __name__ == '__main__':
    FeynmanLogic().run()
