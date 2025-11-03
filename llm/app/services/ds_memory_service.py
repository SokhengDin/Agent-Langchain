from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.documents import Document
from langchain_chroma import Chroma

from app import logger

class DSMemoryService:
    """Memory service for data science agent"""

    def __init__(self, memory_store: Chroma):
        self.memory_store = memory_store

    def save_analysis_memory(
        self
        , thread_id     : str
        , dataset_path  : str
        , analysis_type : str
        , results       : Dict[str, Any]
    ) -> bool:
        """Save analysis results to memory"""
        try:
            content = f"Analysis performed on {dataset_path}: {analysis_type}"

            metadata = {
                "thread_id"     : thread_id
                , "memory_type" : "analysis"
                , "dataset_path": dataset_path
                , "analysis_type": analysis_type
                , "timestamp"   : datetime.now().isoformat()
            }

            memory_doc = Document(
                page_content = content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Saved analysis memory: {analysis_type} on {dataset_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving analysis memory: {str(e)}")
            return False

    def save_dataset_info(
        self
        , thread_id     : str
        , dataset_path  : str
        , dataset_info  : Dict[str, Any]
    ) -> bool:
        """Save dataset metadata"""
        try:
            content = f"Dataset loaded: {dataset_path} ({dataset_info.get('rows', 0)} rows, {dataset_info.get('columns', 0)} columns)"

            metadata = {
                "thread_id"     : thread_id
                , "memory_type" : "dataset"
                , "dataset_path": dataset_path
                , "timestamp"   : datetime.now().isoformat()
            }

            memory_doc = Document(
                page_content = content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Saved dataset info: {dataset_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving dataset info: {str(e)}")
            return False

    def recall_memories(
        self
        , query     : str
        , thread_id : Optional[str] = None
        , limit     : int = 5
    ) -> List[str]:
        """Recall relevant memories"""
        try:
            filter_dict = {}
            if thread_id:
                filter_dict = {"thread_id": {"$eq": thread_id}}

            if filter_dict:
                docs = self.memory_store.similarity_search(
                    query   = query
                    , k     = limit
                    , filter= filter_dict
                )
            else:
                docs = self.memory_store.similarity_search(query, k=limit)

            memories = [doc.page_content for doc in docs]
            logger.info(f"Retrieved {len(memories)} memories")
            return memories

        except Exception as e:
            logger.error(f"Error recalling memories: {str(e)}")
            return []

    def get_thread_datasets(self, thread_id: str) -> List[str]:
        """Get all datasets used in a thread"""
        try:
            results = self.memory_store.get(
                where = {
                    "$and": [
                        {"thread_id": {"$eq": thread_id}},
                        {"memory_type": {"$eq": "dataset"}}
                    ]
                }
            )

            if not results['metadatas']:
                return []

            datasets = [m.get("dataset_path") for m in results['metadatas'] if m.get("dataset_path")]
            return list(set(datasets))

        except Exception as e:
            logger.error(f"Error getting thread datasets: {str(e)}")
            return []
