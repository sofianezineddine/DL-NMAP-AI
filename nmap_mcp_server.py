
from fastmcp import FastMCP
import subprocess
import os

# Initialize the MCP Server
mcp = FastMCP("Nmap-Validator")

# --- CONFIGURATION: SET YOUR NMAP PATH HERE ---
# If 'where nmap' gave you a different path, paste it here inside the r"" quotes.
NMAP_PATH = r"C:\Program Files (x86)\Nmap\nmap.exe" 

def run_nmap_scan(command: str) -> str:
    """
    The actual logic that runs the command. 
    Import THIS function in your Python scripts.
    """
    # Security Check
    if not command.strip().startswith("nmap"):
        return "Error: Only Nmap commands are allowed."
    
    # 1. Replace the simple 'nmap' command with the Full Path
    # This ensures Python finds the executable even if PATH is broken.
    if os.path.exists(NMAP_PATH):
        # Replaces just the first word "nmap" with the full path
        final_command = command.replace("nmap", f'"{NMAP_PATH}"', 1)
    else:
        # Fallback: Try using just 'nmap' and hope it's in PATH
        print(f"[Warning] Could not find Nmap at {NMAP_PATH}. Trying system PATH...")
        final_command = command

    try:
        print(f"[MCP] Executing: {final_command}")
        
        result = subprocess.run(
            final_command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30,
            encoding='utf-8',     # Fix for Windows encoding
            errors='replace'      # prevents crashing on weird characters
        )
        
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
       # ... (previous subprocess code) ...
        
        print(f"Return code: {result.returncode}")
        
        # --- FIX: Check for Nmap specific failure messages even if return code is 0 ---
        if result.returncode == 0:
            # Check if Nmap actually found the target
            if "Failed to resolve" in result.stderr or "0 hosts up" in result.stdout:
                 return f"FAILED (Target Error):\n{result.stderr}\n{result.stdout}"
            
            return f"SUCCESS:\n{result.stdout}"
        else:
            return f"FAILED:\n{result.stderr}"
            
    except FileNotFoundError:
        return f"ERROR: Nmap not found. Please verify the path: {NMAP_PATH}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- Define the Tool ---
@mcp.tool()
def execute_nmap_validation(command: str) -> str:
    return run_nmap_scan(command)

if __name__ == "__main__":
    mcp.run()