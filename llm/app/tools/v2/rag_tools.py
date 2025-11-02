import hashlib
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app import logger


class RAGTools:
    """Tools for processing PDFs and documents using RAG (Retrieval-Augmented Generation)"""

    @staticmethod
    def _get_pdf_hash(pdf_path: str) -> str:
        """Generate a unique hash for the PDF file"""
        with open(pdf_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    @staticmethod
    def _get_persist_directory(pdf_hash: str) -> Path:
        """Get the persist directory for the PDF's vector store"""
        output_dir = Path("output") / "pdf_vectorstores" / pdf_hash
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    @tool("process_pdf_receipt_tool")
    def process_pdf_receipt(
        pdf_path        : str
        , question      : Optional[str] = None
    ) -> Dict:
        """
        Process a PDF receipt and extract information using RAG.
        Use this when a user uploads a PDF receipt or asks about PDF document content.

        Args:
            pdf_path: Path to the PDF file
            question: Optional specific question about the PDF.
                     If not provided, extracts general receipt information.

        Returns:
            Dict containing extracted information from the PDF

        Examples:
            - "What's the total amount in this PDF receipt?"
            - "Extract all transaction details from this PDF"
            - "What's the booking confirmation number?"
        """
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"PDF file not found: {pdf_path}"
                    , "data"    : None
                }

            if pdf_file.suffix.lower() != ".pdf":
                return {
                    "status"    : "error"
                    , "message" : f"Invalid file format. Expected PDF, got: {pdf_file.suffix}"
                    , "data"    : None
                }

            loader      = PyPDFLoader(pdf_path)
            documents   = loader.load()

            if not documents:
                return {
                    "status"    : "error"
                    , "message" : "No content found in PDF"
                    , "data"    : None
                }

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size      = 1000
                , chunk_overlap = 200
                , length_function = len
            )
            splits = text_splitter.split_documents(documents)

            embeddings = OllamaEmbeddings(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.1"
            )

            pdf_hash    = RAGTools._get_pdf_hash(pdf_path)
            persist_dir = RAGTools._get_persist_directory(pdf_hash)

            vectorstore = Chroma.from_documents(
                documents           = splits
                , embedding         = embeddings
                , persist_directory = str(persist_dir)
                , collection_name   = f"pdf_{pdf_hash}"
            )

            llm = ChatOllama(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.1"
                , temperature = 0.0
            )

            if not question:
                question = """Extract the following information from this receipt:
1. Total amount and currency
2. Date and time
3. Payment method
4. Transaction/Receipt number
5. Merchant/Vendor name
6. List of items or services
7. Any other relevant details"""

            template = """Answer the question based on the following context:

Context: {context}

Question: {question}

Answer:"""

            prompt      = ChatPromptTemplate.from_template(template)
            retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})

            def format_docs(docs):
                return "\n\n".join([d.page_content for d in docs])

            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            answer = rag_chain.invoke(question)

            logger.info("PDF receipt processed", extra={"pdf_path": pdf_path})

            return {
                "status"    : "success"
                , "message" : "PDF receipt processed successfully"
                , "data"    : {
                    "answer"            : answer
                    , "source_pages"    : len(documents)
                    , "pdf_path"        : pdf_path
                    , "question"        : question
                    , "vectorstore_path": str(persist_dir)
                }
            }

        except Exception as e:
            logger.error(f"Failed to process PDF: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to process PDF receipt: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("search_pdf_content_tool")
    def search_pdf_content(
        pdf_path        : str
        , search_query  : str
        , num_results   : int = 3
    ) -> Dict:
        """
        Search for specific information within a PDF document.
        Use this when you need to find specific details in a PDF.

        Args:
            pdf_path: Path to the PDF file
            search_query: What to search for in the PDF
            num_results: Number of relevant chunks to retrieve (default: 3)

        Returns:
            Dict containing search results

        Examples:
            - "Find the booking date in this PDF"
            - "Search for payment information"
            - "Look for guest name and contact details"
        """
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"PDF file not found: {pdf_path}"
                    , "data"    : None
                }

            loader      = PyPDFLoader(pdf_path)
            documents   = loader.load()

            if not documents:
                return {
                    "status"    : "error"
                    , "message" : "No content found in PDF"
                    , "data"    : None
                }

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size      = 500
                , chunk_overlap = 100
            )
            splits = text_splitter.split_documents(documents)

            embeddings = OllamaEmbeddings(
                base_url    = settings.OLLAMA_BASE_URL
                , model     = "llama3.1"
            )

            pdf_hash    = RAGTools._get_pdf_hash(pdf_path)
            persist_dir = RAGTools._get_persist_directory(pdf_hash)

            vectorstore = Chroma.from_documents(
                documents           = splits
                , embedding         = embeddings
                , persist_directory = str(persist_dir)
                , collection_name   = f"pdf_search_{pdf_hash}"
            )

            retriever       = vectorstore.as_retriever(search_kwargs={"k": num_results})
            relevant_docs   = retriever.invoke(search_query)

            results = []
            for i, doc in enumerate(relevant_docs):
                results.append({
                    "chunk_id"  : i + 1
                    , "content" : doc.page_content
                    , "page"    : doc.metadata.get("page", "unknown")
                    , "source"  : doc.metadata.get("source", pdf_path)
                })

            logger.info("PDF searched", extra={"pdf_path": pdf_path, "results": len(results)})

            return {
                "status"    : "success"
                , "message" : f"Found {len(results)} relevant sections"
                , "data"    : {
                    "results"           : results
                    , "total_pages"     : len(documents)
                    , "pdf_path"        : pdf_path
                    , "search_query"    : search_query
                    , "vectorstore_path": str(persist_dir)
                }
            }

        except Exception as e:
            logger.error(f"Failed to search PDF: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to search PDF content: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("extract_pdf_text_tool")
    def extract_pdf_text(pdf_path: str) -> Dict:
        """
        Extract all text content from a PDF file.
        Use this for simple text extraction without RAG.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dict containing extracted text
        """
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                return {
                    "status"    : "error"
                    , "message" : f"PDF file not found: {pdf_path}"
                    , "data"    : None
                }

            loader      = PyPDFLoader(pdf_path)
            documents   = loader.load()

            if not documents:
                return {
                    "status"    : "error"
                    , "message" : "No content found in PDF"
                    , "data"    : None
                }

            pages_content = []
            for i, doc in enumerate(documents):
                pages_content.append({
                    "page_number"   : i + 1
                    , "content"     : doc.page_content
                    , "metadata"    : doc.metadata
                })

            full_text = "\n\n".join([doc.page_content for doc in documents])

            output_dir  = Path("output") / "extracted_texts"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_name    = pdf_file.stem
            output_file = output_dir / f"{pdf_name}_{timestamp}.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Extracted from: {pdf_path}\n")
                f.write(f"Extraction date: {datetime.now().isoformat()}\n")
                f.write(f"Total pages: {len(documents)}\n")
                f.write("=" * 80 + "\n\n")
                f.write(full_text)

            logger.info("PDF text extracted", extra={"pdf_path": pdf_path, "pages": len(documents)})

            return {
                "status"    : "success"
                , "message" : f"Extracted text from {len(documents)} pages"
                , "data"    : {
                    "full_text"     : full_text
                    , "pages"       : pages_content
                    , "total_pages" : len(documents)
                    , "pdf_path"    : pdf_path
                    , "output_file" : str(output_file)
                }
            }

        except Exception as e:
            logger.error(f"Failed to extract PDF text: {str(e)}")
            return {
                "status"    : "error"
                , "message" : f"Failed to extract PDF text: {str(e)}"
                , "data"    : None
            }
