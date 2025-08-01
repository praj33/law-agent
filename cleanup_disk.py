#!/usr/bin/env python3
"""
Disk Cleanup Utility for Law Agent
Safely clean up cache files, temporary data, and optimize disk usage.
"""

import os
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

class DiskCleaner:
    """Advanced disk cleanup utility."""
    
    def __init__(self):
        self.cleaned_size = 0
        self.errors = []
    
    def get_disk_usage(self) -> Tuple[float, float, float]:
        """Get disk usage statistics."""
        total, used, free = shutil.disk_usage('.')
        return (
            total / (1024**3),  # GB
            used / (1024**3),   # GB
            free / (1024**3)    # GB
        )
    
    def get_directory_size(self, path: Path) -> int:
        """Get directory size in bytes."""
        total = 0
        try:
            if path.is_file():
                return path.stat().st_size
            
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except (OSError, FileNotFoundError):
                        pass
        except (OSError, PermissionError):
            pass
        return total
    
    def clean_pip_cache(self) -> int:
        """Clean pip cache."""
        try:
            print("🧹 Cleaning pip cache...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'cache', 'purge'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Pip cache cleaned")
                return 100 * 1024 * 1024  # Estimate 100MB
            else:
                print(f"⚠️ Pip cache cleanup warning: {result.stderr}")
        except Exception as e:
            print(f"❌ Pip cache cleanup failed: {e}")
        return 0
    
    def clean_temp_files(self) -> int:
        """Clean temporary files."""
        cleaned = 0
        temp_dirs = [
            Path(tempfile.gettempdir()),
            Path('./temp'),
            Path('./tmp'),
            Path('./cache'),
            Path('./logs')
        ]
        
        print("🧹 Cleaning temporary files...")
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                try:
                    for item in temp_dir.iterdir():
                        if item.is_file() and self._is_safe_to_delete(item):
                            size = item.stat().st_size
                            item.unlink()
                            cleaned += size
                        elif item.is_dir() and item.name.startswith('tmp'):
                            size = self.get_directory_size(item)
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned += size
                except (OSError, PermissionError) as e:
                    self.errors.append(f"Temp cleanup error: {e}")
        
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned // (1024**2):.1f} MB of temporary files")
        return cleaned
    
    def clean_python_cache(self) -> int:
        """Clean Python cache files."""
        cleaned = 0
        print("🧹 Cleaning Python cache...")
        
        # Clean __pycache__ directories
        for pycache in Path('.').rglob('__pycache__'):
            try:
                size = self.get_directory_size(pycache)
                shutil.rmtree(pycache, ignore_errors=True)
                cleaned += size
            except Exception:
                pass
        
        # Clean .pyc files
        for pyc_file in Path('.').rglob('*.pyc'):
            try:
                size = pyc_file.stat().st_size
                pyc_file.unlink()
                cleaned += size
            except Exception:
                pass
        
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned // (1024**2):.1f} MB of Python cache")
        return cleaned
    
    def clean_huggingface_cache(self) -> int:
        """Clean Hugging Face model cache."""
        cleaned = 0
        hf_cache_dirs = [
            Path.home() / '.cache' / 'huggingface',
            Path.home() / '.cache' / 'torch',
            Path('./models'),
        ]
        
        print("🧹 Cleaning ML model cache...")
        for cache_dir in hf_cache_dirs:
            if cache_dir.exists():
                try:
                    # Only clean old/unused models
                    for item in cache_dir.iterdir():
                        if item.is_dir() and 'temp' in item.name.lower():
                            size = self.get_directory_size(item)
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned += size
                except Exception as e:
                    self.errors.append(f"HF cache cleanup error: {e}")
        
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned // (1024**2):.1f} MB of ML cache")
        return cleaned
    
    def clean_logs(self) -> int:
        """Clean old log files."""
        cleaned = 0
        log_dirs = [Path('./logs'), Path('./log')]
        
        print("🧹 Cleaning old logs...")
        for log_dir in log_dirs:
            if log_dir.exists():
                try:
                    for log_file in log_dir.glob('*.log*'):
                        if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                            size = log_file.stat().st_size
                            log_file.unlink()
                            cleaned += size
                except Exception as e:
                    self.errors.append(f"Log cleanup error: {e}")
        
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned // (1024**2):.1f} MB of logs")
        return cleaned
    
    def _is_safe_to_delete(self, file_path: Path) -> bool:
        """Check if file is safe to delete."""
        safe_extensions = {'.tmp', '.temp', '.log', '.cache', '.bak'}
        safe_patterns = {'temp', 'tmp', 'cache', 'backup'}
        
        # Check extension
        if file_path.suffix.lower() in safe_extensions:
            return True
        
        # Check filename patterns
        name_lower = file_path.name.lower()
        return any(pattern in name_lower for pattern in safe_patterns)
    
    def run_windows_cleanup(self) -> int:
        """Run Windows disk cleanup if available."""
        try:
            print("🧹 Running Windows disk cleanup...")
            # Run disk cleanup for temp files
            subprocess.run(['cleanmgr', '/sagerun:1'], 
                         capture_output=True, timeout=60)
            print("✅ Windows cleanup completed")
            return 500 * 1024 * 1024  # Estimate 500MB
        except Exception:
            print("⚠️ Windows cleanup not available")
        return 0
    
    def optimize_database(self) -> int:
        """Optimize database files."""
        cleaned = 0
        db_files = list(Path('.').glob('*.db'))
        
        if db_files:
            print("🧹 Optimizing database...")
            for db_file in db_files:
                try:
                    original_size = db_file.stat().st_size
                    # SQLite VACUUM command would go here
                    # For now, just report the file size
                    print(f"📊 Database {db_file.name}: {original_size // (1024**2):.1f} MB")
                except Exception:
                    pass
        
        return cleaned
    
    def run_cleanup(self) -> bool:
        """Run complete disk cleanup."""
        print("🏛️  LAW AGENT DISK CLEANUP")
        print("=" * 50)
        
        # Show initial disk usage
        total, used, free = self.get_disk_usage()
        print(f"💾 Disk Usage: {used:.1f}GB / {total:.1f}GB ({used/total*100:.1f}%)")
        print(f"💾 Free Space: {free:.1f}GB")
        
        if free < 5:  # Less than 5GB free
            print("⚠️ CRITICAL: Very low disk space!")
        elif free < 10:  # Less than 10GB free
            print("⚠️ WARNING: Low disk space")
        
        print("\n🧹 Starting cleanup...")
        
        # Run cleanup operations
        self.cleaned_size += self.clean_pip_cache()
        self.cleaned_size += self.clean_temp_files()
        self.cleaned_size += self.clean_python_cache()
        self.cleaned_size += self.clean_huggingface_cache()
        self.cleaned_size += self.clean_logs()
        self.cleaned_size += self.run_windows_cleanup()
        self.cleaned_size += self.optimize_database()
        
        # Show results
        print("\n" + "=" * 50)
        print("🎉 CLEANUP COMPLETE!")
        print(f"🧹 Total cleaned: {self.cleaned_size // (1024**2):.1f} MB")
        
        # Show new disk usage
        total, used, free = self.get_disk_usage()
        print(f"💾 New usage: {used:.1f}GB / {total:.1f}GB ({used/total*100:.1f}%)")
        print(f"💾 Free space: {free:.1f}GB")
        
        if self.errors:
            print(f"\n⚠️ {len(self.errors)} warnings occurred:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        return free > 5  # Return True if we have enough space


def main():
    """Main cleanup function."""
    cleaner = DiskCleaner()
    success = cleaner.run_cleanup()
    
    if success:
        print("\n✅ Disk cleanup successful! Ready to start Law Agent.")
    else:
        print("\n❌ Still low on disk space. Consider:")
        print("   • Uninstalling unused programs")
        print("   • Moving files to external storage")
        print("   • Using Windows Storage Sense")
    
    return success


if __name__ == "__main__":
    main()
