import os
import sys

# Add `apps/api` to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "api"))

from app.db.database import SessionLocal
from app.services.matcher import MatcherService

def main():
    db = SessionLocal()
    try:
        matcher = MatcherService(db)
        print("Running deterministic matcher...")
        results = matcher.run_matching()
        print(f"Matcher generated {len(results)} reconciliation results.")
        
        # Summary
        summary = {}
        for r in results:
            summary[r.match_type] = summary.get(r.match_type, 0) + 1
            
        print("Summary:")
        for k, v in summary.items():
            print(f"  {k}: {v}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
