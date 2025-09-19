#!/usr/bin/env python3
"""
数据管理工具
统一管理项目中的所有数据文件
"""

import os
import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging


class DataManager:
    """数据管理器类"""
    
    def __init__(self, data_root: Optional[str] = None):
        """
        初始化数据管理器
        
        Args:
            data_root: 数据根目录路径，默认为当前文件所在目录
        """
        if data_root:
            self.data_root = Path(data_root)
        else:
            self.data_root = Path(__file__).parent
        
        # 确保数据目录存在
        self._ensure_directories()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            'documents/samples',
            'documents/dodaf',
            'knowledge/seed',
            'knowledge/generated',
            'training/raw',
            'training/processed',
            'training/splits',
            'test/scenarios',
            'test/fixtures',
            'cache/schemas',
            'cache/entities'
        ]
        
        for directory in directories:
            dir_path = self.data_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def load_documents(self, category: str = 'samples') -> List[Dict[str, Any]]:
        """
        加载文档数据
        
        Args:
            category: 文档类别 ('samples', 'dodaf', 'test')
            
        Returns:
            文档列表
        """
        documents = []
        
        if category == 'test':
            doc_dir = self.data_root / 'documents'
        else:
            doc_dir = self.data_root / 'documents' / category
        
        if not doc_dir.exists():
            self.logger.warning(f"文档目录不存在: {doc_dir}")
            return documents
        
        # 加载不同格式的文档
        for file_path in doc_dir.rglob('*'):
            if file_path.is_file():
                try:
                    doc_data = self._load_single_document(file_path)
                    if doc_data:
                        doc_data['category'] = category
                        doc_data['file_path'] = str(file_path)
                        documents.append(doc_data)
                except Exception as e:
                    self.logger.error(f"加载文档失败 {file_path}: {e}")
        
        return documents
    
    def _load_single_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载单个文档文件"""
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {
                    'title': data.get('title', file_path.stem),
                    'content': data.get('content', ''),
                    'metadata': data.get('metadata', {}),
                    'format': 'json'
                }
            
            elif suffix == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 简单解析markdown标题
                lines = content.split('\n')
                title = file_path.stem
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                return {
                    'title': title,
                    'content': content,
                    'metadata': {},
                    'format': 'markdown'
                }
            
            elif suffix == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    'title': file_path.stem,
                    'content': content,
                    'metadata': {},
                    'format': 'text'
                }
            
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
        
        return None
    
    def load_training_data(self, split: str = 'all') -> Dict[str, Any]:
        """
        加载训练数据
        
        Args:
            split: 数据分割 ('train', 'val', 'test', 'all')
            
        Returns:
            训练数据字典
        """
        training_data = {}
        
        # 加载原始数据
        raw_dir = self.data_root / 'training' / 'raw'
        if raw_dir.exists():
            training_data['raw'] = self._load_training_files(raw_dir)
        
        # 加载处理后数据
        processed_dir = self.data_root / 'training' / 'processed'
        if processed_dir.exists():
            training_data['processed'] = self._load_training_files(processed_dir)
        
        # 加载分割数据
        if split != 'all':
            splits_dir = self.data_root / 'training' / 'splits'
            split_file = splits_dir / f'{split}.json'
            if split_file.exists():
                with open(split_file, 'r', encoding='utf-8') as f:
                    training_data['split'] = json.load(f)
        
        return training_data
    
    def _load_training_files(self, directory: Path) -> Dict[str, Any]:
        """加载训练文件目录中的所有文件"""
        files_data = {}
        
        for file_path in directory.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    files_data[file_path.stem] = json.load(f)
            except Exception as e:
                self.logger.error(f"加载训练文件失败 {file_path}: {e}")
        
        return files_data
    
    def load_test_data(self, scenario: str = 'all') -> Dict[str, Any]:
        """
        加载测试数据
        
        Args:
            scenario: 测试场景 ('scenarios', 'fixtures', 'all')
            
        Returns:
            测试数据字典
        """
        test_data = {}
        
        if scenario in ['scenarios', 'all']:
            scenarios_dir = self.data_root / 'test' / 'scenarios'
            if scenarios_dir.exists():
                test_data['scenarios'] = self._load_test_scenarios(scenarios_dir)
        
        if scenario in ['fixtures', 'all']:
            fixtures_dir = self.data_root / 'test' / 'fixtures'
            if fixtures_dir.exists():
                test_data['fixtures'] = self._load_test_fixtures(fixtures_dir)
        
        return test_data
    
    def _load_test_scenarios(self, directory: Path) -> Dict[str, Any]:
        """加载测试场景数据"""
        scenarios = {}
        
        for file_path in directory.glob('*.py'):
            if file_path.name != '__init__.py':
                # 这里可以扩展为实际加载Python模块中的测试数据
                scenarios[file_path.stem] = {
                    'file': str(file_path),
                    'type': 'python_module'
                }
        
        for file_path in directory.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    scenarios[file_path.stem] = json.load(f)
            except Exception as e:
                self.logger.error(f"加载测试场景失败 {file_path}: {e}")
        
        return scenarios
    
    def _load_test_fixtures(self, directory: Path) -> Dict[str, Any]:
        """加载测试固件数据"""
        fixtures = {}
        
        for file_path in directory.glob('*'):
            if file_path.is_file():
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            fixtures[file_path.stem] = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            fixtures[file_path.stem] = f.read()
                except Exception as e:
                    self.logger.error(f"加载测试固件失败 {file_path}: {e}")
        
        return fixtures
    
    def load_knowledge_data(self, data_type: str = 'seed') -> Dict[str, Any]:
        """
        加载知识数据
        
        Args:
            data_type: 数据类型 ('seed', 'generated', 'all')
            
        Returns:
            知识数据字典
        """
        knowledge_data = {}
        
        if data_type in ['seed', 'all']:
            seed_dir = self.data_root / 'knowledge' / 'seed'
            knowledge_data['seed'] = self._load_knowledge_files(seed_dir)
        
        if data_type in ['generated', 'all']:
            generated_dir = self.data_root / 'knowledge' / 'generated'
            knowledge_data['generated'] = self._load_knowledge_files(generated_dir)
        
        return knowledge_data
    
    def _load_knowledge_files(self, directory: Path) -> Dict[str, Any]:
        """加载知识文件"""
        knowledge = {}
        
        if not directory.exists():
            return knowledge
        
        for file_path in directory.glob('*'):
            if file_path.is_file():
                try:
                    if file_path.suffix == '.csv':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            knowledge[file_path.stem] = list(reader)
                    elif file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            knowledge[file_path.stem] = json.load(f)
                except Exception as e:
                    self.logger.error(f"加载知识文件失败 {file_path}: {e}")
        
        return knowledge
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """验证数据完整性"""
        validation_result = {
            'status': 'success',
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # 检查目录结构
        required_dirs = [
            'documents', 'knowledge', 'training', 'test', 'cache'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.data_root / dir_name
            if not dir_path.exists():
                validation_result['errors'].append(f"缺少必要目录: {dir_name}")
        
        # 统计文件数量
        stats = {}
        for category in ['documents', 'knowledge', 'training', 'test']:
            category_path = self.data_root / category
            if category_path.exists():
                file_count = len(list(category_path.rglob('*')))
                stats[category] = file_count
        
        validation_result['statistics'] = stats
        
        # 检查文件完整性
        self._check_file_integrity(validation_result)
        
        if validation_result['errors']:
            validation_result['status'] = 'error'
        elif validation_result['warnings']:
            validation_result['status'] = 'warning'
        
        return validation_result
    
    def _check_file_integrity(self, validation_result: Dict[str, Any]):
        """检查文件完整性"""
        # 检查重要的数据文件是否存在
        important_files = [
            'knowledge/seed/graph_algorithm_triples.csv',
            'training/entity_inference_data.json',
            'training/schema_classification_data.json'
        ]
        
        for file_path in important_files:
            full_path = self.data_root / file_path
            if not full_path.exists():
                validation_result['warnings'].append(f"重要文件缺失: {file_path}")
    
    def clean_cache(self) -> Dict[str, int]:
        """清理缓存数据"""
        cleaned_count = {'schemas': 0, 'entities': 0, 'total': 0}
        
        # 清理Schema缓存
        schema_cache_dir = self.data_root / 'cache' / 'schemas'
        if schema_cache_dir.exists():
            for file_path in schema_cache_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                    cleaned_count['schemas'] += 1
        
        # 清理实体缓存
        entity_cache_dir = self.data_root / 'cache' / 'entities'
        if entity_cache_dir.exists():
            for file_path in entity_cache_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                    cleaned_count['entities'] += 1
        
        cleaned_count['total'] = cleaned_count['schemas'] + cleaned_count['entities']
        
        return cleaned_count
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据概览"""
        summary = {
            'directories': {},
            'file_counts': {},
            'total_size': 0
        }
        
        for category in ['documents', 'knowledge', 'training', 'test', 'cache']:
            category_path = self.data_root / category
            if category_path.exists():
                files = list(category_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                summary['directories'][category] = str(category_path)
                summary['file_counts'][category] = file_count
                summary['total_size'] += total_size
        
        # 转换字节为可读格式
        summary['total_size_readable'] = self._format_size(summary['total_size'])
        
        return summary
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    """主函数 - 演示数据管理器功能"""
    print("📁 数据管理工具演示")
    print("=" * 50)
    
    # 创建数据管理器
    data_manager = DataManager()
    
    # 获取数据概览
    print("📊 数据概览:")
    summary = data_manager.get_data_summary()
    for category, count in summary['file_counts'].items():
        print(f"   {category}: {count} 个文件")
    print(f"   总大小: {summary['total_size_readable']}")
    
    # 验证数据完整性
    print("\n🔍 数据完整性验证:")
    validation = data_manager.validate_data_integrity()
    print(f"   状态: {validation['status']}")
    if validation['errors']:
        print(f"   错误: {len(validation['errors'])} 个")
    if validation['warnings']:
        print(f"   警告: {len(validation['warnings'])} 个")
    
    # 清理缓存
    print("\n🧹 清理缓存:")
    cleaned = data_manager.clean_cache()
    print(f"   清理文件: {cleaned['total']} 个")
    
    print("\n✅ 数据管理工具演示完成")


if __name__ == "__main__":
    main()
