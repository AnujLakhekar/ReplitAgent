import os
import logging
import json
import time
from datetime import datetime

# Optional MongoDB support
MONGODB_AVAILABLE = False
try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError:
    logging.warning("MongoDB support not available. Install pymongo for MongoDB support.")

# Optional PostgreSQL support
POSTGRES_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    logging.warning("PostgreSQL support not available. Install psycopg2-binary for PostgreSQL support.")

class MemoryDBHelper:
    """
    A simple in-memory database that simulates database operations 
    when neither MongoDB nor PostgreSQL is available.
    """
    
    def __init__(self):
        """
        Initialize the in-memory database.
        """
        self.collections = {}  # Dictionary to store collections
        self.id_counter = {}   # Counter for generating IDs for each collection
        logging.warning("Using in-memory database. Data will be lost when the application is restarted.")
    
    def connect(self):
        """
        Simulated connect method.
        """
        return True
    
    def close(self):
        """
        Simulated close method.
        """
        pass
    
    def get_collections(self):
        """
        Get a list of all collections.
        
        Returns:
            list: List of collection names
        """
        return list(self.collections.keys())
    
    def create_document(self, collection_name, data):
        """
        Create a document in a collection.
        
        Args:
            collection_name (str): Name of the collection
            data (dict): Document data
        
        Returns:
            str: ID of the created document
        """
        # Ensure collection exists
        if collection_name not in self.collections:
            self.collections[collection_name] = []
            self.id_counter[collection_name] = 0
        
        # Clone data to avoid modifying the original
        document = data.copy()
        
        # Generate ID if not provided
        if '_id' not in document:
            self.id_counter[collection_name] += 1
            document['_id'] = str(self.id_counter[collection_name])
        
        # Add timestamps
        document['created_at'] = document.get('created_at', datetime.now())
        document['updated_at'] = document.get('updated_at', datetime.now())
        
        # Store document
        self.collections[collection_name].append(document)
        
        return document['_id']
    
    def get_document_by_id(self, collection_name, document_id):
        """
        Get a document by its ID.
        
        Args:
            collection_name (str): Name of the collection
            document_id (str): ID of the document
        
        Returns:
            dict: Document data or None if not found
        """
        if collection_name not in self.collections:
            return None
        
        for document in self.collections[collection_name]:
            if str(document.get('_id')) == str(document_id):
                return document.copy()
        
        return None
    
    def update_document(self, collection_name, document_id, data):
        """
        Update a document.
        
        Args:
            collection_name (str): Name of the collection
            document_id (str): ID of the document
            data (dict): New document data
        
        Returns:
            int: Number of modified documents (0 or 1)
        """
        if collection_name not in self.collections:
            return 0
        
        for i, document in enumerate(self.collections[collection_name]):
            if str(document.get('_id')) == str(document_id):
                # Update document with new data
                for key, value in data.items():
                    document[key] = value
                
                # Update timestamp
                document['updated_at'] = datetime.now()
                
                return 1
        
        return 0
    
    def delete_document(self, collection_name, document_id):
        """
        Delete a document.
        
        Args:
            collection_name (str): Name of the collection
            document_id (str): ID of the document
        
        Returns:
            int: Number of deleted documents (0 or 1)
        """
        if collection_name not in self.collections:
            return 0
        
        original_len = len(self.collections[collection_name])
        self.collections[collection_name] = [doc for doc in self.collections[collection_name] 
                                          if str(doc.get('_id')) != str(document_id)]
        
        return original_len - len(self.collections[collection_name])
    
    def list_documents(self, collection_name, query=None, limit=100, skip=0, sort=None):
        """
        List documents in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter
            limit (int): Maximum number of documents to return
            skip (int): Number of documents to skip
            sort (list): List of (key, direction) pairs for sort order
        
        Returns:
            list: List of documents
        """
        if collection_name not in self.collections:
            return []
        
        # Filter documents based on query
        results = self.collections[collection_name]
        if query:
            results = [doc for doc in results if self._matches_query(doc, query)]
        
        # Sort if specified
        if sort:
            for key, direction in reversed(sort):
                results = sorted(results, key=lambda doc: doc.get(key, None),
                               reverse=(direction < 0))
        
        # Apply skip and limit
        results = results[skip:skip + limit]
        
        # Return copies to avoid modifying stored data
        return [doc.copy() for doc in results]
    
    def count_documents(self, collection_name, query=None):
        """
        Count documents in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter
        
        Returns:
            int: Number of documents
        """
        if collection_name not in self.collections:
            return 0
        
        if query:
            return len([doc for doc in self.collections[collection_name] 
                      if self._matches_query(doc, query)])
        else:
            return len(self.collections[collection_name])
    
    def _matches_query(self, document, query):
        """
        Check if a document matches a query.
        
        Args:
            document (dict): Document to check
            query (dict): Query conditions
        
        Returns:
            bool: True if the document matches the query
        """
        for key, value in query.items():
            if key not in document or document[key] != value:
                return False
        return True

# PostgreSQL implementation if available
if POSTGRES_AVAILABLE:
    class PostgreSQLHelper:
        """
        Helper class for PostgreSQL operations.
        """
        
        def __init__(self, conn_string=None):
            """
            Initialize the PostgreSQL helper.
            
            Args:
                conn_string (str): PostgreSQL connection string
            """
            self.conn_string = conn_string or os.getenv("DATABASE_URL")
            if not self.conn_string:
                raise ValueError("PostgreSQL connection string not provided and DATABASE_URL environment variable not set")
            
            self.conn = None
        
        def connect(self):
            """
            Connect to the PostgreSQL database.
            
            Returns:
                psycopg2.extensions.connection: Connection object
            """
            try:
                if self.conn is None or self.conn.closed:
                    self.conn = psycopg2.connect(self.conn_string)
                    self.conn.autocommit = False
                    logging.info("Connected to PostgreSQL database")
                return self.conn
            except Exception as e:
                logging.error(f"Error connecting to PostgreSQL: {str(e)}")
                raise
        
        def close(self):
            """
            Close the PostgreSQL connection.
            """
            if self.conn and not self.conn.closed:
                self.conn.close()
                self.conn = None
                logging.info("PostgreSQL connection closed")
        
        def execute_query(self, query, params=None, fetchall=True):
            """
            Execute a PostgreSQL query.
            
            Args:
                query (str): SQL query
                params (tuple or dict): Query parameters
                fetchall (bool): Whether to fetch all results
            
            Returns:
                list or dict: Query results
            """
            conn = self.connect()
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith(("SELECT", "SHOW", "WITH")):
                        if fetchall:
                            return cursor.fetchall()
                        else:
                            return cursor.fetchone()
                    else:
                        conn.commit()
                        if cursor.rowcount >= 0:
                            return cursor.rowcount
                        return None
            except Exception as e:
                conn.rollback()
                logging.error(f"Error executing query: {str(e)}")
                raise
        
        def get_collections(self):
            """
            Get a list of all tables in the database.
            
            Returns:
                list: List of table names
            """
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
            """
            tables = self.execute_query(query)
            return [table['table_name'] for table in tables]
        
        def create_document(self, collection_name, data):
            """
            Insert a record into a table.
            
            Args:
                collection_name (str): Table name
                data (dict): Record data
            
            Returns:
                str: ID of the created record
            """
            # Check if table exists, create if not
            self._ensure_table_exists(collection_name, data)
            
            # Add timestamp if not present
            if 'created_at' not in data:
                data['created_at'] = datetime.now()
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f'%({key})s' for key in data.keys()])
            
            query = f"""
            INSERT INTO {collection_name} ({columns}) 
            VALUES ({placeholders}) 
            RETURNING id;
            """
            
            result = self.execute_query(query, data, fetchall=False)
            return str(result['id'])
        
        def get_document_by_id(self, collection_name, document_id):
            """
            Get a record by its ID.
            
            Args:
                collection_name (str): Table name
                document_id (str): ID of the record
            
            Returns:
                dict: Record data
            """
            query = f"SELECT * FROM {collection_name} WHERE id = %s;"
            return self.execute_query(query, (document_id,), fetchall=False)
        
        def update_document(self, collection_name, document_id, data):
            """
            Update a record.
            
            Args:
                collection_name (str): Table name
                document_id (str): ID of the record
                data (dict): New record data
            
            Returns:
                int: Number of updated records
            """
            # Add updated_at timestamp
            data['updated_at'] = datetime.now()
            
            set_clause = ', '.join([f"{key} = %({key})s" for key in data.keys()])
            data['id'] = document_id
            
            query = f"""
            UPDATE {collection_name} 
            SET {set_clause} 
            WHERE id = %(id)s;
            """
            
            return self.execute_query(query, data)
        
        def delete_document(self, collection_name, document_id):
            """
            Delete a record.
            
            Args:
                collection_name (str): Table name
                document_id (str): ID of the record
            
            Returns:
                int: Number of deleted records
            """
            query = f"DELETE FROM {collection_name} WHERE id = %s;"
            return self.execute_query(query, (document_id,))
        
        def list_documents(self, collection_name, query=None, limit=100, skip=0, sort=None):
            """
            List records in a table.
            
            Args:
                collection_name (str): Table name
                query (dict): Query conditions
                limit (int): Maximum number of records to return
                skip (int): Number of records to skip
                sort (list): List of (column, direction) pairs for sort order
            
            Returns:
                list: List of records
            """
            # Build WHERE clause from query dict
            where_clause = ""
            params = {}
            
            if query:
                conditions = []
                for key, value in query.items():
                    conditions.append(f"{key} = %({key})s")
                    params[key] = value
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            # Build ORDER BY clause
            order_clause = ""
            if sort:
                sort_items = []
                for key, direction in sort:
                    dir_str = "ASC" if direction > 0 else "DESC"
                    sort_items.append(f"{key} {dir_str}")
                
                if sort_items:
                    order_clause = "ORDER BY " + ", ".join(sort_items)
            
            # Build complete query
            query_str = f"""
            SELECT * FROM {collection_name} 
            {where_clause} 
            {order_clause} 
            LIMIT {limit} OFFSET {skip};
            """
            
            return self.execute_query(query_str, params)
        
        def count_documents(self, collection_name, query=None):
            """
            Count records in a table.
            
            Args:
                collection_name (str): Table name
                query (dict): Query conditions
            
            Returns:
                int: Number of records
            """
            # Build WHERE clause from query dict
            where_clause = ""
            params = {}
            
            if query:
                conditions = []
                for key, value in query.items():
                    conditions.append(f"{key} = %({key})s")
                    params[key] = value
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            query_str = f"""
            SELECT COUNT(*) as count FROM {collection_name} 
            {where_clause};
            """
            
            result = self.execute_query(query_str, params, fetchall=False)
            return result['count']
        
        def _ensure_table_exists(self, table_name, sample_data):
            """
            Ensure that a table exists, create it if it doesn't.
            
            Args:
                table_name (str): Table name
                sample_data (dict): Sample data to infer schema
            """
            # Check if table exists
            check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
            """
            
            result = self.execute_query(check_query, (table_name,), fetchall=False)
            if result and result['exists']:
                return
            
            # Create table based on sample data
            columns = []
            for key, value in sample_data.items():
                col_type = self._infer_column_type(value)
                columns.append(f"{key} {col_type}")
            
            # Ensure id, created_at, updated_at columns
            if 'id' not in sample_data:
                columns.insert(0, "id SERIAL PRIMARY KEY")
            if 'created_at' not in sample_data:
                columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            if 'updated_at' not in sample_data:
                columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            create_query = f"""
            CREATE TABLE {table_name} (
                {', '.join(columns)}
            );
            """
            
            self.execute_query(create_query)
            logging.info(f"Created table: {table_name}")
        
        def _infer_column_type(self, value):
            """
            Infer PostgreSQL column type from a Python value.
            
            Args:
                value: Python value
            
            Returns:
                str: PostgreSQL column type
            """
            if isinstance(value, int):
                return "INTEGER"
            elif isinstance(value, float):
                return "NUMERIC"
            elif isinstance(value, bool):
                return "BOOLEAN"
            elif isinstance(value, datetime):
                return "TIMESTAMP"
            elif isinstance(value, dict) or isinstance(value, list):
                return "JSONB"
            else:
                return "TEXT"

# MongoDB implementation if available
if MONGODB_AVAILABLE:
    class MongoDBHelper:
        """
        Helper class for MongoDB operations.
        """
        
        def __init__(self, uri=None, db_name=None):
            """
            Initialize the MongoDB helper.
            
            Args:
                uri (str): MongoDB connection URI
                db_name (str): Database name
            """
            self.uri = uri or os.getenv("MONGO_URI")
            if not self.uri:
                raise ValueError("MongoDB URI not provided and MONGO_URI environment variable not set")
            
            self.db_name = db_name or os.getenv("MONGO_DB_NAME", "replit_agent_db")
            self.client = None
            self.db = None
        
        def connect(self):
            """
            Connect to the MongoDB database.
            
            Returns:
                pymongo.database.Database: Database object
            """
            try:
                if self.client is None:
                    self.client = MongoClient(self.uri)
                    self.db = self.client[self.db_name]
                    logging.info(f"Connected to MongoDB database: {self.db_name}")
                return self.db
            except Exception as e:
                logging.error(f"Error connecting to MongoDB: {str(e)}")
                raise
        
        def close(self):
            """
            Close the MongoDB connection.
            """
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                logging.info("MongoDB connection closed")
        
        def get_collection(self, collection_name):
            """
            Get a MongoDB collection.
            
            Args:
                collection_name (str): Name of the collection
            
            Returns:
                pymongo.collection.Collection: Collection object
            """
            if self.db is None:
                self.connect()
            return self.db[collection_name]
        
        def create_document(self, collection_name, data):
            """
            Create a document in a collection.
            
            Args:
                collection_name (str): Name of the collection
                data (dict): Document data
            
            Returns:
                str: ID of the created document
            """
            try:
                collection = self.get_collection(collection_name)
                result = collection.insert_one(data)
                return str(result.inserted_id)
            except Exception as e:
                logging.error(f"Error creating document in {collection_name}: {str(e)}")
                raise
        
        def get_document_by_id(self, collection_name, document_id):
            """
            Get a document by its ID.
            
            Args:
                collection_name (str): Name of the collection
                document_id (str): ID of the document
            
            Returns:
                dict: Document data
            """
            try:
                collection = self.get_collection(collection_name)
                result = collection.find_one({"_id": ObjectId(document_id)})
                return self._process_document(result) if result else None
            except Exception as e:
                logging.error(f"Error getting document {document_id} from {collection_name}: {str(e)}")
                raise
        
        def update_document(self, collection_name, document_id, data):
            """
            Update a document.
            
            Args:
                collection_name (str): Name of the collection
                document_id (str): ID of the document
                data (dict): New document data
            
            Returns:
                int: Number of modified documents
            """
            try:
                collection = self.get_collection(collection_name)
                result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": data})
                return result.modified_count
            except Exception as e:
                logging.error(f"Error updating document {document_id} in {collection_name}: {str(e)}")
                raise
        
        def delete_document(self, collection_name, document_id):
            """
            Delete a document.
            
            Args:
                collection_name (str): Name of the collection
                document_id (str): ID of the document
            
            Returns:
                int: Number of deleted documents
            """
            try:
                collection = self.get_collection(collection_name)
                result = collection.delete_one({"_id": ObjectId(document_id)})
                return result.deleted_count
            except Exception as e:
                logging.error(f"Error deleting document {document_id} from {collection_name}: {str(e)}")
                raise
        
        def list_documents(self, collection_name, query=None, limit=100, skip=0, sort=None):
            """
            List documents in a collection.
            
            Args:
                collection_name (str): Name of the collection
                query (dict): Query filter
                limit (int): Maximum number of documents to return
                skip (int): Number of documents to skip
                sort (list): List of (key, direction) pairs for sort order
            
            Returns:
                list: List of documents
            """
            try:
                collection = self.get_collection(collection_name)
                cursor = collection.find(query or {}).limit(limit).skip(skip)
                
                if sort:
                    cursor = cursor.sort(sort)
                
                return [self._process_document(doc) for doc in cursor]
            except Exception as e:
                logging.error(f"Error listing documents in {collection_name}: {str(e)}")
                raise
        
        def count_documents(self, collection_name, query=None):
            """
            Count documents in a collection.
            
            Args:
                collection_name (str): Name of the collection
                query (dict): Query filter
            
            Returns:
                int: Number of documents
            """
            try:
                collection = self.get_collection(collection_name)
                return collection.count_documents(query or {})
            except Exception as e:
                logging.error(f"Error counting documents in {collection_name}: {str(e)}")
                raise
        
        def get_collections(self):
            """
            Get a list of all collections in the database.
            
            Returns:
                list: List of collection names
            """
            try:
                if self.db is None:
                    self.connect()
                return self.db.list_collection_names()
            except Exception as e:
                logging.error(f"Error getting collections: {str(e)}")
                raise
        
        def _process_document(self, document):
            """
            Process a document, converting ObjectId to string.
            
            Args:
                document (dict): Document to process
            
            Returns:
                dict: Processed document
            """
            if document is None:
                return None
            
            result = document.copy()
            if '_id' in result and isinstance(result['_id'], ObjectId):
                result['_id'] = str(result['_id'])
            
            return result

# Create singleton instances for easy access
_db_helper = None

def get_db_helper():
    """
    Get a database helper instance based on what's available.
    Prioritize PostgreSQL, then MongoDB, then in-memory.
    
    Returns:
        Database helper instance
    """
    global _db_helper
    
    if _db_helper:
        return _db_helper
    
    # Try PostgreSQL first (since we created one with create_postgresql_database_tool)
    if POSTGRES_AVAILABLE and os.getenv("DATABASE_URL"):
        try:
            _db_helper = PostgreSQLHelper()
            logging.info("Using PostgreSQL database")
            return _db_helper
        except Exception as e:
            logging.error(f"Failed to initialize PostgreSQL: {str(e)}")
    
    # Fall back to MongoDB if available and configured
    if MONGODB_AVAILABLE and os.getenv("MONGO_URI"):
        try:
            _db_helper = MongoDBHelper()
            logging.info("Using MongoDB database")
            return _db_helper
        except Exception as e:
            logging.error(f"Failed to initialize MongoDB: {str(e)}")
    
    # Fall back to in-memory database as last resort
    _db_helper = MemoryDBHelper()
    logging.info("Using in-memory database (data will not persist)")
    return _db_helper

# Convenience functions that use the global helper instance

def create_document(collection_name, data):
    """
    Create a document in a collection.
    
    Args:
        collection_name (str): Name of the collection
        data (dict): Document data
    
    Returns:
        str: ID of the created document
    """
    return get_db_helper().create_document(collection_name, data)

def get_document_by_id(collection_name, document_id):
    """
    Get a document by its ID.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document
    
    Returns:
        dict: Document data
    """
    return get_db_helper().get_document_by_id(collection_name, document_id)

def update_document(collection_name, document_id, data):
    """
    Update a document.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document
        data (dict): New document data
    
    Returns:
        int: Number of modified documents
    """
    return get_db_helper().update_document(collection_name, document_id, data)

def delete_document(collection_name, document_id):
    """
    Delete a document.
    
    Args:
        collection_name (str): Name of the collection
        document_id (str): ID of the document
    
    Returns:
        int: Number of deleted documents
    """
    return get_db_helper().delete_document(collection_name, document_id)

def list_documents(collection_name, query=None, limit=100, skip=0, sort=None):
    """
    List documents in a collection.
    
    Args:
        collection_name (str): Name of the collection
        query (dict): Query filter
        limit (int): Maximum number of documents to return
        skip (int): Number of documents to skip
        sort (list): List of (key, direction) pairs for sort order
    
    Returns:
        list: List of documents
    """
    return get_db_helper().list_documents(collection_name, query, limit, skip, sort)

def count_documents(collection_name, query=None):
    """
    Count documents in a collection.
    
    Args:
        collection_name (str): Name of the collection
        query (dict): Query filter
    
    Returns:
        int: Number of documents
    """
    return get_db_helper().count_documents(collection_name, query)

def get_collections():
    """
    Get a list of all collections in the database.
    
    Returns:
        list: List of collection names
    """
    return get_db_helper().get_collections()

def close_db_connection():
    """
    Close the database connection.
    """
    global _db_helper
    if _db_helper is not None:
        _db_helper.close()
        _db_helper = None