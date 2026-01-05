import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("Importing app from app.py...")
    from app import app
    
    print("\n--- Registered Routes ---")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
        
    print("\n--- App Config ---")
    print(f"App Name: {app.name}")
    
    # Check for specific routes from app_original
    has_index = any(r.endpoint == 'index' for r in app.url_map.iter_rules())
    has_ranking = any(r.endpoint == 'ranking' for r in app.url_map.iter_rules())
    
    if has_index and has_ranking:
        print("\nSUCCESS: Original routes found.")
    else:
        print("\nFAILURE: Original routes MISSING.")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
