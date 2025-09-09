"""
基于本体Schema的领域识别系统
结合 document + seed_knowledge + ontology + LLM 进行智能识别
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from ontology.managers.dynamic_schema import DynamicOntologyManager

@dataclass
class SchemaDetectionResult:
    """Schema检测结果"""
    schema_file: str
    confidence: float
    evidence: List[str]
    method: str  # 'ontology', 'seed_knowledge', 'document', 'llm'
    schema: Optional[object] = None  # 添加schema属性以兼容动态Schema

class SchemaDetector:
    """基于本体Schema的领域检测器"""
    
    def __init__(self, schema_dir: str = "ontology/schemas/spatiotemporal"):
        self.schema_dir = Path(schema_dir)
        self.available_schemas = self._discover_schemas()
        self.ontology_managers = {}
        
        # 加载所有可用的Schema
        self._load_all_schemas()
    
    def _discover_schemas(self) -> List[str]:
        """发现可用的Schema文件"""
        schema_files = []

        # 添加通用本体Schema
        schema_files.append("../schemas/general/schema_config.yaml")  # 通用本体

        # 添加时空本体Schema
        if self.schema_dir.exists():
            for file_path in self.schema_dir.glob("*.yaml"):
                schema_files.append(file_path.name)

        return schema_files
    
    def _load_all_schemas(self):
        """加载所有Schema"""
        for schema_file in self.available_schemas:
            try:
                if schema_file.startswith("../"):
                    schema_path = str(Path("ontology") / schema_file[3:])
                else:
                    schema_path = str(self.schema_dir / schema_file)
                
                manager = DynamicOntologyManager(schema_path)
                self.ontology_managers[schema_file] = manager
                print(f"✅ 加载Schema: {schema_file}")
            except Exception as e:
                print(f"⚠️ 加载Schema失败 {schema_file}: {e}")
    
    def detect_schema(self, document_text: str, seed_knowledge: List[Dict] = None,
                     use_llm: bool = True) -> List[SchemaDetectionResult]:
        """
        综合检测最适合的Schema

        Args:
            document_text: 文档文本
            seed_knowledge: 种子知识（三元组列表）
            use_llm: 是否使用LLM辅助决策

        Returns:
            按置信度排序的Schema检测结果
        """
        results = []

        for schema_file, manager in self.ontology_managers.items():
            # 方法1：基于本体实体类型匹配
            ontology_score, ontology_evidence = self._ontology_based_detection(
                document_text, manager
            )

            # 方法2：基于种子知识匹配
            seed_score, seed_evidence = self._seed_knowledge_detection(
                seed_knowledge, manager
            ) if seed_knowledge else (0.0, [])

            # 方法3：基于文档结构特征
            document_score, document_evidence = self._document_structure_detection(
                document_text, manager
            )

            # 综合评分
            final_score = (
                0.4 * ontology_score +      # 本体匹配权重最高
                0.3 * seed_score +          # 种子知识匹配
                0.3 * document_score        # 文档结构匹配
            )



            if final_score > 0.05:  # 降低最低阈值
                all_evidence = ontology_evidence + seed_evidence + document_evidence
                results.append(SchemaDetectionResult(
                    schema_file=schema_file,
                    confidence=final_score,
                    evidence=all_evidence[:5],  # 最多5个证据
                    method='hybrid'
                ))

        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)

        # LLM辅助决策：当前两名置信度相近时
        if use_llm and len(results) >= 2:
            top1, top2 = results[0], results[1]
            confidence_diff = top1.confidence - top2.confidence

            if confidence_diff < 0.1:  # 置信度差异小于10%
                print(f"🤖 置信度相近({confidence_diff:.3f})，启用LLM辅助决策...")
                llm_result = self._llm_schema_decision(document_text, [top1, top2])
                if llm_result:
                    # 更新LLM选择的Schema置信度
                    for result in results:
                        if result.schema_file == llm_result:
                            result.confidence += 0.1  # 给LLM选择的Schema加分
                            result.method = 'llm_assisted'
                            break

                    # 重新排序
                    results.sort(key=lambda x: x.confidence, reverse=True)

        return results
    
    def _ontology_based_detection(self, text: str, manager: DynamicOntologyManager) -> Tuple[float, List[str]]:
        """基于本体实体类型的检测"""
        text_lower = text.lower()
        matched_entities = []
        matched_keywords = []
        
        # 检查实体类型的关键词和模式
        for entity_type, config in manager.entity_types.items():
            # 检查关键词
            if hasattr(config, 'keywords'):
                for keyword in config.keywords:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(f"{entity_type}:{keyword}")
            
            # 检查示例实体
            if hasattr(config, 'examples'):
                for example in config.examples:
                    if example.lower() in text_lower:
                        matched_entities.append(f"{entity_type}:{example}")
        
        # 计算得分
        total_types = len(manager.entity_types)
        entity_score = len(matched_entities) / max(total_types * 2, 1)  # 每个类型期望2个实体
        keyword_score = len(matched_keywords) / max(total_types * 3, 1)  # 每个类型期望3个关键词
        
        final_score = min((entity_score + keyword_score) / 2, 1.0)
        evidence = matched_entities + matched_keywords
        
        return final_score, evidence
    
    def _seed_knowledge_detection(self, seed_knowledge: List[Dict], manager: DynamicOntologyManager) -> Tuple[float, List[str]]:
        """基于种子知识的检测"""
        if not seed_knowledge:
            return 0.0, []
        
        matched_relations = []
        matched_entities = []
        
        # 检查种子知识中的关系类型
        for triple in seed_knowledge:
            predicate = triple.get('predicate', '')
            if predicate in manager.relation_types:
                matched_relations.append(f"关系:{predicate}")
            
            # 检查实体是否符合本体定义
            subject = triple.get('subject', '')
            obj = triple.get('object', '')
            
            for entity_name in [subject, obj]:
                if entity_name:
                    inferred_type = self._infer_entity_type_from_schema(entity_name, manager)
                    if inferred_type:
                        matched_entities.append(f"实体:{entity_name}({inferred_type})")
        
        # 计算得分
        total_relations = len(manager.relation_types)
        relation_score = len(set(matched_relations)) / max(total_relations, 1)
        entity_score = len(matched_entities) / max(len(seed_knowledge) * 2, 1)
        
        final_score = min((relation_score + entity_score) / 2, 1.0)
        evidence = list(set(matched_relations + matched_entities))
        
        return final_score, evidence
    
    def _document_structure_detection(self, text: str, manager: DynamicOntologyManager) -> Tuple[float, List[str]]:
        """基于文档结构特征的检测"""
        evidence = []
        score = 0.0
        
        # 检查文档中的结构化模式
        # 例如：DoDAF的OV-1, SV-1模式，时空本体的时间表达等
        
        # 提取可能的结构化实体
        structured_entities = re.findall(r'\b[A-Z]{2,3}-\d+\b', text)  # OV-1, SV-1等
        time_expressions = re.findall(r'\d{4}-\d{2}-\d{2}', text)      # 时间表达
        
        structure_matches = 0
        
        # 检查是否匹配Schema中定义的模式
        for entity_type, config in manager.entity_types.items():
            if hasattr(config, 'patterns'):
                for pattern in config.patterns:
                    try:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            structure_matches += len(matches)
                            evidence.append(f"模式:{entity_type}({len(matches)}个)")
                    except re.error:
                        continue
        
        # 基于结构化匹配计算得分
        if structure_matches > 0:
            score = min(structure_matches / 10.0, 1.0)  # 每10个匹配得1分
        
        return score, evidence
    
    def _infer_entity_type_from_schema(self, entity_name: str, manager: DynamicOntologyManager) -> Optional[str]:
        """从Schema推断实体类型"""
        entity_lower = entity_name.lower()
        
        for entity_type, config in manager.entity_types.items():
            # 检查关键词
            if hasattr(config, 'keywords'):
                for keyword in config.keywords:
                    if keyword.lower() in entity_lower:
                        return entity_type
            
            # 检查模式
            if hasattr(config, 'patterns'):
                for pattern in config.patterns:
                    try:
                        if re.match(pattern, entity_name, re.IGNORECASE):
                            return entity_type
                    except re.error:
                        continue
        
        return None
    
    def get_best_schema(self, document_text: str, seed_knowledge: List[Dict] = None) -> Optional[str]:
        """获取最佳匹配的Schema"""
        results = self.detect_schema(document_text, seed_knowledge)

        if results and results[0].confidence > 0.05:  # 进一步降低最低置信度阈值
            return results[0].schema_file

        return None
    
    def get_schema_suggestions(self, document_text: str, seed_knowledge: List[Dict] = None) -> Dict[str, str]:
        """获取Schema建议和理由"""
        results = self.detect_schema(document_text, seed_knowledge)
        suggestions = {}
        
        for result in results:
            if result.confidence > 0.1:
                reason = f"置信度: {result.confidence:.2f}, 证据: {', '.join(result.evidence[:2])}"
                suggestions[result.schema_file] = reason
        
        return suggestions

    def _llm_schema_decision(self, document_text: str, candidate_schemas: List[SchemaDetectionResult]) -> Optional[str]:
        """LLM辅助Schema决策"""
        try:
            from pipeline.llm_client import LLMClient

            llm_client = LLMClient()

            # 构建候选Schema描述
            schema_descriptions = []
            for result in candidate_schemas:
                manager = self.ontology_managers[result.schema_file]
                schema_info = getattr(manager, 'metadata', {})
                description = schema_info.get('description', f'Schema: {result.schema_file}')

                schema_descriptions.append(f"""
Schema: {result.schema_file}
描述: {description}
置信度: {result.confidence:.3f}
证据: {', '.join(result.evidence)}
""")

            # LLM Prompt
            prompt = f"""
你是一个专业的知识图谱本体选择专家。请根据给定的文档内容，从候选Schema中选择最适合的一个。

文档内容：
{document_text[:1000]}...

候选Schema：
{''.join(schema_descriptions)}

请分析文档的主要内容和结构特征，选择最适合的Schema。只需要回答Schema文件名，不需要解释。

最适合的Schema是："""

            response = llm_client.generate_response(prompt, max_tokens=50)

            # 提取Schema文件名
            for result in candidate_schemas:
                if result.schema_file in response:
                    print(f"🎯 LLM选择: {result.schema_file}")
                    return result.schema_file

            return None

        except Exception as e:
            print(f"⚠️ LLM辅助决策失败: {e}")
            return None

# 全局Schema检测器实例
schema_detector = SchemaDetector()
