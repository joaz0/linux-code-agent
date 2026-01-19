# app/core/llm/complexity_estimator.py
import re
from typing import Dict, List
from enum import Enum
from app.config import TaskComplexity


class ComplexityEstimator:
    """Estima a complexidade de uma tarefa baseado em heurísticas."""
    
    def __init__(self):
        # Palavras-chave para cada nível de complexidade
        self.simple_keywords = [
            'list', 'show', 'display', 'get', 'fetch', 'read',
            'find', 'search', 'count', 'check', 'verify',
            'ls', 'cat', 'grep', 'pwd', 'whoami'
        ]
        
        self.medium_keywords = [
            'edit', 'modify', 'update', 'change', 'add', 'insert',
            'remove', 'delete', 'create', 'write', 'save',
            'mv', 'cp', 'mkdir', 'touch', 'echo'
        ]
        
        self.complex_keywords = [
            'refactor', 'refactoring', 'debug', 'optimize', 'improve',
            'implement', 'develop', 'build', 'design', 'architecture',
            'test', 'validate', 'multi', 'multiple', 'batch',
            'restructure', 'reorganize', 'redesign', 'rewrite'
        ]
        
        # Padrões regex para tarefas complexas
        self.complex_patterns = [
            r'refactor.*code',
            r'debug.*error',
            r'optimize.*performance',
            r'implement.*feature',
            r'create.*system',
            r'multi.*file',
            r'batch.*process'
        ]
    
    def estimate(self, task_description: str) -> TaskComplexity:
        """
        Estima complexidade da tarefa usando heurística combinada.
        Retorna: SIMPLE, MEDIUM ou COMPLEX
        """
        task_lower = task_description.lower()
        
        # 1. Contagem de palavras-chave
        simple_count = self._count_keywords(task_lower, self.simple_keywords)
        medium_count = self._count_keywords(task_lower, self.medium_keywords)
        complex_count = self._count_keywords(task_lower, self.complex_keywords)
        
        # 2. Verificação de padrões complexos
        pattern_match = any(re.search(pattern, task_lower) 
                          for pattern in self.complex_patterns)
        
        # 3. Análise de comprimento
        word_count = len(task_lower.split())
        
        # 4. Heurística de decisão
        if pattern_match or complex_count > 2:
            return TaskComplexity.COMPLEX
        elif complex_count > 0 or medium_count > 1:
            return TaskComplexity.MEDIUM
        elif word_count > 100:  # Tarefas muito longas são complexas
            return TaskComplexity.COMPLEX
        elif word_count > 50:   # Tarefas longas são médias
            return TaskComplexity.MEDIUM
        elif simple_count > 0 and medium_count == 0 and complex_count == 0:
            return TaskComplexity.SIMPLE
        else:
            # Default: médio
            return TaskComplexity.MEDIUM
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Conta ocorrências de palavras-chave no texto."""
        count = 0
        for keyword in keywords:
            # Busca por palavra inteira (com boundaries)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text)
            count += len(matches)
        return count
    
    def get_detailed_analysis(self, task_description: str) -> Dict:
        """Retorna análise detalhada da tarefa."""
        task_lower = task_description.lower()
        
        return {
            "task": task_description,
            "word_count": len(task_lower.split()),
            "simple_keywords": self._find_keywords(task_lower, self.simple_keywords),
            "medium_keywords": self._find_keywords(task_lower, self.medium_keywords),
            "complex_keywords": self._find_keywords(task_lower, self.complex_keywords),
            "complex_patterns_matched": self._find_patterns(task_lower),
            "estimated_complexity": self.estimate(task_description).value
        }
    
    def _find_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Encontra quais palavras-chave estão presentes."""
        found = []
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                found.append(keyword)
        return found
    
    def _find_patterns(self, text: str) -> List[str]:
        """Encontra quais padrões complexos foram detectados."""
        matched = []
        for pattern in self.complex_patterns:
            if re.search(pattern, text):
                matched.append(pattern)
        return matched


# Instância global
complexity_estimator = ComplexityEstimator()