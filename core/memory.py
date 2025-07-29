"""
Memory System - NOVA's long-term and short-term memory

Handles storage, retrieval, and management of all information NOVA learns,
including user preferences, conversation history, and learned patterns.
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available, using fallback memory system")
import logging


@dataclass
class Memory:
    """Represents a single memory item"""
    id: str
    content: str
    type: str  # conversation, pattern, preference, fact
    importance: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class MemorySystem:
    """
    NOVA's hybrid memory system combining vector and relational storage
    """
    
    def __init__(self, db_path: str = "data/nova_memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("nova.memory")
        
        # Vector database for semantic search
        self.chroma_client = None
        self.memory_collection = None
        
        # SQLite for structured data
        self.sql_connection = None
        
        # In-memory cache for frequent access
        self.cache = {}
        self.max_cache_size = 1000
    
    async def initialize(self):
        """Initialize the memory system"""
        try:
            self.logger.info("🧠 Initializing memory system...")
            
            # Initialize ChromaDB for vector storage (if available)
            if CHROMADB_AVAILABLE:
                # Use new ChromaDB API
                self.chroma_client = chromadb.PersistentClient(
                    path="data/chroma_db"
                )
                
                self.memory_collection = self.chroma_client.get_or_create_collection(
                    name="nova_memories",
                    metadata={"hnsw:space": "cosine"}
                )
            else:
                self.logger.warning("ChromaDB not available, using basic memory system")
                self.chroma_client = None
                self.memory_collection = None
            
            # Initialize SQLite for structured data
            self.sql_connection = sqlite3.connect(self.db_path)
            await self._create_tables()
            
            self.logger.info("✅ Memory system initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Memory initialization failed: {e}")
            raise
    
    async def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.sql_connection.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_input TEXT,
                nova_response TEXT,
                timestamp TEXT,
                context TEXT,
                satisfaction_score REAL
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT,
                pattern_data TEXT,
                confidence_score REAL,
                usage_count INTEGER,
                last_used TEXT
            )
        ''')
        
        # Facts and knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                category TEXT,
                fact TEXT,
                source TEXT,
                reliability_score REAL,
                created_at TEXT
            )
        ''')
        
        self.sql_connection.commit()
    
    async def store_interaction(self, input_data: Dict[str, Any]) -> str:
        """Store a user interaction in memory"""
        try:
            memory_id = f"interaction_{datetime.now().isoformat()}"
            
            # Store in vector database for semantic search (if available)
            if self.memory_collection:
                self.memory_collection.add(
                    documents=[json.dumps(input_data)],
                    metadatas=[{
                        "type": "interaction",
                        "timestamp": datetime.now().isoformat(),
                        "input_type": input_data.get("type", "unknown")
                    }],
                    ids=[memory_id]
                )
            
            # Store structured data in SQLite
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                INSERT INTO conversations (id, user_input, timestamp, context)
                VALUES (?, ?, ?, ?)
            ''', (
                memory_id,
                input_data.get("content", ""),
                datetime.now().isoformat(),
                json.dumps(input_data.get("context", {}))
            ))
            self.sql_connection.commit()
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {e}")
            return ""
    
    async def store_pattern(self, input_data: Dict[str, Any], response: Dict[str, Any]):
        """Store successful interaction patterns for learning"""
        try:
            pattern_id = f"pattern_{datetime.now().isoformat()}"
            
            pattern_data = {
                "input": input_data,
                "response": response,
                "success_indicators": self._extract_success_indicators(input_data, response)
            }
            
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO patterns 
                (id, pattern_type, pattern_data, confidence_score, usage_count, last_used)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (
                pattern_id,
                input_data.get("type", "general"),
                json.dumps(pattern_data),
                0.5,  # Initial confidence
                datetime.now().isoformat()
            ))
            self.sql_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing pattern: {e}")
    
    async def retrieve_similar_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories similar to the given query"""
        try:
            if not self.memory_collection:
                # Fallback to simple text search in SQLite
                return await self._fallback_search(query, limit)
            
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            memories = []
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    "content": json.loads(doc),
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error retrieving memories: {e}")
            return []
    
    async def _fallback_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search using SQLite when ChromaDB is not available"""
        try:
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                SELECT user_input, context, timestamp
                FROM conversations 
                WHERE user_input LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f"%{query}%", limit))
            
            memories = []
            for row in cursor.fetchall():
                memory = {
                    "content": {
                        "content": row[0],
                        "context": json.loads(row[1]) if row[1] else {},
                        "timestamp": row[2]
                    },
                    "metadata": {"type": "conversation", "timestamp": row[2]},
                    "distance": 0.5  # Default similarity
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error in fallback search: {e}")
            return []
    
    async def get_user_preference(self, key: str) -> Optional[str]:
        """Get a user preference value"""
        try:
            # Check cache first
            if key in self.cache:
                return self.cache[key]
            
            cursor = self.sql_connection.cursor()
            cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            if result:
                value = result[0]
                self.cache[key] = value
                return value
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting preference: {e}")
            return None
    
    async def set_user_preference(self, key: str, value: str):
        """Set a user preference"""
        try:
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, datetime.now().isoformat()))
            self.sql_connection.commit()
            
            # Update cache
            self.cache[key] = value
            
            # Manage cache size
            if len(self.cache) > self.max_cache_size:
                # Remove oldest entries
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
        except Exception as e:
            self.logger.error(f"Error setting preference: {e}")
    
    async def store_knowledge(self, category: str, fact: str, source: str, reliability: float = 0.8):
        """Store a piece of knowledge/fact"""
        try:
            knowledge_id = f"fact_{datetime.now().isoformat()}"
            
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                INSERT INTO knowledge (id, category, fact, source, reliability_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                knowledge_id,
                category,
                fact,
                source,
                reliability,
                datetime.now().isoformat()
            ))
            self.sql_connection.commit()
            
            # Also store in vector database for semantic search (if available)
            if self.memory_collection:
                self.memory_collection.add(
                    documents=[fact],
                    metadatas=[{
                        "type": "knowledge",
                        "category": category,
                        "source": source,
                        "reliability": reliability,
                        "timestamp": datetime.now().isoformat()
                    }],
                    ids=[knowledge_id]
                )
            
        except Exception as e:
            self.logger.error(f"Error storing knowledge: {e}")
    
    async def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        try:
            cursor = self.sql_connection.cursor()
            cursor.execute('''
                SELECT user_input, nova_response, timestamp, context
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "user_input": row[0],
                    "nova_response": row[1],
                    "timestamp": row[2],
                    "context": json.loads(row[3]) if row[3] else {}
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _extract_success_indicators(self, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract indicators of successful interactions"""
        indicators = {
            "response_time": response.get("processing_time", 0),
            "user_satisfaction": input_data.get("satisfaction", 0.5),
            "task_completed": response.get("task_completed", False),
            "error_occurred": "error" in response
        }
        return indicators
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            cursor = self.sql_connection.cursor()
            
            # Count different types of memories
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversation_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM preferences')
            preference_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM patterns')
            pattern_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            knowledge_count = cursor.fetchone()[0]
            
            # Vector database stats (if available)
            vector_count = 0
            if self.memory_collection:
                vector_count = self.memory_collection.count()
            
            return {
                "conversations": conversation_count,
                "preferences": preference_count,
                "patterns": pattern_count,
                "knowledge": knowledge_count,
                "vector_memories": vector_count,
                "cache_size": len(self.cache),
                "chromadb_available": CHROMADB_AVAILABLE
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup memory system resources"""
        try:
            if self.sql_connection:
                self.sql_connection.close()
            
            # Clear cache
            self.cache.clear()
            
            self.logger.info("🧹 Memory system cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def backup_memories(self, backup_path: str):
        """Create a backup of all memories"""
        # Implementation for backing up memories
        pass
    
    async def restore_memories(self, backup_path: str):
        """Restore memories from backup"""
        # Implementation for restoring memories
        pass
