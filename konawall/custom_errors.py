class RequestFailed(Exception):
    "Raised when a request fails."

    def __init__(self, status_code: int):
        self.status_code = status_code
        self.message = f"Request failed with status code {self.status_code}"
        super().__init__(self.message)

class UnsupportedPlatform(Exception):
    "Raised when the platform is not supported."

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)