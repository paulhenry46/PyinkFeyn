class FeyngenError(Exception):
    """Base class for pyfeyngen errors."""
    pass

class InvalidReactionError(FeyngenError):
    """The syntax of the string is incorrect."""
    pass

class UnknownParticleError(FeyngenError):
    """A particle is not defined in physics.py."""
    pass