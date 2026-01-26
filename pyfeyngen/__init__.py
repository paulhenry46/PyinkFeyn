
# pyfeyngen/__init__.py
# Main initialization file for the pyfeyngen package.

from .parser import parse_reaction
from .layout import FeynmanGraph
from .exporter import generate_physical_tikz
from .errors import InvalidReactionError, UnknownParticleError
from .logger import setup_logging, logger
from .layout_engine import LayeredLayout
import logging

__version__ = "1.0.0"
__author__ = "Saux Paulhenry & Contributors"

def quick_render(reaction_string, user_dict=None, debug=False):

    # Enable debug logging if requested
    if debug:
        setup_logging(True)
    try:
        # Parse the reaction string into a structured format
        structure = parse_reaction(reaction_string)
        # Build the Feynman graph from the parsed structure
        graph = FeynmanGraph(structure)
        # Log graph node and edge information for debugging
        logger.debug(f"\nNodes created: {graph.v_count} vertex, {graph.in_count} inputs, {graph.f_count} outputs.")
        logger.debug("\nEdge list:")
        logger.debug(f"{'Source':<10} | {'Target':<10} | {'Particle':<10}")
        logger.debug("-" * 35)
        for src, dst, particle in graph.edges:
            logger.debug(f"{src:<10} | {dst:<10} | {particle:<10}")
        logger.debug("-" * 35)
        logger.debug("\nAnchor points:")
        logger.debug(graph.anchor_points)

        # Generate the TikZ code from the graph and user dictionary
        return generate_physical_tikz(graph, user_dict)
    except InvalidReactionError as e:
        # Return a LaTeX comment for syntax errors
        return f"% Syntax error: {e}"
    except UnknownParticleError as e:
        # Return a LaTeX comment for unknown particle errors
        return f"% Physics error: {e}"
    except Exception as e:
        # Return a LaTeX comment for any unexpected error
        return f"% Unexpected error: {e}"
    
def quick_geometry(reaction_string, debug=False):
    """
    Parse une réaction et retourne les coordonnées et métadonnées 
    sous forme de dictionnaire (convertible en JSON).
    """
    # Active les logs si besoin
    if debug:
        setup_logging(True)
        
    try:
        # 1. Pipeline classique : Parser -> Graphe
        structure = parse_reaction(reaction_string)
        graph = FeynmanGraph(structure)
        
        # 2. Pipeline Géométrique : Engine de Layout
        # On peut ajuster l'espacement ici si nécessaire
        engine = LayeredLayout(graph, x_spacing=150, y_spacing=100)
        
        # 3. Calcul et récupération des données pour Inkscape
        geometry_data = engine.get_inkscape_data()
        
        if debug:
            logger = logging.getLogger("pyfeyngen")
            logger.debug(f"Geometry calculated for {len(geometry_data['nodes'])} nodes.")
            
        return geometry_data

    except Exception as e:
        if debug:
            print(f"Error in quick_geometry: {e}")
        return {"error": str(e)}

# Define what is accessible with 'from pyfeyngen import *'
__all__ = ["parse_reaction", "FeynmanGraph", "generate_physical_tikz", "quick_render", "quick_geometry"]