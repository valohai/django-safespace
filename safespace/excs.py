class Problem(Exception):
    """
    Generic problem that could be shown to the end-user.

    This could also be used as a mixin, if you like.
    """

    # These are here to allow subclasses to default them,
    # if necessary.

    code = None
    title = None

    def __init__(self, message=None, code=None, title=None):
        """
        Initialize a Problem.

        :param message: The actual error message.
        :param code: An optional machine-readable error code.
        :param title: An optional title for the error.
        """
        super(Problem, self).__init__(message)
        if code:
            self.code = code
        if title:
            self.title = title
