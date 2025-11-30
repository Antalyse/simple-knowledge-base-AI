import argparse
import os
import sys


# Configuration
from .config import UPLOAD_FOLDER 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)





def cli_ask(args):
    from .ask import ask_question
    output, code = ask_question(question=args.question, k=args.k, model=args.model)
    
    if code == 200:
        print(f"Sources: {output['sources']}\n")
        print(output['answer'])
    else:
        print(f"Error with Code: {code}")

def cli_ingest(args):
    from .ingest import ingest
    output, code = ingest(args.path)



def main():
    
    parser = argparse.ArgumentParser(
        description="An CLI to interact with a local, AI powered knowledge base.",
        epilog="Example: kb ask \"When did we sign the partnership contract with Antalyse International Inc. ?\""
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # --- Command: ask ---
    subparser_cleanup = subparsers.add_parser("ask", help="Will respond with an answer to your question.")
    subparser_cleanup.add_argument("question", type=str, help="The question you want to ask.")
    subparser_cleanup.add_argument("--model", default=None, type=str, help="Set a model to use different than the config")
    subparser_cleanup.add_argument("-k", default=3, type=int, help="Override the amount of samples used as context")
    subparser_cleanup.set_defaults(func=cli_ask)

    # --- Command: inject ---
    subparser_schedule = subparsers.add_parser("ingest", help="Injects files into the knowledge base")
    subparser_schedule.add_argument("path", type=str, help="The path of the file or folder to inject")
    subparser_schedule.add_argument("-R", action="store_true", help="Inject all subfolders and files recursively")
    subparser_schedule.set_defaults(func=cli_ingest)



    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)

if __name__ == "__main__":
    main()
    