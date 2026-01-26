from .logger import logger

class FeynmanGraph:
    def __init__(self, structure):
        self.nodes = []      
        self.edges = []      
        self.v_count = 0
        self.in_count = 0
        self.f_count = 0
        self.anchor_points = {} 
        self.vertex_styles = {}  # Stores vertex styles (e.g., { "vx1": "blob" })
        
        self.build_graph(structure)

    def new_v(self):
        self.v_count += 1
        return f"vx{self.v_count}"

    def new_in(self):
        self.in_count += 1
        return f"inx{self.in_count}"

    def new_f(self):
        self.f_count += 1
        return f"fx{self.f_count}"

    def build_graph(self, structure):
        first_step = structure[0]
        
        # Extraction adapted to new token types from the parser
        in_particles = [p for p in first_step if isinstance(p, (str, dict)) and 'anchor' not in str(p) and 'loop' not in str(p) and 'cascade' not in str(p)]
        in_anchors = [p for p in first_step if isinstance(p, dict) and 'anchor' in p]
        in_cascades = [p for p in first_step if isinstance(p, (list, dict)) and ('cascade' in str(p) or isinstance(p, list))]

        if in_particles:
            v_start = self.new_v()
            for a in in_anchors:
                self._register_anchor(v_start, a)
            for p in in_particles:
                p_name = p['name'] if isinstance(p, dict) else p
                in_node = self.new_in()
                self.edges.append((in_node, v_start, p_name))
            self._process_steps(v_start, structure[1:])

        elif in_cascades:
            for item in in_cascades:
                cascade = item['cascade'] if isinstance(item, dict) else item
                v_root = self.new_v()
                
                # Handle blob style on the root
                if isinstance(item, dict) and item.get('style') == 'blob':
                    self.vertex_styles[v_root] = 'blob'

                p_start = cascade[0][0]
                p_name = p_start['name'] if isinstance(p_start, dict) else p_start
                
                in_node = self.new_in()
                self.edges.append((in_node, v_root, p_name))
                
                for t in cascade[0]:
                    if isinstance(t, dict) and 'anchor' in t:
                        self._register_anchor(v_root, t)
                self._process_steps(v_root, cascade[1:])
        
        self._connect_anchors()

    def _process_steps(self, current_v, steps):
        if not steps: return
        step = steps[0]

        # 1. Extract ALL token types
        anchors = [item for item in step if isinstance(item, dict) and 'anchor' in item]
        loops = [item for item in step if isinstance(item, dict) and 'loop' in item]
        # Capture anything that can be a particle (str, style dict, or cascade)
        particles = [item for item in step if isinstance(item, (str, list)) or (isinstance(item, dict) and 'anchor' not in item and 'loop' not in item)]

        # 2. Register anchors and detect blob style
        for a in anchors:
            self._register_anchor(current_v, a)
            
        for item in step:
            if isinstance(item, dict) and item.get('style') == 'blob':
                self.vertex_styles[current_v] = 'blob'

        # 3. Handle loops [...] -> Exit after because the loop consumes the step
        if loops:
            loop_data = loops[0]
            v_loop_end = self.new_v()
            if loop_data.get('style') == 'blob': self.vertex_styles[v_loop_end] = 'blob'
            for p in loop_data['loop']:
                self.edges.append((current_v, v_loop_end, p))
            self._process_steps(v_loop_end, steps[1:])
            return

        if not particles:
            self._process_steps(current_v, steps[1:])
            return

        # 4. HANDLE PARTICLES (Outputs or Propagation)
        # If this is the LAST step of the chain or if there are multiple particles
        if len(steps) == 1 or len(particles) > 1:
            for item in particles:
                if isinstance(item, (list, dict)) and ('cascade' in str(item) or isinstance(item, list)):
                    # This is a cascade ( ... )
                    cascade = item['cascade'] if isinstance(item, dict) else item
                    v_branch = self.new_v()
                    if isinstance(item, dict) and item.get('style') == 'blob':
                        self.vertex_styles[v_branch] = 'blob'
                    
                    # Take the bridge particle
                    p_start = cascade[0][0]
                    p_name = p_start['name'] if isinstance(p_start, dict) else p_start
                    self.edges.append((current_v, v_branch, p_name))
                    self._process_steps(v_branch, cascade[1:])
                else:
                    # This is a final particle
                    p_name = item['name'] if isinstance(item, dict) else item
                    f_node = self.new_f()
                    self.edges.append((current_v, f_node, p_name))
        
        # If there is only one particle and there are remaining steps -> Propagation
        else:
            item = particles[0]
            p_name = item['name'] if isinstance(item, dict) else item
            v_next = self.new_v()
            self.edges.append((current_v, v_next, p_name))
            self._process_steps(v_next, steps[1:])

    def _register_anchor(self, vertex, anchor_dict):
        name = anchor_dict['anchor']
        if anchor_dict.get('style') == 'blob':
            self.vertex_styles[vertex] = 'blob'
            
        if name not in self.anchor_points:
            self.anchor_points[name] = []
        self.anchor_points[name].append({
            'vertex': vertex,
            'particle': anchor_dict.get('particle')
        })

    def _connect_anchors(self):
        for name, points in self.anchor_points.items():
            if len(points) >= 2:
                for i in range(len(points) - 1):
                    src = points[i]['vertex']
                    dst = points[i+1]['vertex']
                    p_name = points[i]['particle'] or "gamma"
                    self.edges.append((src, dst, p_name))
