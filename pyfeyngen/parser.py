from .errors import InvalidReactionError

def parse_reaction(reaction_str):
    """
    Transforms a reaction string into a nested list structure.
    Supports branching (...), multi-particle loops [...],
    anchors @, and style attributes {...}.
    """
    if not reaction_str.strip():
        raise InvalidReactionError("La chaîne de réaction est vide.")
    
    # Check for balanced delimiters
    if reaction_str.count('(') != reaction_str.count(')'):
        raise InvalidReactionError("Unbalanced parentheses.")
    if reaction_str.count('[') != reaction_str.count(']'):
        raise InvalidReactionError("Unbalanced brackets.")
    if reaction_str.count('{') != reaction_str.count('}'):
        raise InvalidReactionError("Unbalanced braces.")
    
    s = reaction_str.strip()
    steps = []
    current_step = ""
    depth = 0
    
    # Step 1: Split by top-level '>'
    for char in s:
        if char == '(': depth += 1
        elif char == ')': depth -= 1
        
        if char == '>' and depth == 0:
            steps.append(current_step.strip())
            current_step = ""
        else:
            current_step += char
    steps.append(current_step.strip())
    
    final_structure = []
    for step in steps:
        if step:
            final_structure.append(_parse_step(step))
        
    return final_structure

def _parse_step(step_str):
    """Analyze a step to separate particles, blocks ( ), loops [ ], anchors @, and styles { }"""
    tokens = []
    i = 0
    while i < len(step_str):
        if step_str[i].isspace():
            i += 1
            continue
            
        # 1. GESTION DES PARENTHÈSES (Cascades)
        if step_str[i] == '(':
            start = i + 1
            depth = 1
            i += 1
            while i < len(step_str) and depth > 0:
                if step_str[i] == '(': depth += 1
                elif step_str[i] == ')': depth -= 1
                i += 1
            tokens.append(parse_reaction(step_str[start:i-1]))

        # 2. Manage [] = Bend
        elif step_str[i] == '[':
            start = i + 1
            depth = 1
            i += 1
            while i < len(step_str) and depth > 0:
                if step_str[i] == '[': depth += 1
                elif step_str[i] == ']': depth -= 1
                i += 1
            loop_content = [p.strip() for p in step_str[start:i-1].split() if p.strip()]
            tokens.append({'loop': loop_content})

        # 3. manage Anchors @
        elif step_str[i] == '@':
            start = i + 1
            # FIX: Add '{' as a stop character
            while i < len(step_str) and not step_str[i].isspace() and step_str[i] not in '([{':
                i += 1
            anchor_text = step_str[start:i]
            if ':' in anchor_text:
                name, part = anchor_text.split(':', 1)
                tokens.append({'anchor': name, 'particle': part})
            else:
                tokens.append({'anchor': anchor_text, 'particle': None})

        # 4. Manage {style} (ex: {blob})
        elif step_str[i] == '{':
            start = i + 1
            depth = 1
            i += 1
            while i < len(step_str) and depth > 0:
                if step_str[i] == '{': depth += 1
                elif step_str[i] == '}': depth -= 1
                i += 1
            attr_content = step_str[start:i-1].strip()
            

            # Apply the attribute to the last added element
            if tokens:
                last_item = tokens[-1]
                if isinstance(last_item, dict):
                    last_item['style'] = attr_content
                elif isinstance(last_item, str):
                    tokens[-1] = {'name': last_item, 'style': attr_content}
                elif isinstance(last_item, list):
                    tokens[-1] = {'cascade': last_item, 'style': attr_content}
            continue # Important: do not increment i twice
               

        # 5. Particles
        else:
            start = i
            # FIX: Explicitly stop before '@', '(', '[' or '{'
            while i < len(step_str) and not step_str[i].isspace() and step_str[i] not in '([@{':
                i += 1
            token = step_str[start:i]
            if token:
                tokens.append(token)
                
    return tokens