class NoCacheMiddleware:
    """
    Middleware to prevent browser caching for sensitive pages.
    This helps prevent back-button access to protected pages after logout.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Always prevent caching of authentication pages
        auth_paths = ["/login/", "/register/", "/logout/", "/student-profile/"]
        if any(request.path.startswith(path) for path in auth_paths):
            self.set_no_cache_headers(response)

        # For logged-in users, prevent caching of all pages
        elif request.user.is_authenticated:
            self.set_no_cache_headers(response)

        return response

    def set_no_cache_headers(self, response):
        """Set headers to prevent caching."""
        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0, private"
        )
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
