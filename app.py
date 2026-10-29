from wsgiref.simple_server import make_server
from middleware import RateLimitMiddleware
from router import application as base_app
from db import init_db

def main() -> None:
    init_db()
    
    # Wrap the base app with our Rate Limiter (5 requests max burst, 1 refill per second)
    protected_app = RateLimitMiddleware(base_app, capacity=5, refill_rate=1.0)
    
    port = 8000
    with make_server("", port, protected_app) as httpd:
        print(f"Serving on http://localhost:{port}")
        print("Rate limit: 5 requests burst, 1 refill/sec.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")

if __name__ == "__main__":
    main()