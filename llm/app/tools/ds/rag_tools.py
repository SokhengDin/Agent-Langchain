from typing import Dict, List, Optional, Annotated
from pathlib import Path
import fitz
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.config import settings
from app import logger

class DSRAGTools:
    """Tools for RAG on educational materials"""

    embeddings = OllamaEmbeddings(
        base_url    = settings.OLLAMA_BASE_URL
        , model     = "llama3.1"
    )

    vector_store = Chroma(
        collection_name     = "ds_documents"
        , embedding_function= embeddings
        , persist_directory = "output/ds_chromadb"
    )

    @staticmethod
    @tool("process_pdf_document")
    async def process_pdf_document(
        file_path   : str
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Process PDF document and store in vector database

        Args:
            file_path: Path to PDF file

        Returns:
            Dict with processing status
        """
        try:
            pdf_doc = fitz.open(file_path)
            text_content = []

            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                text = page.get_text()
                text_content.append({
                    "page"      : page_num + 1
                    , "content" : text
                })

            pdf_doc.close()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size      = 1000
                , chunk_overlap = 200
            )

            chunks = []
            metadatas = []

            for item in text_content:
                page_chunks = text_splitter.split_text(item["content"])
                for chunk in page_chunks:
                    chunks.append(chunk)
                    metadatas.append({
                        "source"    : file_path
                        , "page"    : item["page"]
                    })

            DSRAGTools.vector_store.add_texts(
                texts       = chunks
                , metadatas = metadatas
            )

            logger.info(f"Processed PDF: {file_path} - {len(chunks)} chunks")

            return {
                "status"    : 200
                , "message" : "PDF processed successfully"
                , "data"    : {
                    "file"          : file_path
                    , "pages"       : len(text_content)
                    , "chunks"      : len(chunks)
                }
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to process PDF: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("search_document_content")
    async def search_document_content(
        query   : str
        , k     : int = 5
        , state : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Search for relevant content in processed documents

        Args:
            query   : Search query
            k       : Number of results

        Returns:
            Dict with search results
        """
        try:
            results = DSRAGTools.vector_store.similarity_search(query, k=k)

            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content"   : doc.page_content
                    , "source"  : doc.metadata.get("source", "unknown")
                    , "page"    : doc.metadata.get("page", 0)
                })

            logger.info(f"Document search: '{query}' - {len(results)} results")

            return {
                "status"    : 200
                , "message" : "Search completed"
                , "data"    : {
                    "query"     : query
                    , "results" : formatted_results
                }
            }

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to search: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("extract_pdf_text")
    async def extract_pdf_text(
        file_path   : str
        , page_num  : Optional[int] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Extract raw text from PDF

        Args:
            file_path   : Path to PDF
            page_num    : Optional specific page (1-indexed)

        Returns:
            Dict with extracted text
        """
        try:
            pdf_doc = fitz.open(file_path)

            if page_num:
                if page_num < 1 or page_num > len(pdf_doc):
                    return {
                        "status"    : 400
                        , "message" : f"Invalid page number. PDF has {len(pdf_doc)} pages"
                        , "data"    : None
                    }
                text = pdf_doc[page_num - 1].get_text()
                pdf_doc.close()

                return {
                    "status"    : 200
                    , "message" : "Text extracted"
                    , "data"    : {
                        "page"  : page_num
                        , "text": text
                    }
                }
            else:
                all_text = []
                for page_idx in range(len(pdf_doc)):
                    all_text.append(pdf_doc[page_idx].get_text())
                pdf_doc.close()

                return {
                    "status"    : 200
                    , "message" : "Text extracted"
                    , "data"    : {
                        "pages" : len(all_text)
                        , "text": "\n\n".join(all_text)
                    }
                }

        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to extract text: {str(e)}"
                , "data"    : None
            }
