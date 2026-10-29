from limiter import TokenBucket

class RateLimitMiddleware:
    def __init__(self, app, capacity: int = 10, refill_rate: float = 1.0):
        self.app = app
        # Capacity: Max burst of 10 requests
        # Refill rate: 1 request per second
        self.limiter = TokenBucket(capacity=capacity, refill_rate=refill_rate)

    def __call__(self, environ: dict, start_response: callable) -> list[bytes]:
        # Extract client IP (Handling proxies)
        ip = environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR", "unknown"))
        
        # Check rate limit
        allowed, retry_after = self.limiter.consume(key=ip)
        
        if not allowed:
            status = "429 Too Many Requests"
            headers = [
                ("Content-Type", "application/json"),
                ("Retry-After", str(int(retry_after) + 1))
            ]
            start_response(status, headers)
            return [b'{"error": "Too Many Requests. Please slow down."}']
            
        # If allowed, pass the request to the actual application
        return self.app(environ, start_response)