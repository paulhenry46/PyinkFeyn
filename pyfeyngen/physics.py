# physics.py
from .errors import UnknownParticleError
from .logger import logger
import re
# physics.py

PARTICLES = {
    # Quarks
    'u':     {'style': 'fermion', 'label': 'u', 'is_anti': False},
    'ubar':  {'style': 'fermion', 'label': '\\bar{u}', 'is_anti': True},
    'd':     {'style': 'fermion', 'label': 'd', 'is_anti': False},
    'dbar':  {'style': 'fermion', 'label': '\\bar{d}', 'is_anti': True},
    't':     {'style': 'fermion', 'label': 't', 'is_anti': False},
    'tbar':  {'style': 'fermion', 'label': '\\bar{t}', 'is_anti': True},
    
    # Leptons
    'e-':    {'style': 'fermion', 'label': 'e^{-}', 'is_anti': False},
    'e+':    {'style': 'fermion', 'label': 'e^{+}', 'is_anti': True},
    'mu-':   {'style': 'fermion', 'label': '\\mu^{-}', 'is_anti': False},
    'mu+':   {'style': 'fermion', 'label': '\\mu^{+}', 'is_anti': True},
    'tau-':  {'style': 'fermion', 'label': '\\tau^{-}', 'is_anti': False},
    'tau+':  {'style': 'fermion', 'label': '\\tau^{+}', 'is_anti': True},
    'nu_e':  {'style': 'fermion', 'label': '\\nu_{e}', 'is_anti': False},
    
    # Bosons
    'Z0':    {'style': 'boson', 'label': 'Z^{0}', 'is_anti': False},
    'W+':    {'style': 'charged boson', 'label': 'W^{+}', 'is_anti': False},
    'W-':    {'style': 'charged boson', 'label': 'W^{-}', 'is_anti': True},
    'gamma': {'style': 'photon', 'label': '\\gamma', 'is_anti': False},
    'g':     {'style': 'gluon', 'label': 'g', 'is_anti': False},
    'H':     {'style': 'scalar', 'label': 'H^{0}', 'is_anti': False}, # Style scalar = ligne tiretée ou pleine
}

GREEK_LETTERS = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 
                 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 
                 'rho', 'sigma', 'tau', 'phi', 'chi', 'psi', 'omega']

def get_info(name, user_dict=None):
    if user_dict == None:
        user_dict = {}
    if name in user_dict:
        return user_dict[name]
    elif name in PARTICLES:
        return PARTICLES[name]
    else:
        logger.warning(f"La particule '{name}' n'est pas définie dans la bibliothèque.")

        match = re.match(r"^([a-zA-Z]+?)(bar|\+|\-|0)?(_[a-zA-Z0-9]+)?$", name)

        if not match:
            logger.warning(f"La particule '{name}' est illisible.")
            return {"style": "fermion", "label": name, "is_anti": False}

        base, modifier, index = match.groups()

        # 1. Traitement de la BASE (ex: alpha -> \alpha)
        latex_base = rf"\{base}" if base in GREEK_LETTERS else base
        
        # 2. Traitement de l'INDICE (ex: _e -> _{e})
        index_str = f"_{{{index[1:]}}}" if index else ""

        # 3. ASSEMBLAGE FINAL (C'est ici qu'on transforme 'bar' en commande LaTeX)
        is_anti = False
        if modifier == 'bar':
            is_anti = True
            label = rf"\bar{{{latex_base}}}{index_str}"  # Donne \bar{\alpha}_{e}
        elif modifier in ['+', '-', '0']:
            label = f"{latex_base}^{{{modifier}}}{index_str}" # Donne \alpha^{+}_{e}
            if modifier == '+' and base in ['e', 'mu', 'tau']:
                is_anti = True
        else:
            label = f"{latex_base}{index_str}"

        # 4. Déduction du style
        style = "fermion"
        if base in ['phi', 'h', 'H', 'S']: style = "scalar"
        elif base in ['W', 'Z', 'gamma', 'g']: style = "boson" # Simplifié pour l'exemple

        return {
            "style": style,
            "label": label,
            "is_anti": is_anti
        }