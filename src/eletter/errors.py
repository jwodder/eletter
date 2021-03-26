class Error(Exception):
    """ The superclass of all custom exceptions raised by ``eletter`` """

    pass


class DecompositionError(Error, ValueError):
    """
    Raised when ``eletter`` is asked to decompose an
    `~email.message.EmailMessage` with an unrepresentable
    :mailheader:`Content-Type`
    """

    pass


class SimplificationError(Error, ValueError):
    """
    Raised when ``eletter`` is asked to decompose a message that cannot be
    simplified
    """

    pass


class MixedContentError(SimplificationError):
    """
    Subclass of `SimplificationError` raised when a :mimetype:`multipart/mixed`
    is encountered in which one or more attachments precede a message body
    part; such messages can be forced to be simplified by setting the ``unmix``
    argument of `~Eletter.simplify()` or `decompose_simple()` to `True`.
    """

    pass
