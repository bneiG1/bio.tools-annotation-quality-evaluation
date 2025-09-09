#!/usr/bin/env python3
"""
Cleanup script to kill existing Streamlit processes
Useful for deployment environments where processes might not shut down cleanly
"""

import os
import sys
import signal
import subprocess
import time

def find_streamlit_processes():
    """Find running Streamlit processes."""
    try:
        # Use ps to find streamlit processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            streamlit_procs = []
            for line in lines:
                if 'streamlit' in line.lower() and 'python' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            streamlit_procs.append(pid)
                        except ValueError:
                            continue
            return streamlit_procs
    except FileNotFoundError:
        # ps command not available, try alternative
        pass
    
    # Alternative: use pgrep if available
    try:
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = [int(pid.strip()) for pid in result.stdout.split('\n') if pid.strip().isdigit()]
            return pids
    except FileNotFoundError:
        pass
    
    return []

def kill_processes(pids):
    """Kill the specified processes."""
    for pid in pids:
        try:
            print(f"🔄 Killing process {pid}...")
            
            # Windows-compatible process termination
            if sys.platform == "win32":
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             capture_output=True, text=True)
                print(f"✅ Process {pid} terminated")
            else:
                # Unix-like systems
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)  # This doesn't kill, just checks if process exists
                    print(f"⚠️ Process {pid} still running, using SIGKILL...")
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    print(f"✅ Process {pid} terminated successfully")
                
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"❌ Failed to kill process {pid}: {e}")

def cleanup_ports():
    """Try to free up common Streamlit ports."""
    ports = ['8501', '8502', '8503']
    
    for port in ports:
        try:
            # Find processes using the port
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = [int(pid.strip()) for pid in result.stdout.split('\n') 
                       if pid.strip().isdigit()]
                print(f"🔄 Found processes using port {port}: {pids}")
                kill_processes(pids)
        except FileNotFoundError:
            # lsof not available
            pass

def main():
    """Main cleanup function."""
    print("🧹 Streamlit Process Cleanup")
    print("=" * 30)
    
    # Find and kill Streamlit processes
    streamlit_pids = find_streamlit_processes()
    if streamlit_pids:
        print(f"Found {len(streamlit_pids)} Streamlit processes: {streamlit_pids}")
        kill_processes(streamlit_pids)
    else:
        print("No Streamlit processes found")
    
    # Try to free up ports
    print("\n🔌 Checking ports...")
    cleanup_ports()
    
    print("\n✅ Cleanup complete!")
    
    # Wait a moment for processes to fully terminate
    time.sleep(2)

if __name__ == "__main__":
    main()
