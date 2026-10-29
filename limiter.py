import time
from db import get_connection

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate # Tokens per second

    def consume(self, key: str) -> tuple[bool, float]:
        """
        Returns (is_allowed, retry_after_seconds)
        """
        now = time.time()
        
        with get_connection() as conn:
            # Start an immediate transaction to lock the database for this operation
            conn.execute("BEGIN IMMEDIATE")
            
            cursor = conn.execute("SELECT tokens, last_refill FROM buckets WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if not row:
                # First request from this IP
                tokens = self.capacity - 1
                conn.execute(
                    "INSERT INTO buckets (key, tokens, last_refill) VALUES (?, ?, ?)",
                    (key, tokens, now)
                )
                conn.commit()
                return True, 0.0
                
            # Calculate refill
            elapsed = now - row["last_refill"]
            refilled_tokens = row["tokens"] + (elapsed * self.refill_rate)
            current_tokens = min(refilled_tokens, self.capacity)
            
            if current_tokens >= 1.0:
                # Allow request
                conn.execute(
                    "UPDATE buckets SET tokens = ?, last_refill = ? WHERE key = ?",
                    (current_tokens - 1.0, now, key)
                )
                conn.commit()
                return True, 0.0
            else:
                # Deny request
                conn.execute(
                    "UPDATE buckets SET tokens = ?, last_refill = ? WHERE key = ?",
                    (current_tokens, now, key)
                )
                conn.commit()
                
                # Calculate how long until 1 full token is available
                missing_tokens = 1.0 - current_tokens
                retry_after = missing_tokens / self.refill_rate
                return False, retry_after