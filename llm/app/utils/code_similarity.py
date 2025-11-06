from typing import Dict, Any, Optional
import re
from difflib import SequenceMatcher


class CodeSimilarityDetector:

    @staticmethod
    def normalize_code(code: str) -> str:
        code = re.sub(r'#.*', '', code)
        code = re.sub(r'\s+', ' ', code)
        code = code.strip().lower()
        return code

    @staticmethod
    def calculate_similarity(code1: str, code2: str) -> float:
        norm1 = CodeSimilarityDetector.normalize_code(code1)
        norm2 = CodeSimilarityDetector.normalize_code(code2)

        if not norm1 or not norm2:
            return 0.0

        return SequenceMatcher(None, norm1, norm2).ratio()

    @staticmethod
    def extract_keywords(text: str) -> set:
        keywords = set()

        analysis_keywords = [
            'correlation', 'histogram', 'scatter', 'plot', 'distribution',
            'mean', 'median', 'std', 'variance', 'regression', 'classification',
            'heatmap', 'boxplot', 'lineplot', 'barplot', 'pca', 'cluster'
        ]

        text_lower = text.lower()
        for keyword in analysis_keywords:
            if keyword in text_lower:
                keywords.add(keyword)

        column_matches = re.findall(r'column[s]?\s+["\']?(\w+)["\']?', text_lower)
        keywords.update(column_matches)

        return keywords

    @staticmethod
    def is_similar_request(
        current_request   : str
        , code_history    : list
        , similarity_threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        if not code_history:
            return None

        current_keywords = CodeSimilarityDetector.extract_keywords(current_request)

        for history_entry in reversed(code_history[-5:]):
            code            = history_entry.get("code", "")
            timestamp       = history_entry.get("timestamp", 0)

            code_keywords   = CodeSimilarityDetector.extract_keywords(code)

            keyword_overlap = len(current_keywords & code_keywords) / max(len(current_keywords), 1)

            if keyword_overlap >= 0.6:
                return {
                    "is_similar"    : True
                    , "previous_code": code
                    , "timestamp"   : timestamp
                    , "similarity"  : keyword_overlap
                }

        return None

    @staticmethod
    def find_similar_code_pattern(
        task_description  : str
        , code_history    : list
    ) -> Optional[str]:
        similar = CodeSimilarityDetector.is_similar_request(task_description, code_history)

        if similar:
            return similar.get("previous_code")

        return None
