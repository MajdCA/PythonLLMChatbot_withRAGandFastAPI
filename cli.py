import argparse
import sys
from llm_chat import ChatBot

def main():
    parser = argparse.ArgumentParser(description="Geoatlas Chatbot CLI")
    parser.add_argument("query", nargs="?", help="Your question for the chatbot")
    parser.add_argument("--add-knowledge", action="store_true", help="Add new knowledge")
    parser.add_argument("--category", help="Knowledge category")
    parser.add_argument("--answer", help="Answer for knowledge")
    
    args = parser.parse_args()
    chatbot = ChatBot()
    
    if args.add_knowledge:
        if not all([args.query, args.category, args.answer]):
            print("Error: --add-knowledge requires --category and --answer")
            sys.exit(1)
        chatbot.add_knowledge(args.category, args.query, args.answer)
        print(f"✓ Knowledge added to '{args.category}'")
    elif args.query:
        answer = chatbot.answer(args.query)
        print(f"\nQ: {args.query}")
        print(f"A: {answer}\n")
    else:
        print("Usage: python cli.py 'your question'")
        print("       python cli.py 'question' --add-knowledge --category 'category' --answer 'answer'")

if __name__ == "__main__":
    main()
