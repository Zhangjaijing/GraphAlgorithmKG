"""
会话管理器
管理处理会话的完整生命周期，包括中间结果的保存和检索
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class SessionMetadata:
    """会话元数据"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    document_path: str
    schema_used: str
    total_processing_time: float
    stages_completed: List[str]
    final_stats: Dict[str, Any]

class SessionManager:
    """会话管理器"""
    
    def __init__(self, base_path: str = "results"):
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"
        self.cache_path = self.base_path / "cache"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 当前会话
        self.current_session = None
        self.current_session_path = None
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.sessions_path,
            self.base_path / "knowledge_graphs",
            self.base_path / "analysis",
            self.base_path / "exports",
            self.cache_path / "entities",
            self.cache_path / "schemas"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def start_session(self, document_path: str) -> str:
        """
        开始新的处理会话
        
        Args:
            document_path: 输入文档路径
            
        Returns:
            会话ID
        """
        # 生成会话ID
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = session_id
        
        # 创建会话目录
        self.current_session_path = self.sessions_path / session_id
        self.current_session_path.mkdir(exist_ok=True)
        
        # 初始化会话元数据
        metadata = SessionMetadata(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            document_path=document_path,
            schema_used="",
            total_processing_time=0.0,
            stages_completed=[],
            final_stats={}
        )
        
        self._save_metadata(metadata)
        
        print(f"🚀 开始新会话: {session_id}")
        print(f"📁 会话目录: {self.current_session_path}")
        
        return session_id
    
    def save_stage_result(self, stage_name: str, data: Any,
                         description: str = "", input_summary: str = "",
                         output_summary: str = "") -> str:
        """
        保存阶段结果，包含输入输出摘要

        Args:
            stage_name: 阶段名称
            data: 要保存的数据
            description: 阶段描述
            input_summary: 输入数据摘要
            output_summary: 输出数据摘要

        Returns:
            保存的文件路径
        """
        if not self.current_session:
            raise ValueError("没有活动会话，请先调用 start_session()")
        
        # 生成文件名（带序号）
        stage_files = list(self.current_session_path.glob("*.json"))
        stage_number = len([f for f in stage_files if not f.name.startswith("session_")]) + 1
        
        filename = f"{stage_number:02d}_{stage_name}.json"
        file_path = self.current_session_path / filename
        
        # 准备保存的数据
        stage_data = {
            "stage_name": stage_name,
            "stage_number": stage_number,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "data": data
        }
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stage_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 更新元数据
        self._update_metadata_stage(stage_name)
        
        print(f"💾 保存阶段结果: {filename}")
        print(f"   📝 描述: {description}")
        if input_summary:
            print(f"   📥 输入: {input_summary}")
        if output_summary:
            print(f"   📤 输出: {output_summary}")
        print(f"   📊 数据大小: {len(json.dumps(data, default=str))} 字符")
        
        return str(file_path)
    
    def save_final_result(self, kg_data: Dict[str, Any],
                         analysis_data: Dict[str, Any] = None,
                         schema_type: str = "mixed") -> Dict[str, str]:
        """
        保存最终结果到按Schema分类的目录

        Args:
            kg_data: 知识图谱数据
            analysis_data: 分析数据
            schema_type: Schema类型 (general/spatiotemporal/mixed)

        Returns:
            保存的文件路径字典
        """
        if not self.current_session:
            raise ValueError("没有活动会话")

        saved_files = {}

        # 确定Schema分类
        schema_category = self._classify_schema_type(schema_type)

        # 确保目录存在
        kg_output_path = self.base_path / "knowledge_graphs" / schema_category
        analysis_output_path = self.base_path / "analysis"
        kg_output_path.mkdir(parents=True, exist_ok=True)
        analysis_output_path.mkdir(parents=True, exist_ok=True)

        # 保存知识图谱
        kg_filename = f"{self.current_session}_{schema_category}_kg.json"
        kg_path = kg_output_path / kg_filename

        with open(kg_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2, default=str)

        saved_files["knowledge_graph"] = str(kg_path)

        # 保存分析报告
        if analysis_data:
            analysis_filename = f"{self.current_session}_{schema_category}_analysis.json"
            analysis_path = analysis_output_path / analysis_filename

            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)

            saved_files["analysis"] = str(analysis_path)

        # 同时保存到根knowledge_graphs目录（向后兼容）
        legacy_kg_path = self.base_path / "knowledge_graphs" / f"{self.current_session}_knowledge_graph.json"
        legacy_kg_path.parent.mkdir(parents=True, exist_ok=True)
        with open(legacy_kg_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"📦 保存最终结果 (Schema: {schema_category}):")
        for result_type, path in saved_files.items():
            print(f"   {result_type}: {path}")

        return saved_files

    def _classify_schema_type(self, schema_path: str) -> str:
        """根据schema路径分类"""
        if not schema_path:
            return "mixed"

        schema_path_lower = schema_path.lower()

        if "schema_config" in schema_path_lower or "general" in schema_path_lower:
            return "general"
        elif "spatiotemporal" in schema_path_lower or "spatial" in schema_path_lower:
            return "spatiotemporal"
        else:
            return "mixed"
    
    def end_session(self, final_stats: Dict[str, Any] = None):
        """
        结束当前会话
        
        Args:
            final_stats: 最终统计信息
        """
        if not self.current_session:
            return
        
        # 更新元数据
        metadata = self._load_metadata()
        metadata.end_time = datetime.now().isoformat()
        metadata.final_stats = final_stats or {}
        
        # 计算总处理时间
        start_time = datetime.fromisoformat(metadata.start_time)
        end_time = datetime.fromisoformat(metadata.end_time)
        metadata.total_processing_time = (end_time - start_time).total_seconds()
        
        self._save_metadata(metadata)
        
        # 创建latest软链接
        self._update_latest_link()
        
        print(f"🏁 会话结束: {self.current_session}")
        print(f"⏱️ 总耗时: {metadata.total_processing_time:.2f}s")
        print(f"📋 完成阶段: {len(metadata.stages_completed)} 个")
        
        self.current_session = None
        self.current_session_path = None
    
    def get_stage_result(self, session_id: str, stage_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定会话的阶段结果
        
        Args:
            session_id: 会话ID
            stage_name: 阶段名称
            
        Returns:
            阶段数据
        """
        session_path = self.sessions_path / session_id
        if not session_path.exists():
            return None
        
        # 查找匹配的阶段文件
        for file_path in session_path.glob(f"*_{stage_name}.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        sessions = []
        
        for session_dir in self.sessions_path.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / "session_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        sessions.append(metadata)
        
        # 按时间排序
        sessions.sort(key=lambda x: x['start_time'], reverse=True)
        return sessions
    
    def get_intermediate_results(self, session_id: str) -> Dict[str, str]:
        """
        获取会话的所有中间结果文件路径
        
        Args:
            session_id: 会话ID
            
        Returns:
            阶段名称到文件路径的映射
        """
        session_path = self.sessions_path / session_id
        if not session_path.exists():
            return {}
        
        results = {}
        for file_path in session_path.glob("*.json"):
            if not file_path.name.startswith("session_"):
                # 提取阶段名称
                parts = file_path.stem.split("_", 1)
                if len(parts) == 2:
                    stage_name = parts[1]
                    results[stage_name] = str(file_path)
        
        return results
    
    def _save_metadata(self, metadata: SessionMetadata):
        """保存会话元数据"""
        metadata_path = self.current_session_path / "session_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self) -> SessionMetadata:
        """加载会话元数据"""
        metadata_path = self.current_session_path / "session_metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return SessionMetadata(**data)
    
    def _update_metadata_stage(self, stage_name: str):
        """更新元数据中的阶段信息"""
        metadata = self._load_metadata()
        if stage_name not in metadata.stages_completed:
            metadata.stages_completed.append(stage_name)
        self._save_metadata(metadata)
    
    def _update_latest_link(self):
        """更新latest软链接"""
        latest_link = self.sessions_path / "latest"
        
        # 删除旧的软链接
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        
        # 创建新的软链接
        try:
            latest_link.symlink_to(self.current_session)
        except OSError:
            # Windows系统可能不支持软链接，创建一个文本文件
            with open(latest_link.with_suffix('.txt'), 'w') as f:
                f.write(self.current_session)

# 全局会话管理器实例
session_manager = SessionManager()
