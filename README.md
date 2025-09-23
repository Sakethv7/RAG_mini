RAG-Mini: Simple Document Q&A System
A minimal RAG (Retrieval-Augmented Generation) system that lets you ask questions about your documents using Google's Gemini AI.
Features

Document Processing: Supports .txt, .md, and .pdf files
Smart Chunking: Automatically splits documents into searchable chunks
Semantic Search: Uses sentence transformers for finding relevant content
AI-Powered Answers: Generates concise answers using Google Gemini
Local Embeddings: No API calls for document processing (uses sentence-transformers)
Interactive Chat: Simple command-line interface

Quick Start
1. Clone and Setup
bashgit clone <https://github.com/Sakethv7/RAG_mini>
cd RAG-mini
pip install -r requirements.txt
2. Get Google API Key

Go to Google AI Studio
Create an API key
Create .env file in project root:

GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
3. Add Documents
Place your documents in the documents/ folder:
documents/
├── your_file1.txt
├── your_file2.md
└── your_file3.pdf
4. Start Asking Questions
bashpython ask.py
Usage Examples
Q: What is the main topic of the documents?
A: The documents discuss historical battles and revolutionary figures from Indian history.

Q: Who was Savarkar?
A: Vinayak Damodar Savarkar was a revolutionary organizer and writer who founded Abhinav Bharat and later became president of the Hindu Mahasabha.
File Structure
RAG-mini/
├── ask.py              # Interactive Q&A interface
├── eval.py             # Test retrieval only
├── ingest.py           # Document processing (optional)
├── rag_simple.py       # Core RAG system
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── documents/         # Your documents go here
│   ├── *.txt
│   ├── *.md
│   └── *.pdf
└── README.md
How It Works

Document Loading: Reads all supported files from documents/ folder
Text Chunking: Splits documents into overlapping chunks (800 chars with 200 char overlap)
Embedding: Converts text chunks to vectors using all-MiniLM-L6-v2
Storage: Stores embeddings in Qdrant (in-memory mode for Windows compatibility)
Retrieval: Finds most relevant chunks for your question
Generation: Uses Google Gemini to generate concise answers based on retrieved context

Configuration
You can customize the system by modifying parameters in rag_simple.py:

chunk_size: Size of text chunks (default: 800 characters)
overlap: Overlap between chunks (default: 200 characters)
embedding_model: Sentence transformer model (default: all-MiniLM-L6-v2)
k: Number of chunks to retrieve (default: 2)

Requirements

Python 3.8+
Google API key (free tier available)
~500MB disk space for embedding model (downloaded automatically)

Troubleshooting
Common Issues
Q: "GOOGLE_API_KEY missing" error
A: Create a .env file with your Google API key
Q: Documents not found
A: Make sure your files are in the documents/ folder and have supported extensions
Q: Qdrant connection errors
A: The system uses in-memory mode by default for Windows compatibility
Q: Slow first run
A: The embedding model is downloaded on first use (~500MB)
Contributing

Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request

License
MIT License - see LICENSE file for details
Acknowledgments

Built with Qdrant for vector search
Sentence Transformers for embeddings
Google Gemini for answer generation