#!/usr/bin/env python3
"""
Auto-updater for Lacs TikTok Monitor
Downloads the latest version from GitHub
"""

import os
import sys
import json
import requests
import zipfile
import shutil
from pathlib import Path

GITHUB_REPO = "Lacurity/tikmon-releases"  # Change this to your actual repo
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CURRENT_DIR = Path(__file__).parent

def get_current_version():
    """Get current version from version.json."""
    version_file = CURRENT_DIR / "version.json"
    if version_file.exists():
        try:
            with open(version_file, 'r') as f:
                data = json.load(f)
                return data.get("version", "1.0.0")
        except:
            pass
    return "1.0.0"

def get_latest_version():
    """Get latest version from GitHub."""
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v"), data["zipball_url"]
    except Exception as e:
        print(f"Failed to check for updates: {e}")
        return None, None

def download_and_extract(url, version):
    """Download and extract the latest version."""
    try:
        print(f"Downloading version {version}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save zip file
        zip_path = CURRENT_DIR / f"update_{version}.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract to temp directory
        temp_dir = CURRENT_DIR / "temp_update"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted folder (usually has repo name prefix)
        extracted_folders = [d for d in temp_dir.iterdir() if d.is_dir()]
        if not extracted_folders:
            raise Exception("No folders found in zip")
        
        source_dir = extracted_folders[0]
        
        # Backup current config
        config_backup = None
        config_file = CURRENT_DIR / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_backup = f.read()
        
        # Copy new files (excluding config.json and logs)
        for item in source_dir.iterdir():
            if item.name in ["config.json", "tiktok_monitor.log", "__pycache__"]:
                continue
                
            target = CURRENT_DIR / item.name
            if item.is_file():
                shutil.copy2(item, target)
                print(f"Updated: {item.name}")
            elif item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
                print(f"Updated directory: {item.name}")
        
        # Restore config if it was backed up
        if config_backup:
            with open(config_file, 'w') as f:
                f.write(config_backup)
            print("Restored config.json")
        
        # Update version file
        version_data = {
            "version": version,
            "updated_at": str(datetime.utcnow()),
            "auto_updated": True
        }
        with open(CURRENT_DIR / "version.json", 'w') as f:
            json.dump(version_data, f, indent=2)
        
        # Cleanup
        zip_path.unlink()
        shutil.rmtree(temp_dir)
        
        print(f"✅ Successfully updated to version {version}")
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        return False

def check_for_updates():
    """Check for updates and update if available."""
    current_version = get_current_version()
    latest_version, download_url = get_latest_version()
    
    if not latest_version:
        print("Could not check for updates")
        return False
    
    print(f"Current version: {current_version}")
    print(f"Latest version: {latest_version}")
    
    if current_version != latest_version:
        print("Update available!")
        response = input("Do you want to update? (y/n): ").lower().strip()
        if response == 'y':
            return download_and_extract(download_url, latest_version)
    else:
        print("You're running the latest version!")
    
    return False

def check_for_updates_silent():
    """Check for updates and auto-update if available (silent mode)."""
    try:
        current_version = get_current_version()
        latest_version, download_url = get_latest_version()
        
        if not latest_version:
            print("Could not check for updates")
            return False
        
        if current_version != latest_version:
            print(f"Update available: v{current_version} -> v{latest_version}")
            print("Auto-updating...")
            result = download_and_extract(download_url, latest_version)
            if result:
                print("Update completed successfully!")
            return result
        else:
            print("Already running latest version")
        
        return False
    except Exception as e:
        print(f"Auto-update failed: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--silent":
        check_for_updates_silent()
    else:
        check_for_updates()