# app/core/llm/cache_system.py
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
import redis
from app.config import settings


class SemanticCache:
    """Cache semântico que considera similaridade de prompts."""
    
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        self.cache_ttl = settings.cache_ttl
        
        if use_redis:
            self.redis_client = redis.Redis(
                host='localhost', port=6379, decode_responses=True
            )
            self._cache = None
        else:
            self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def _generate_key(self, prompt: str, provider: str, model: str) -> str:
        """Gera chave única baseada no hash do prompt + provider + model."""
        content = f"{prompt}:{provider}:{model}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _semantic_key(self, prompt: str) -> str:
        """
        Gera chave semântica simplificada.
        Em produção, usar embeddings para similaridade.
        """
        # Simplificação: remove espaços extras e converte para lowercase
        normalized = ' '.join(prompt.lower().split())
        # Pega as primeiras 100 palavras para representação
        words = normalized.split()[:100]
        return ' '.join(sorted(set(words)))
    
    def get(self, prompt: str, provider: str, model: str) -> Optional[Any]:
        """Tenta obter do cache exato."""
        key = self._generate_key(prompt, provider, model)
        
        if self.use_redis:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        else:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return value
                else:
                    del self._cache[key]
        
        return None
    
    def get_semantic(self, prompt: str, threshold: float = 0.8) -> Optional[Any]:
        """
        Busca por prompts semanticamente similares.
        TODO: Implementar com embeddings para similaridade real.
        """
        # Implementação simplificada
        semantic_key = self._semantic_key(prompt)
        
        if self.use_redis:
            # Padrão de chave para busca
            pattern = f"semantic:*{hashlib.md5(semantic_key.encode()).hexdigest()[:10]}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return json.loads(self.redis_client.get(keys[0]))
        else:
            # Implementação em memória
            for key, (value, timestamp) in list(self._cache.items()):
                if "semantic:" in key and time.time() - timestamp < self.cache_ttl:
                    # Verificação simplificada de similaridade
                    cached_prompt = key.split(":")[1]
                    if self._simple_similarity(prompt, cached_prompt) > threshold:
                        return value
        
        return None
    
    def set(self, prompt: str, provider: str, model: str, value: Any):
        """Armazena no cache."""
        key = self._generate_key(prompt, provider, model)
        
        if self.use_redis:
            self.redis_client.setex(
                key, 
                self.cache_ttl,
                json.dumps(value)
            )
            # Também armazena versão semântica
            semantic_key = f"semantic:{self._semantic_key(prompt)}:{key}"
            self.redis_client.setex(
                semantic_key,
                self.cache_ttl,
                json.dumps(value)
            )
        else:
            self._cache[key] = (value, time.time())
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Similaridade simplificada baseada em palavras em comum."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def clear_expired(self):
        """Limpa entradas expiradas (apenas para cache em memória)."""
        if not self.use_redis:
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def stats(self) -> Dict[str, Any]:
        """Estatísticas do cache."""
        if self.use_redis:
            info = self.redis_client.info()
            return {
                "type": "redis",
                "keys": info.get('db0', {}).get('keys', 0),
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "hit_rate": info.get('keyspace_hits', 0) / 
                          max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
            }
        else:
            total = len(self._cache)
            current_time = time.time()
            valid = sum(1 for _, timestamp in self._cache.values() 
                       if current_time - timestamp < self.cache_ttl)
            
            return {
                "type": "memory",
                "total_entries": total,
                "valid_entries": valid,
                "expired_entries": total - valid
            }


# Instância global do cache
cache_system = SemanticCache(use_redis=False)