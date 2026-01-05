import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("Importing app from run.py...")
    # run.py has 'app = create_app()'
    from run import app
    
    print("\n--- Registered Routes ---")
    # Count routes
    route_count = len(list(app.url_map.iter_rules()))
    print(f"Total routes: {route_count}")
    
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    
    # Check for specific routes from app_original/legacy_routes
    has_index = any(r.endpoint == 'index' for r in app.url_map.iter_rules())
    has_ranking = any(r.endpoint == 'ranking' for r in app.url_map.iter_rules())
    
    if has_index and has_ranking:
        print("\nSUCCESS: Original routes found via run.py.")
    else:
        print("\nFAILURE: Original routes MISSING in run.py.")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
