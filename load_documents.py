import argparse
from knowledge_base import KnowledgeBase
from knowledge_loader import KnowledgeLoader

def main():
    parser = argparse.ArgumentParser(description="Load documents into Geoatlas knowledge base")
    parser.add_argument("--pdf", help="Path to PDF file to load")
    parser.add_argument("--pptx", help="Path to PowerPoint file to load")
    parser.add_argument("--dir", help="Load all PDFs/PowerPoints from directory")
    parser.add_argument("--category", default="documents", help="Knowledge category")
    parser.add_argument("--save", action="store_true", help="Save KB to file after loading")
    
    args = parser.parse_args()
    
    # Initialize
    kb = KnowledgeBase()
    loader = KnowledgeLoader(kb)
    
    # Load files
    if args.pdf:
        loader.load_pdf_to_kb(args.pdf, args.category)
    
    if args.pptx:
        loader.load_powerpoint_to_kb(args.pptx, args.category)
    
    if args.dir:
        loader.load_directory_to_kb(args.dir)
    
    # Save if requested
    if args.save:
        loader.save_kb_to_file()

if __name__ == "__main__":
    main()