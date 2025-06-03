"""
Decentralized AI Node Operating System - Step 4: File Encryption & Security
Advanced encryption and security features for the file system.
"""

import os
import time
import hashlib
import secrets
import base64
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

class EncryptionLevel(Enum):
    """File encryption levels"""
    NONE = "No Encryption"
    BASIC = "🔐 Basic Encryption"
    ADVANCED = "🔒 Advanced Encryption"
    MILITARY = "🛡️ Military Grade"

class SecurityEvent(Enum):
    """Security audit event types"""
    FILE_ACCESS = "File Access"
    ENCRYPTION_APPLIED = "Encryption Applied"
    DECRYPTION_ATTEMPTED = "Decryption Attempted"
    PERMISSION_DENIED = "Permission Denied"
    SUSPICIOUS_ACTIVITY = "Suspicious Activity"
    KEY_GENERATED = "Key Generated"
    INTEGRITY_CHECK = "Integrity Check"

@dataclass
class SecurityAuditLog:
    """Security audit log entry"""
    timestamp: float = field(default_factory=time.time)
    event_type: SecurityEvent = SecurityEvent.FILE_ACCESS
    user_id: str = "unknown"
    file_path: str = ""
    success: bool = True
    details: str = ""
    ip_address: str = "127.0.0.1"
    user_agent: str = "AI_Node_OS"

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    algorithm: str
    created_time: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    usage_count: int = 0
    owner: str = "system"
    encryption_level: EncryptionLevel = EncryptionLevel.BASIC

class SimpleEncryption:
    """
    Simple XOR-based encryption for demonstration purposes
    Note: This is for educational use only, not cryptographically secure
    """
    
    @staticmethod
    def generate_key(length: int = 32) -> bytes:
        """Generate a random encryption key"""
        return secrets.token_bytes(length)
        
    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        """Encrypt data using XOR cipher with key stretching"""
        if not data:
            return data
            
        # Stretch key to match data length using SHA256
        extended_key = b""
        key_index = 0
        
        for i in range(len(data)):
            if key_index >= len(key):
                # Generate more key material using hash
                hash_input = key + extended_key[-32:] if extended_key else key
                new_key_material = hashlib.sha256(hash_input).digest()
                extended_key += new_key_material
                key_index = len(extended_key) - 32
                
            # XOR operation
            extended_key += bytes([key[key_index % len(key)]])
            key_index += 1
            
        # Perform XOR encryption
        encrypted = bytes(a ^ b for a, b in zip(data, extended_key[:len(data)]))
        
        # Add checksum for integrity
        checksum = hashlib.sha256(data).digest()[:8]
        return checksum + encrypted
        
    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using XOR cipher"""
        if not encrypted_data or len(encrypted_data) < 8:
            return encrypted_data
            
        # Extract checksum and encrypted data
        checksum = encrypted_data[:8]
        data = encrypted_data[8:]
        
        # Stretch key to match data length
        extended_key = b""
        key_index = 0
        
        for i in range(len(data)):
            if key_index >= len(key):
                # Generate more key material using hash
                hash_input = key + extended_key[-32:] if extended_key else key
                new_key_material = hashlib.sha256(hash_input).digest()
                extended_key += new_key_material
                key_index = len(extended_key) - 32
                
            extended_key += bytes([key[key_index % len(key)]])
            key_index += 1
            
        # Perform XOR decryption
        decrypted = bytes(a ^ b for a, b in zip(data, extended_key[:len(data)]))
        
        # Verify checksum
        expected_checksum = hashlib.sha256(decrypted).digest()[:8]
        if checksum != expected_checksum:
            raise ValueError("Data integrity check failed - file may be corrupted")
            
        return decrypted

class FileEncryption:
    """
    File encryption and security management system
    Provides encryption, decryption, key management, and security auditing
    """
    
    def __init__(self):
        # Encryption keys and metadata
        self.encryption_keys: Dict[str, bytes] = {}  # key_id -> actual key
        self.key_metadata: Dict[str, EncryptionKey] = {}  # key_id -> metadata
        self.file_keys: Dict[str, str] = {}  # file_id -> key_id
        
        # Security and auditing
        self.audit_log: List[SecurityAuditLog] = []
        self.failed_attempts: Dict[str, List[float]] = {}  # user_id -> attempt times
        self.blocked_users: Dict[str, float] = {}  # user_id -> block_until_time
        
        # Access control
        self.file_access_rules: Dict[str, Dict[str, Any]] = {}  # file_id -> rules
        
        # Synchronization
        self.security_lock = threading.RLock()
        
        # Generate master key for system
        self._generate_master_key()
        
    def _generate_master_key(self):
        """Generate master encryption key for system"""
        master_key = SimpleEncryption.generate_key(32)
        key_id = "master_system_key"
        
        self.encryption_keys[key_id] = master_key
        self.key_metadata[key_id] = EncryptionKey(
            key_id=key_id,
            algorithm="XOR-SHA256",
            owner="system",
            encryption_level=EncryptionLevel.ADVANCED
        )
        
        self._log_security_event(
            SecurityEvent.KEY_GENERATED,
            "system",
            "",
            True,
            f"Master key generated: {key_id}"
        )
        
    def generate_file_key(self, 
                         file_id: str, 
                         user_id: str,
                         encryption_level: EncryptionLevel = EncryptionLevel.BASIC) -> str:
        """Generate encryption key for a specific file"""
        
        with self.security_lock:
            # Generate unique key ID
            key_id = f"file_{file_id}_{int(time.time())}"
            
            # Generate encryption key based on level
            if encryption_level == EncryptionLevel.BASIC:
                key = SimpleEncryption.generate_key(16)
                algorithm = "XOR-SHA256-Basic"
            elif encryption_level == EncryptionLevel.ADVANCED:
                key = SimpleEncryption.generate_key(32)
                algorithm = "XOR-SHA256-Advanced"
            elif encryption_level == EncryptionLevel.MILITARY:
                key = SimpleEncryption.generate_key(64)
                algorithm = "XOR-SHA256-Military"
            elif encryption_level == EncryptionLevel.NONE:
                key = b""
                algorithm = "None"
            else:
                raise ValueError(f"Unsupported encryption level: {encryption_level}")
                
            # Store key and metadata
            self.encryption_keys[key_id] = key
            self.key_metadata[key_id] = EncryptionKey(
                key_id=key_id,
                algorithm=algorithm,
                owner=user_id,
                encryption_level=encryption_level
            )
            
            # Associate key with file
            self.file_keys[file_id] = key_id
            
            self._log_security_event(
                SecurityEvent.KEY_GENERATED,
                user_id,
                f"file_id:{file_id}",
                True,
                f"Encryption key generated: {encryption_level.value}"
            )
            
            return key_id
            
    def encrypt_file_content(self, 
                           file_id: str, 
                           content: bytes, 
                           user_id: str) -> bytes:
        """Encrypt file content using file's encryption key"""
        
        with self.security_lock:
            # Check if user is blocked
            if self._is_user_blocked(user_id):
                self._log_security_event(
                    SecurityEvent.PERMISSION_DENIED,
                    user_id,
                    f"file_id:{file_id}",
                    False,
                    "User blocked due to suspicious activity"
                )
                raise PermissionError("User blocked due to suspicious activity")
                
            # Get file's encryption key
            if file_id not in self.file_keys:
                raise ValueError(f"No encryption key found for file: {file_id}")
                
            key_id = self.file_keys[file_id]
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key not found: {key_id}")
                
            key = self.encryption_keys[key_id]
            
            # Skip encryption if no key (NONE level)
            if not key:
                encrypted_content = content
            else:
                # Encrypt content
                encrypted_content = SimpleEncryption.encrypt(content, key)
            
            # Update key usage
            self.key_metadata[key_id].last_used = time.time()
            self.key_metadata[key_id].usage_count += 1
            
            self._log_security_event(
                SecurityEvent.ENCRYPTION_APPLIED,
                user_id,
                f"file_id:{file_id}",
                True,
                f"File encrypted with key: {key_id}"
            )
            
            return encrypted_content
            
    def decrypt_file_content(self, 
                           file_id: str, 
                           encrypted_content: bytes, 
                           user_id: str) -> bytes:
        """Decrypt file content using file's encryption key"""
        
        with self.security_lock:
            start_time = time.time()
            
            # Check if user is blocked
            if self._is_user_blocked(user_id):
                self._log_security_event(
                    SecurityEvent.PERMISSION_DENIED,
                    user_id,
                    f"file_id:{file_id}",
                    False,
                    "User blocked - decryption denied"
                )
                raise PermissionError("User blocked due to suspicious activity")
                
            try:
                # Get file's encryption key
                if file_id not in self.file_keys:
                    raise ValueError(f"No encryption key found for file: {file_id}")
                    
                key_id = self.file_keys[file_id]
                if key_id not in self.encryption_keys:
                    raise ValueError(f"Encryption key not found: {key_id}")
                    
                # Check access permissions
                if not self._check_file_access(file_id, user_id):
                    self._record_failed_attempt(user_id)
                    self._log_security_event(
                        SecurityEvent.PERMISSION_DENIED,
                        user_id,
                        f"file_id:{file_id}",
                        False,
                        "Insufficient permissions for decryption"
                    )
                    raise PermissionError("Insufficient permissions for decryption")
                    
                key = self.encryption_keys[key_id]
                
                # Skip decryption if no key (NONE level)
                if not key:
                    decrypted_content = encrypted_content
                else:
                    # Decrypt content
                    decrypted_content = SimpleEncryption.decrypt(encrypted_content, key)
                
                # Update key usage
                self.key_metadata[key_id].last_used = time.time()
                self.key_metadata[key_id].usage_count += 1
                
                self._log_security_event(
                    SecurityEvent.DECRYPTION_ATTEMPTED,
                    user_id,
                    f"file_id:{file_id}",
                    True,
                    f"File decrypted successfully with key: {key_id}"
                )
                
                return decrypted_content
                
            except Exception as e:
                # Record failed decryption attempt
                self._record_failed_attempt(user_id)
                
                self._log_security_event(
                    SecurityEvent.DECRYPTION_ATTEMPTED,
                    user_id,
                    f"file_id:{file_id}",
                    False,
                    f"Decryption failed: {str(e)}"
                )
                
                # Check if this should be flagged as suspicious
                if self._is_suspicious_activity(user_id):
                    self._log_security_event(
                        SecurityEvent.SUSPICIOUS_ACTIVITY,
                        user_id,
                        f"file_id:{file_id}",
                        False,
                        "Multiple failed decryption attempts detected"
                    )
                    
                raise
                
    def set_file_access_rules(self, 
                            file_id: str, 
                            allowed_users: List[str],
                            time_restrictions: Optional[Tuple[int, int]] = None,
                            max_accesses: Optional[int] = None):
        """Set access control rules for a file"""
        
        with self.security_lock:
            self.file_access_rules[file_id] = {
                "allowed_users": allowed_users,
                "time_restrictions": time_restrictions,  # (start_hour, end_hour)
                "max_accesses": max_accesses,
                "access_count": 0,
                "created_time": time.time()
            }
            
    def _check_file_access(self, file_id: str, user_id: str) -> bool:
        """Check if user has access to file"""
        
        # Admin always has access
        if user_id == "admin" or user_id == "system":
            return True
            
        # Check if access rules exist
        if file_id not in self.file_access_rules:
            return True  # No restrictions
            
        rules = self.file_access_rules[file_id]
        
        # Check allowed users
        if "allowed_users" in rules and user_id not in rules["allowed_users"]:
            return False
            
        # Check time restrictions
        if "time_restrictions" in rules and rules["time_restrictions"]:
            current_hour = time.localtime().tm_hour
            start_hour, end_hour = rules["time_restrictions"]
            if not (start_hour <= current_hour <= end_hour):
                return False
                
        # Check access count limit
        if "max_accesses" in rules and rules["max_accesses"]:
            if rules["access_count"] >= rules["max_accesses"]:
                return False
                
        # Increment access count
        rules["access_count"] += 1
        
        return True
        
    def _record_failed_attempt(self, user_id: str):
        """Record failed access attempt"""
        
        current_time = time.time()
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
            
        self.failed_attempts[user_id].append(current_time)
        
        # Clean old attempts (older than 1 hour)
        hour_ago = current_time - 3600
        self.failed_attempts[user_id] = [
            t for t in self.failed_attempts[user_id] if t > hour_ago
        ]
        
    def _is_suspicious_activity(self, user_id: str) -> bool:
        """Check if user activity is suspicious"""
        
        if user_id not in self.failed_attempts:
            return False
            
        # More than 5 failed attempts in last hour
        recent_failures = len(self.failed_attempts[user_id])
        if recent_failures > 5:
            # Block user for 1 hour
            self.blocked_users[user_id] = time.time() + 3600
            return True
            
        return False
        
    def _is_user_blocked(self, user_id: str) -> bool:
        """Check if user is currently blocked"""
        
        if user_id not in self.blocked_users:
            return False
            
        block_until = self.blocked_users[user_id]
        if time.time() > block_until:
            # Unblock user
            del self.blocked_users[user_id]
            return False
            
        return True
        
    def _log_security_event(self, 
                          event_type: SecurityEvent,
                          user_id: str,
                          file_path: str,
                          success: bool,
                          details: str):
        """Log security event for auditing"""
        
        event = SecurityAuditLog(
            event_type=event_type,
            user_id=user_id,
            file_path=file_path,
            success=success,
            details=details
        )
        
        self.audit_log.append(event)
        
        # Keep only last 10000 events
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
            
    def verify_file_integrity(self, 
                            file_id: str, 
                            content: bytes, 
                            expected_hash: str) -> bool:
        """Verify file integrity using hash"""
        
        actual_hash = hashlib.sha256(content).hexdigest()
        is_valid = actual_hash == expected_hash
        
        self._log_security_event(
            SecurityEvent.INTEGRITY_CHECK,
            "system",
            f"file_id:{file_id}",
            is_valid,
            f"Integrity check: {'passed' if is_valid else 'failed'}"
        )
        
        return is_valid
        
    def get_security_statistics(self) -> Dict[str, Any]:
        """Get security and encryption statistics"""
        
        with self.security_lock:
            total_events = len(self.audit_log)
            successful_events = len([e for e in self.audit_log if e.success])
            failed_events = total_events - successful_events
            
            # Count events by type
            events_by_type = {}
            for event in self.audit_log:
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
            # Active encryption keys
            active_keys = len([k for k in self.key_metadata.values() 
                              if k.usage_count > 0])
                              
            return {
                "total_encryption_keys": len(self.encryption_keys),
                "active_encryption_keys": active_keys,
                "encrypted_files": len(self.file_keys),
                "total_security_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "success_rate": (successful_events / max(total_events, 1)) * 100,
                "events_by_type": events_by_type,
                "blocked_users": len(self.blocked_users),
                "users_with_failed_attempts": len(self.failed_attempts),
                "encryption_levels": {
                    level.value: len([k for k in self.key_metadata.values() 
                                    if k.encryption_level == level])
                    for level in EncryptionLevel
                }
            }
            
    def get_audit_log(self, 
                     limit: int = 100,
                     event_type: Optional[SecurityEvent] = None,
                     user_id: Optional[str] = None) -> List[SecurityAuditLog]:
        """Get filtered audit log entries"""
        
        with self.security_lock:
            filtered_log = self.audit_log
            
            # Filter by event type
            if event_type:
                filtered_log = [e for e in filtered_log if e.event_type == event_type]
                
            # Filter by user
            if user_id:
                filtered_log = [e for e in filtered_log if e.user_id == user_id]
                
            # Return most recent entries
            return filtered_log[-limit:]
            
    def export_audit_log(self, filename: str):
        """Export audit log to file"""
        
        import json
        
        with self.security_lock:
            audit_data = []
            for event in self.audit_log:
                audit_data.append({
                    "timestamp": event.timestamp,
                    "event_type": event.event_type.value,
                    "user_id": event.user_id,
                    "file_path": event.file_path,
                    "success": event.success,
                    "details": event.details,
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent
                })
                
            with open(filename, 'w') as f:
                json.dump(audit_data, f, indent=2)
                
        self._log_security_event(
            SecurityEvent.FILE_ACCESS,
            "system",
            filename,
            True,
            f"Audit log exported to {filename}"
        ) 