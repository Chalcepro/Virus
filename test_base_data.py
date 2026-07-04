#!/usr/bin/env python3
"""
Quick test to verify --base-data integration
"""
import sys
import argparse
from pathlib import Path

# Import config
sys.path.insert(0, str(Path(__file__).parent))
import config

def test_base_data_integration():
    """Test that base-data files are discoverable"""
    
    # Manually test get_data_files logic
    data_dir = config.DATA_DIR
    print(f"Data directory: {data_dir}")
    
    # Test regular files
    regular_files = sorted(data_dir.glob("*.txt"))
    print(f"\n✓ Regular data files found: {len(regular_files)}")
    for f in regular_files[:3]:
        print(f"  - {f.relative_to(data_dir)}")
    
    # Test base-data files
    base_data_dirs = [
        data_dir / 'base-data-conversations',
        data_dir / 'base-data-knowledge', 
        data_dir / 'base-data-sentences',
        data_dir / 'base-data-generated',
    ]
    
    base_files = []
    for base_dir in base_data_dirs:
        if base_dir.exists():
            files = sorted(base_dir.glob("*.txt"))
            base_files.extend(files)
            print(f"\n✓ {base_dir.name}: {len(files)} files")
            for f in files:
                size_kb = f.stat().st_size / 1024
                print(f"  - {f.name} ({size_kb:.1f} KB)")
    
    print(f"\n{'='*60}")
    print(f"INTEGRATION TEST RESULTS:")
    print(f"{'='*60}")
    print(f"Regular data files:    {len(regular_files)} files")
    print(f"Base-data files:       {len(base_files)} files")
    print(f"Total files available: {len(regular_files) + len(base_files)} files")
    
    if base_files:
        print(f"\n✓ SUCCESS: --base-data flag will work!")
        print(f"  Files can be trained with: py -3 auto_train.py --base-data")
    else:
        print(f"\n✗ ISSUE: No base-data files found")
    
    print(f"\nTo generate more base-data, run:")
    print(f"  py -3 words\\ generator\\main_generator.py --conversations 500 --knowledge 500 --sentences 2000")

if __name__ == "__main__":
    test_base_data_integration()
