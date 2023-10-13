class ComponentException(Exception):
    """Base Exception for the components"""


class NoComponentError(ComponentException):
    """No component has been found"""


class SeveralComponentError(ComponentException):
    """More than one component have been found"""
