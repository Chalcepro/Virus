#!/usr/bin/env python3
"""
Convenience script to manage the complete Words Generator workflow.
Generates data and/or trains the model in one command.
"""

import sys
import subprocess
import argparse
from pathlib import Path

import config

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"\n✗ FAILED: {description}")
            return False
        print(f"\n✓ SUCCESS: {description}")
        return True
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Manage Words Generator workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate data only
  python workflow.py --generate
  
  # Train with generated data only
  python workflow.py --train
  
  # Generate and train (full workflow)
  python workflow.py --full
  
  # Custom generation parameters
  python workflow.py --generate --conversations 500 --sentences 3000
  
  # Train with custom parameters
  python workflow.py --train --epochs 30 --retrain
        """
    )
    
    # Generation options
    parser.add_argument('--generate', action='store_true',
                        help='Generate training data')
    parser.add_argument('--conversations', type=int, default=200,
                        help='Number of conversations (default: 200)')
    parser.add_argument('--knowledge', type=int, default=200,
                        help='Number of knowledge entries (default: 200)')
    parser.add_argument('--sentences', type=int, default=500,
                        help='Number of sentences (default: 500)')
    
    # Training options
    parser.add_argument('--train', action='store_true',
                        help='Train model with base-data')
    parser.add_argument('--epochs', type=int, default=25,
                        help='Training epochs (default: 25)')
    parser.add_argument('--lr', type=float, default=0.0005,
                        help='Learning rate (default: 0.0005)')
    parser.add_argument('--retrain', action='store_true',
                        help='Retrain on all data (not just new)')
    parser.add_argument('--reset', action='store_true',
                        help='Reset training state before training')
    
    # Combined options
    parser.add_argument('--full', action='store_true',
                        help='Run full workflow: generate + train')
    parser.add_argument('--quick', action='store_true',
                        help='Quick test: small generation + quick training')
    
    # Other options
    parser.add_argument('--test', action='store_true',
                        help='Test base-data integration (no generation/training)')
    
    args = parser.parse_args()
    
    # Determine what to do
    do_generate = args.generate or args.full or args.quick
    do_train = args.train or args.full or args.quick
    
    # Quick mode overrides
    if args.quick:
        args.conversations = 50
        args.knowledge = 50
        args.sentences = 100
        args.epochs = 2
        args.retrain = True
    
    if not (do_generate or do_train or args.test):
        parser.print_help()
        return
    
    # Test integration
    if args.test:
        print("Testing base-data integration...")
        result = subprocess.run([sys.executable, 'test_base_data.py'])
        sys.exit(result.returncode)
    
    # Generate data
    if do_generate:
        cmd = f'py -3 "words generator\\main_generator.py" ' \
              f'--conversations {args.conversations} ' \
              f'--knowledge {args.knowledge} ' \
              f'--sentences {args.sentences}'
        if not run_command(cmd, "GENERATING TRAINING DATA"):
            print("\n✗ Generation failed. Exiting.")
            sys.exit(1)

        cmd = f'py -3 "words generator\\generate_training_data.py"'
        if not run_command(cmd, "GENERATING ADDITIONAL BASE-DATA FROM DEEPSEEK OUTPUT"):
            print("\n✗ Generation of deepseek-derived data failed. Exiting.")
            sys.exit(1)
    
    # Train model
    if do_train:
        cmd = f'py -3 auto_train.py --base-data ' \
              f'--epochs {args.epochs} ' \
              f'--lr {args.lr} ' \
              f'--model {config.MODEL_PATH}'
        
        if args.reset:
            cmd = f'py -3 auto_train.py --reset && {cmd}'
        elif args.retrain:
            cmd += ' --retrain'
        
        if not run_command(cmd, "TRAINING MODEL WITH BASE-DATA"):
            print("\n✗ Training failed. Exiting.")
            sys.exit(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*60}\n")
    
    if do_generate:
        print("✓ Data generated in:")
        print("  • data/base-data-conversations/")
        print("  • data/base-data-knowledge/")
        print("  • data/base-data-sentences/")
    
    if do_train:
        print(f"✓ Model trained and saved to: {config.MODEL_PATH}")
        print("✓ To chat with the model, run: py -3 text_model.py")
        print("✓ To generate text, run: py -3 main.py \"hello\" 100")
    
    if args.quick:
        print("\n💡 Tip: Run with more data for better results:")
        print("   python workflow.py --full --conversations 500 --sentences 2000")

if __name__ == "__main__":
    main()
