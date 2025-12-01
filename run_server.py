#!/usr/bin/env python3
"""
Convex Optimizer 2000 - Server Runner
Start the Flask development server
"""

import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solver.app import run_server

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run Convex Optimizer 2000 Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     ██████╗ ██████╗ ███╗   ██╗██╗   ██╗███████╗██╗  ██╗          ║
    ║    ██╔════╝██╔═══██╗████╗  ██║██║   ██║██╔════╝╚██╗██╔╝          ║
    ║    ██║     ██║   ██║██╔██╗ ██║██║   ██║█████╗   ╚███╔╝           ║
    ║    ██║     ██║   ██║██║╚██╗██║╚██╗ ██╔╝██╔══╝   ██╔██╗           ║
    ║    ╚██████╗╚██████╔╝██║ ╚████║ ╚████╔╝ ███████╗██╔╝ ██╗          ║
    ║     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝          ║
    ║                                                                   ║
    ║              OPTIMIZER 2000 - Server Starting...                  ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    print(f"    Starting server at http://{args.host}:{args.port}")
    print(f"    Open http://localhost:{args.port}/optimizer.html in your browser")
    print()

    run_server(host=args.host, port=args.port, debug=args.debug)
