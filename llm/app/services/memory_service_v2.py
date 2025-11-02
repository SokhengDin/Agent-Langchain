from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import json

from langchain_core.documents import Document
from langchain_chroma import Chroma

from app import logger


class MemoryServiceV2:
    """
    Synchronous Memory Service for v2 (used with sync middleware)
    """

    def __init__(self, memory_store: Chroma):
        """
        Initialize the memory service with a vector store

        Parameters:
        memory_store : Chroma
            Vector store for storing and retrieving memories
        """
        self.memory_store = memory_store

    def save_guest_preference(
        self
        , guest_id          : UUID
        , preference_type   : str
        , value             : str
        , thread_id         : Optional[str] = None
    ) -> bool:
        """
        Save a guest preference to memory for future reference
        """
        try:
            content = f"Guest {guest_id} prefers {preference_type}: {value}"

            metadata = {
                "guest_id"          : str(guest_id)
                , "memory_type"     : "preference"
                , "preference_type" : preference_type
                , "value"           : value
                , "timestamp"       : datetime.now().isoformat()
                , "cross_thread"    : True
            }

            if thread_id:
                metadata["thread_id"] = thread_id

            memory_doc = Document(
                page_content = content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Saved preference for guest {guest_id}: {preference_type}={value}")
            return True

        except Exception as e:
            logger.error(f"Error saving guest preference: {str(e)}")
            return False

    def save_booking_memory(
        self
        , guest_id      : UUID
        , booking_id    : Optional[UUID] = None
        , hotel_id      : Optional[UUID] = None
        , room_id       : Optional[UUID] = None
        , check_in      : Optional[str] = None
        , check_out     : Optional[str] = None
        , num_guests    : Optional[int] = None
        , details       : Optional[Dict] = None
        , thread_id     : Optional[str] = None
    ) -> bool:
        """
        Save booking information to memory
        """
        try:
            content_parts = [f"Guest {guest_id} booking memory:"]

            if booking_id:
                content_parts.append(f"Booking ID: {booking_id}")

            if hotel_id:
                content_parts.append(f"Hotel ID: {hotel_id}")

            if room_id:
                content_parts.append(f"Room ID: {room_id}")

            if check_in and check_out:
                content_parts.append(f"Stay period: {check_in} to {check_out}")

            if num_guests:
                content_parts.append(f"Number of guests: {num_guests}")

            if details:
                content_parts.append(f"Additional details: {json.dumps(details)}")

            content = " | ".join(content_parts)

            metadata = {
                "guest_id"      : str(guest_id)
                , "memory_type" : "booking"
                , "timestamp"   : datetime.now().isoformat()
                , "cross_thread": True
            }

            if booking_id:
                metadata["booking_id"] = str(booking_id)

            if hotel_id:
                metadata["hotel_id"] = str(hotel_id)

            if room_id:
                metadata["room_id"] = str(room_id)

            if check_in:
                metadata["check_in"] = check_in

            if check_out:
                metadata["check_out"] = check_out

            if num_guests:
                metadata["num_guests"] = num_guests

            if thread_id:
                metadata["thread_id"] = thread_id

            memory_doc = Document(
                page_content = content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Saved booking memory for guest {guest_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving booking memory: {str(e)}")
            return False

    def save_interaction_memory(
        self
        , thread_id     : str
        , content       : str
        , guest_id      : Optional[UUID] = None
        , category      : Optional[str] = None
        , summary       : Optional[str] = None
    ) -> bool:
        """
        Save an interaction to memory
        """
        try:
            metadata = {
                "thread_id"     : thread_id
                , "memory_type" : "interaction"
                , "category"    : category or "general"
                , "timestamp"   : datetime.now().isoformat()
                , "cross_thread": True
            }

            if guest_id:
                metadata["guest_id"] = str(guest_id)

            page_content = content
            if summary:
                page_content = f"SUMMARY: {summary}\n\nDETAILS: {content}"

            memory_doc = Document(
                page_content = page_content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Saved interaction memory for thread {thread_id}" +
                       (f" and guest {guest_id}" if guest_id else ""))
            return True

        except Exception as e:
            logger.error(f"Error saving interaction memory: {str(e)}")
            return False

    def link_guest_to_thread(
        self
        , guest_id  : UUID
        , thread_id : str
    ) -> bool:
        """
        Link a guest to a conversation thread
        """
        try:
            content = f"Guest {guest_id} is linked to conversation thread {thread_id}"

            metadata = {
                "guest_id"      : str(guest_id)
                , "thread_id"   : thread_id
                , "memory_type" : "thread_link"
                , "timestamp"   : datetime.now().isoformat()
                , "cross_thread": True
            }

            memory_doc = Document(
                page_content = content
                , metadata   = metadata
            )

            self.memory_store.add_documents([memory_doc])
            logger.info(f"Linked guest {guest_id} to thread {thread_id}")
            return True

        except Exception as e:
            logger.error(f"Error linking guest to thread: {str(e)}")
            return False

    def get_thread_guest(
        self
        , thread_id : str
    ) -> Optional[str]:
        """
        Get the guest ID associated with a thread
        """
        try:
            results = self.memory_store.get(
                where = {
                    "$and": [
                        {"thread_id": {"$eq": thread_id}},
                        {"memory_type": {"$eq": "thread_link"}}
                    ]
                }
            )

            if not results['metadatas'] or len(results['metadatas']) == 0:
                return None

            return results['metadatas'][0].get("guest_id")

        except Exception as e:
            logger.error(f"Error getting thread guest: {str(e)}")
            return None

    def recall_memories(
        self
        , query     : str
        , guest_id  : Optional[UUID] = None
        , thread_id : Optional[str] = None
        , limit     : int = 5
        , filter_type: Optional[str] = None
    ) -> List[str]:
        """
        Recall relevant memories based on similarity search
        """
        try:
            filter_conditions = []

            if guest_id:
                filter_conditions.append({"guest_id": {"$eq": str(guest_id)}})

            if thread_id:
                filter_conditions.append({"thread_id": {"$eq": thread_id}})

            if filter_type:
                filter_conditions.append({"memory_type": {"$eq": filter_type}})

            filter_dict = {}
            if len(filter_conditions) > 1:
                filter_dict = {"$and": filter_conditions}
            elif len(filter_conditions) == 1:
                filter_dict = filter_conditions[0]

            if filter_dict:
                docs = self.memory_store.similarity_search(
                    query       = query
                    , k         = limit
                    , filter    = filter_dict
                )
            else:
                docs = self.memory_store.similarity_search(
                    query   = query
                    , k     = limit
                )

            memories = [doc.page_content for doc in docs]
            logger.info(f"Retrieved {len(memories)} memories for query")
            return memories

        except Exception as e:
            logger.error(f"Error recalling memories: {str(e)}")
            return []

    def get_guest_preferences(
        self
        , guest_id  : UUID
    ) -> Dict[str, str]:
        """
        Get all preferences for a guest
        """
        try:
            results = self.memory_store.get(
                where = {
                    "$and": [
                        {"guest_id": {"$eq": str(guest_id)}},
                        {"memory_type": {"$eq": "preference"}}
                    ]
                }
            )

            if not results['metadatas'] or len(results['metadatas']) == 0:
                return {}

            preferences = {}
            for metadata in results['metadatas']:
                pref_type = metadata.get("preference_type")
                value = metadata.get("value")

                if pref_type and value:
                    preferences[pref_type] = value

            return preferences

        except Exception as e:
            logger.error(f"Error getting guest preferences: {str(e)}")
            return {}

    def get_guest_bookings(
        self
        , guest_id  : UUID
    ) -> List[Dict]:
        """
        Get all booking memories for a guest
        """
        try:
            results = self.memory_store.get(
                where = {
                    "$and": [
                        {"guest_id": {"$eq": str(guest_id)}},
                        {"memory_type": {"$eq": "booking"}}
                    ]
                }
            )

            if not results['metadatas'] or len(results['metadatas']) == 0:
                return []

            bookings = []
            for metadata in results['metadatas']:
                booking_data = {k: v for k, v in metadata.items()
                            if k not in ["cross_thread", "memory_type"]}
                bookings.append(booking_data)

            bookings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return bookings

        except Exception as e:
            logger.error(f"Error getting guest bookings: {str(e)}")
            return []

    def clear_thread_memories(
        self
        , thread_id : str
    ) -> bool:
        """
        Clear all memories for a specific thread
        """
        try:
            results = self.memory_store.get(
                where = {"thread_id": {"$eq": thread_id}}
            )

            if not results['ids'] or len(results['ids']) == 0:
                return True

            self.memory_store.delete(ids=results['ids'])
            logger.info(f"Cleared {len(results['ids'])} memories for thread {thread_id}")
            return True

        except Exception as e:
            logger.error(f"Error clearing thread memories: {str(e)}")
            return False
