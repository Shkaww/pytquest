# exceptions.py

class InsufficientFundsError(Exception):
    """Raised when a user tries to make a request without enough balance."""
    pass

class InvalidDataError(Exception):
    """Raised when provided data is not valid for ML model."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Invalid data provided: {errors}")


class AuthenticationError(Exception):
    """Raised for auth errors"""
    pass