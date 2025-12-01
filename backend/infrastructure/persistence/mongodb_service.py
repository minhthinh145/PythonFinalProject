"""
MongoDB Service - Connection and utilities for MongoDB operations
Used for TKB caching and document storage
"""
from typing import Optional, Dict, Any, List
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Lazy-load pymongo to avoid import errors if not installed
_mongo_client = None
_mongo_db = None


def get_mongo_client():
    """Get MongoDB client (singleton pattern)"""
    global _mongo_client
    
    if _mongo_client is None:
        try:
            from pymongo import MongoClient
            from pymongo.server_api import ServerApi
            
            mongodb_url = config('MONGODB_URL', default=None)
            
            if not mongodb_url:
                logger.warning("MONGODB_URL not configured, MongoDB features disabled")
                return None
            
            _mongo_client = MongoClient(
                mongodb_url,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            
            # Test connection
            _mongo_client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully")
            
        except ImportError:
            logger.error("❌ pymongo not installed. Run: pip install pymongo dnspython")
            return None
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            _mongo_client = None
            return None
    
    return _mongo_client


def get_mongo_db(db_name: str = None):
    """Get MongoDB database instance"""
    global _mongo_db
    
    client = get_mongo_client()
    if client is None:
        return None
    
    if _mongo_db is None:
        # Extract db name from URL or use provided
        if db_name is None:
            db_name = config('MONGODB_DB_NAME', default='dkhp_tkb')
        _mongo_db = client[db_name]
    
    return _mongo_db


class MongoDBService:
    """
    MongoDB Service for document operations
    
    Collections:
    - tkb_cache: Cache TKB data
    - tai_lieu: Store document metadata
    """
    
    def __init__(self):
        self.db = get_mongo_db()
    
    @property
    def is_available(self) -> bool:
        """Check if MongoDB is available"""
        return self.db is not None
    
    # ============ TKB CACHE OPERATIONS ============
    
    def cache_tkb(self, sinh_vien_id: str, hoc_ky_id: str, tkb_data: List[Dict]) -> bool:
        """Cache TKB data for a student"""
        if not self.is_available:
            logger.warning("MongoDB not available, skipping cache")
            return False
        
        try:
            collection = self.db['tkb_cache']
            
            # Upsert
            result = collection.update_one(
                {'sinh_vien_id': sinh_vien_id, 'hoc_ky_id': hoc_ky_id},
                {
                    '$set': {
                        'tkb_data': tkb_data,
                        'updated_at': self._get_current_time()
                    }
                },
                upsert=True
            )
            
            logger.debug(f"TKB cached for SV {sinh_vien_id}, HK {hoc_ky_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache TKB: {e}")
            return False
    
    def get_cached_tkb(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[List[Dict]]:
        """Get cached TKB data"""
        if not self.is_available:
            return None
        
        try:
            collection = self.db['tkb_cache']
            doc = collection.find_one({
                'sinh_vien_id': sinh_vien_id,
                'hoc_ky_id': hoc_ky_id
            })
            
            if doc:
                return doc.get('tkb_data')
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached TKB: {e}")
            return None
    
    def invalidate_tkb_cache(self, sinh_vien_id: str = None, hoc_ky_id: str = None) -> bool:
        """Invalidate TKB cache"""
        if not self.is_available:
            return False
        
        try:
            collection = self.db['tkb_cache']
            
            query = {}
            if sinh_vien_id:
                query['sinh_vien_id'] = sinh_vien_id
            if hoc_ky_id:
                query['hoc_ky_id'] = hoc_ky_id
            
            if query:
                collection.delete_many(query)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate TKB cache: {e}")
            return False
    
    # ============ TKB MON HOC OPERATIONS (MAIN TKB DATA) ============
    # Collection: thoi_khoa_bieu_mon_hoc
    # Schema from BE legacy:
    #   - ma_hoc_phan: String
    #   - hoc_ky_id: String
    #   - danhSachLop: [{ tenLop, phongHocId, ngayBatDau, ngayKetThuc, tietBatDau, tietKetThuc, thuTrongTuan }]
    
    TKB_COLLECTION = 'thoi_khoa_bieu_mon_hoc'
    
    def get_tkb_by_ma_hoc_phan_and_hoc_ky(self, ma_hoc_phan: str, hoc_ky_id: str) -> Optional[Dict]:
        """
        Get TKB for a specific môn học in a học kỳ
        """
        if not self.is_available:
            return None
        
        try:
            collection = self.db[self.TKB_COLLECTION]
            
            doc = collection.find_one({
                'ma_hoc_phan': ma_hoc_phan,
                'hoc_ky_id': hoc_ky_id
            })
            
            return doc
            
        except Exception as e:
            logger.error(f"Failed to get TKB by ma_hoc_phan: {e}")
            return None
    
    def get_tkb_by_hoc_phans(self, ma_hoc_phans: List[str], hoc_ky_id: str) -> List[Dict]:
        """
        Get TKB data for multiple học phần
        Used by SV to view class schedules
        """
        if not self.is_available:
            return []
        
        try:
            collection = self.db[self.TKB_COLLECTION]
            
            cursor = collection.find({
                'ma_hoc_phan': {'$in': ma_hoc_phans},
                'hoc_ky_id': hoc_ky_id
            })
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Failed to get TKB by hoc phans: {e}")
            return []
    
    def get_tkb_by_hoc_ky(self, hoc_ky_id: str) -> List[Dict]:
        """
        Get all TKB for a học kỳ
        Used by TLK to view all schedules
        """
        if not self.is_available:
            return []
        
        try:
            collection = self.db[self.TKB_COLLECTION]
            
            cursor = collection.find({
                'hoc_ky_id': hoc_ky_id
            }).sort('ma_hoc_phan', 1)
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Failed to get TKB by hoc ky: {e}")
            return []
    
    def save_tkb_mon_hoc(self, ma_hoc_phan: str, hoc_ky_id: str, danh_sach_lop: List[Dict]) -> bool:
        """
        Save TKB for a học phần (when TLK creates schedule)
        Stores in MongoDB for fast retrieval
        """
        if not self.is_available:
            logger.warning("MongoDB not available, will use PostgreSQL only")
            return False
        
        try:
            collection = self.db[self.TKB_COLLECTION]
            
            result = collection.update_one(
                {'ma_hoc_phan': ma_hoc_phan, 'hoc_ky_id': hoc_ky_id},
                {
                    '$set': {
                        'danhSachLop': danh_sach_lop,
                        'updated_at': self._get_current_time()
                    }
                },
                upsert=True
            )
            
            logger.info(f"✅ TKB saved for {ma_hoc_phan} in HK {hoc_ky_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save TKB mon hoc: {e}")
            return False
    
    def add_lop_to_tkb(self, ma_hoc_phan: str, hoc_ky_id: str, lop_info: Dict) -> bool:
        """
        Add a class to existing TKB (or create new TKB if not exists)
        """
        if not self.is_available:
            return False
        
        try:
            collection = self.db[self.TKB_COLLECTION]
            
            # Check if TKB exists
            existing = collection.find_one({
                'ma_hoc_phan': ma_hoc_phan,
                'hoc_ky_id': hoc_ky_id
            })
            
            if existing:
                # Append to danhSachLop
                result = collection.update_one(
                    {'ma_hoc_phan': ma_hoc_phan, 'hoc_ky_id': hoc_ky_id},
                    {
                        '$push': {'danhSachLop': lop_info},
                        '$set': {'updated_at': self._get_current_time()}
                    }
                )
            else:
                # Create new
                result = collection.insert_one({
                    'ma_hoc_phan': ma_hoc_phan,
                    'hoc_ky_id': hoc_ky_id,
                    'danhSachLop': [lop_info],
                    'updated_at': self._get_current_time()
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lop to TKB: {e}")
            return False
    
    def get_tkb_for_lop(self, ma_hoc_phan: str, hoc_ky_id: str, ten_lop: str) -> Optional[Dict]:
        """
        Get TKB info for a specific class
        Returns the class info from danhSachLop
        """
        if not self.is_available:
            return None
        
        try:
            tkb = self.get_tkb_by_ma_hoc_phan_and_hoc_ky(ma_hoc_phan, hoc_ky_id)
            if not tkb:
                return None
            
            danh_sach_lop = tkb.get('danhSachLop', [])
            for lop in danh_sach_lop:
                if lop.get('tenLop') == ten_lop:
                    return lop
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get TKB for lop: {e}")
            return None
    
    # ============ TAI LIEU OPERATIONS ============
    
    def save_tai_lieu_metadata(self, tai_lieu_id: str, metadata: Dict) -> bool:
        """Save tài liệu metadata to MongoDB"""
        if not self.is_available:
            return False
        
        try:
            collection = self.db['tai_lieu']
            
            result = collection.update_one(
                {'tai_lieu_id': tai_lieu_id},
                {'$set': {**metadata, 'updated_at': self._get_current_time()}},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save tai lieu metadata: {e}")
            return False
    
    def get_tai_lieu_by_lop(self, lop_hoc_phan_id: str) -> List[Dict]:
        """Get tài liệu metadata for a lớp học phần"""
        if not self.is_available:
            return []
        
        try:
            collection = self.db['tai_lieu']
            cursor = collection.find({'lop_hoc_phan_id': lop_hoc_phan_id})
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Failed to get tai lieu: {e}")
            return []
    
    # ============ UTILITY METHODS ============
    
    def _get_current_time(self):
        """Get current datetime"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for MongoDB connection"""
        if not self.is_available:
            return {
                'status': 'unavailable',
                'message': 'MongoDB not configured or connection failed'
            }
        
        try:
            # Ping test
            self.db.client.admin.command('ping')
            return {
                'status': 'healthy',
                'database': self.db.name,
                'collections': self.db.list_collection_names()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Singleton instance
_mongodb_service = None


def get_mongodb_service() -> MongoDBService:
    """Get MongoDB service singleton"""
    global _mongodb_service
    if _mongodb_service is None:
        _mongodb_service = MongoDBService()
    return _mongodb_service
