"""
概念漂移检测器

检测领域概念的变化和演化趋势
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import Counter, defaultdict
import logging
import time

from ..schemas.base_schema import Schema

logger = logging.getLogger(__name__)


@dataclass
class ConceptDrift:
    """概念漂移"""
    concept_name: str
    drift_type: str  # 'emergence', 'disappearance', 'frequency_change', 'context_change'
    old_frequency: float
    new_frequency: float
    confidence: float
    evidence: List[str]
    timestamp: str


@dataclass
class DriftDetectionResult:
    """漂移检测结果"""
    detected_drifts: List[ConceptDrift]
    stability_score: float  # 0-1, 1表示完全稳定
    recommendation: str
    analysis_summary: str


class ConceptDriftDetector:
    """概念漂移检测器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.drift_threshold = config.get('drift_threshold', 0.3)  # 频率变化阈值
        self.min_samples = config.get('min_samples', 10)  # 最小样本数
        self.window_size = config.get('window_size', 100)  # 滑动窗口大小
        
        # 历史数据存储
        self.concept_history: Dict[str, List[Tuple[float, int]]] = defaultdict(list)  # (timestamp, frequency)
        self.document_history: List[Tuple[float, str]] = []  # (timestamp, content)
    
    def detect_drift(self, current_documents: List[str], 
                    reference_schema: Optional[Schema] = None) -> DriftDetectionResult:
        """
        检测概念漂移
        
        Args:
            current_documents: 当前文档集合
            reference_schema: 参考Schema（可选）
            
        Returns:
            DriftDetectionResult: 漂移检测结果
        """
        current_time = time.time()
        
        # 1. 提取当前概念频率
        current_concepts = self._extract_concepts(current_documents)
        
        # 2. 更新历史记录
        self._update_history(current_concepts, current_documents, current_time)
        
        # 3. 检测各种类型的漂移
        detected_drifts = []
        
        # 检测频率漂移
        frequency_drifts = self._detect_frequency_drift(current_concepts)
        detected_drifts.extend(frequency_drifts)
        
        # 检测新概念出现
        emergence_drifts = self._detect_concept_emergence(current_concepts)
        detected_drifts.extend(emergence_drifts)
        
        # 检测概念消失
        disappearance_drifts = self._detect_concept_disappearance(current_concepts)
        detected_drifts.extend(disappearance_drifts)
        
        # 4. 计算稳定性分数
        stability_score = self._calculate_stability_score(detected_drifts)
        
        # 5. 生成建议
        recommendation = self._generate_recommendation(detected_drifts, stability_score)
        
        # 6. 生成分析摘要
        analysis_summary = self._generate_analysis_summary(detected_drifts, stability_score)
        
        return DriftDetectionResult(
            detected_drifts=detected_drifts,
            stability_score=stability_score,
            recommendation=recommendation,
            analysis_summary=analysis_summary
        )
    
    def _extract_concepts(self, documents: List[str]) -> Dict[str, int]:
        """提取文档中的概念及其频率"""
        all_text = ' '.join(documents)
        
        # 使用简单的正则表达式提取概念
        import re
        
        concepts = []
        
        # 提取技术术语
        tech_patterns = [
            r'\b\w+算法\b', r'\b\w+模型\b', r'\b\w+方法\b',
            r'\b\w+系统\b', r'\b\w+框架\b', r'\b\w+网络\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, all_text)
            concepts.extend(matches)
        
        # 提取大写开头的名词短语
        noun_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', all_text)
        concepts.extend(noun_phrases)
        
        return dict(Counter(concepts))
    
    def _update_history(self, concepts: Dict[str, int], documents: List[str], timestamp: float):
        """更新历史记录"""
        # 更新概念频率历史
        for concept, frequency in concepts.items():
            self.concept_history[concept].append((timestamp, frequency))
            
            # 保持窗口大小
            if len(self.concept_history[concept]) > self.window_size:
                self.concept_history[concept] = self.concept_history[concept][-self.window_size:]
        
        # 更新文档历史
        for doc in documents:
            self.document_history.append((timestamp, doc))
        
        # 保持窗口大小
        if len(self.document_history) > self.window_size:
            self.document_history = self.document_history[-self.window_size:]
    
    def _detect_frequency_drift(self, current_concepts: Dict[str, int]) -> List[ConceptDrift]:
        """检测频率漂移"""
        drifts = []
        
        for concept, current_freq in current_concepts.items():
            if concept in self.concept_history and len(self.concept_history[concept]) >= self.min_samples:
                # 计算历史平均频率
                historical_freqs = [freq for _, freq in self.concept_history[concept][:-1]]
                if historical_freqs:
                    avg_historical_freq = sum(historical_freqs) / len(historical_freqs)
                    
                    # 计算频率变化比例
                    if avg_historical_freq > 0:
                        change_ratio = abs(current_freq - avg_historical_freq) / avg_historical_freq
                        
                        if change_ratio > self.drift_threshold:
                            drift_type = 'frequency_increase' if current_freq > avg_historical_freq else 'frequency_decrease'
                            
                            drifts.append(ConceptDrift(
                                concept_name=concept,
                                drift_type=drift_type,
                                old_frequency=avg_historical_freq,
                                new_frequency=current_freq,
                                confidence=min(0.9, change_ratio),
                                evidence=[f"频率从{avg_historical_freq:.1f}变化到{current_freq}"],
                                timestamp=str(time.time())
                            ))
        
        return drifts
    
    def _detect_concept_emergence(self, current_concepts: Dict[str, int]) -> List[ConceptDrift]:
        """检测新概念出现"""
        drifts = []
        
        for concept, frequency in current_concepts.items():
            if concept not in self.concept_history or len(self.concept_history[concept]) == 0:
                # 新出现的概念
                if frequency >= 2:  # 至少出现2次才认为是有意义的新概念
                    drifts.append(ConceptDrift(
                        concept_name=concept,
                        drift_type='emergence',
                        old_frequency=0.0,
                        new_frequency=frequency,
                        confidence=0.8,
                        evidence=[f"新概念首次出现，频率为{frequency}"],
                        timestamp=str(time.time())
                    ))
        
        return drifts
    
    def _detect_concept_disappearance(self, current_concepts: Dict[str, int]) -> List[ConceptDrift]:
        """检测概念消失"""
        drifts = []
        
        # 检查历史中存在但当前不存在的概念
        for concept in self.concept_history:
            if concept not in current_concepts and len(self.concept_history[concept]) >= self.min_samples:
                # 计算历史平均频率
                historical_freqs = [freq for _, freq in self.concept_history[concept]]
                avg_historical_freq = sum(historical_freqs) / len(historical_freqs)
                
                if avg_historical_freq >= 2:  # 只关注之前有意义的概念
                    drifts.append(ConceptDrift(
                        concept_name=concept,
                        drift_type='disappearance',
                        old_frequency=avg_historical_freq,
                        new_frequency=0.0,
                        confidence=0.7,
                        evidence=[f"概念消失，历史平均频率为{avg_historical_freq:.1f}"],
                        timestamp=str(time.time())
                    ))
        
        return drifts
    
    def _calculate_stability_score(self, drifts: List[ConceptDrift]) -> float:
        """计算稳定性分数"""
        if not drifts:
            return 1.0
        
        # 基于漂移数量和置信度计算稳定性
        total_drift_impact = sum(drift.confidence for drift in drifts)
        max_possible_impact = len(drifts) * 1.0
        
        stability = 1.0 - (total_drift_impact / max_possible_impact)
        return max(0.0, stability)
    
    def _generate_recommendation(self, drifts: List[ConceptDrift], stability_score: float) -> str:
        """生成建议"""
        if stability_score > 0.8:
            return "概念稳定，无需调整Schema"
        elif stability_score > 0.6:
            return "检测到轻微概念漂移，建议监控但暂不调整"
        elif stability_score > 0.4:
            return "检测到中等程度概念漂移，建议考虑更新Schema"
        else:
            return "检测到严重概念漂移，强烈建议更新Schema"
    
    def _generate_analysis_summary(self, drifts: List[ConceptDrift], stability_score: float) -> str:
        """生成分析摘要"""
        if not drifts:
            return f"未检测到概念漂移，稳定性分数: {stability_score:.2f}"
        
        drift_types = Counter([drift.drift_type for drift in drifts])
        summary_parts = [f"检测到{len(drifts)}个概念漂移"]
        
        for drift_type, count in drift_types.items():
            type_name = {
                'emergence': '新概念出现',
                'disappearance': '概念消失',
                'frequency_increase': '频率增加',
                'frequency_decrease': '频率减少'
            }.get(drift_type, drift_type)
            
            summary_parts.append(f"{type_name}: {count}个")
        
        summary_parts.append(f"稳定性分数: {stability_score:.2f}")
        
        return "，".join(summary_parts)
    
    def get_concept_trends(self, concept_name: str) -> List[Tuple[float, int]]:
        """获取特定概念的趋势数据"""
        return self.concept_history.get(concept_name, [])
    
    def clear_history(self):
        """清空历史记录"""
        self.concept_history.clear()
        self.document_history.clear()
        self.logger.info("概念漂移历史记录已清空")
