#!/usr/bin/env python3
"""
示例运行器
统一管理和运行所有示例
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


class ExampleRunner:
    """示例运行器类"""
    
    def __init__(self):
        self.examples_dir = Path(__file__).parent
        self.project_root = self.examples_dir.parent
        
        # 定义示例分类
        self.examples = {
            'basic': [
                {
                    'file': 'basic/01_simple_kg_building.py',
                    'name': '简单知识图谱构建',
                    'description': '演示最基本的知识图谱构建流程',
                    'duration': '~30秒',
                    'interactive': False
                },
                {
                    'file': 'basic/02_schema_detection.py',
                    'name': 'Schema检测演示',
                    'description': '演示如何检测文档适合的Schema类型',
                    'duration': '~45秒',
                    'interactive': False
                }
            ],
            'advanced': [
                {
                    'file': 'advanced/04_dynamic_schema_discovery.py',
                    'name': '动态Schema发现',
                    'description': '演示问题驱动的Schema生成功能',
                    'duration': '~2分钟',
                    'interactive': False
                }
            ],
            'complete': [
                {
                    'file': 'complete/08_four_scenarios_demo.py',
                    'name': '四个场景完整演示',
                    'description': '演示所有四个动态Schema场景',
                    'duration': '~3分钟',
                    'interactive': False
                }
            ],
            'interactive': [
                {
                    'file': 'interactive/10_user_guided_schema.py',
                    'name': '用户引导Schema生成',
                    'description': '交互式创建定制化Schema',
                    'duration': '5-15分钟',
                    'interactive': True
                }
            ]
        }
    
    def list_examples(self):
        """列出所有可用示例"""
        print("📚 可用示例列表")
        print("=" * 60)
        
        for category, examples in self.examples.items():
            category_names = {
                'basic': '🔰 基础示例',
                'advanced': '🚀 高级示例',
                'complete': '🔄 完整流程示例',
                'interactive': '💬 交互式示例'
            }
            
            print(f"\n{category_names.get(category, category.upper())}")
            print("-" * 40)
            
            for i, example in enumerate(examples, 1):
                interactive_mark = " 🎮" if example['interactive'] else ""
                print(f"{i:2d}. {example['name']}{interactive_mark}")
                print(f"    文件: {example['file']}")
                print(f"    描述: {example['description']}")
                print(f"    预计时间: {example['duration']}")
                print()
        
        print("💡 提示:")
        print("   🎮 标记的示例需要用户交互输入")
        print("   使用 --category 参数运行特定类别的示例")
        print("   使用 --example 参数运行特定示例")
    
    def run_example(self, example_file, verbose=False):
        """运行单个示例"""
        example_path = self.examples_dir / example_file
        
        if not example_path.exists():
            print(f"❌ 示例文件不存在: {example_file}")
            return False
        
        print(f"🚀 运行示例: {example_file}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            # 运行示例
            cmd = [sys.executable, str(example_path)]
            if verbose:
                cmd.append('--verbose')
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                capture_output=False,  # 直接显示输出
                text=True
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"\n✅ 示例运行成功! (耗时: {duration:.1f}秒)")
                return True
            else:
                print(f"\n❌ 示例运行失败! (返回码: {result.returncode})")
                return False
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️ 用户中断示例运行")
            return False
        except Exception as e:
            print(f"\n❌ 运行示例时出错: {e}")
            return False
    
    def run_category(self, category, verbose=False):
        """运行指定类别的所有示例"""
        if category not in self.examples:
            print(f"❌ 未知类别: {category}")
            print(f"可用类别: {', '.join(self.examples.keys())}")
            return False
        
        examples = self.examples[category]
        category_names = {
            'basic': '基础示例',
            'advanced': '高级示例', 
            'complete': '完整流程示例',
            'interactive': '交互式示例'
        }
        
        print(f"🎯 运行 {category_names.get(category, category)} 类别")
        print("=" * 60)
        
        successful = 0
        total = len(examples)
        
        for i, example in enumerate(examples, 1):
            print(f"\n📋 示例 {i}/{total}: {example['name']}")
            
            if example['interactive']:
                # 交互式示例需要用户确认
                confirm = input(f"这是交互式示例，需要用户输入。是否继续？ (y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("⏭️ 跳过交互式示例")
                    continue
            
            if self.run_example(example['file'], verbose):
                successful += 1
            
            # 示例间的间隔
            if i < total:
                print("\n" + "="*30)
                time.sleep(1)
        
        print(f"\n📊 类别执行结果: {successful}/{total} 成功")
        return successful == total
    
    def run_all_examples(self, verbose=False, skip_interactive=False):
        """运行所有示例"""
        print("🚀 运行所有示例")
        print("=" * 60)
        
        total_successful = 0
        total_examples = 0
        
        for category in ['basic', 'advanced', 'complete', 'interactive']:
            if skip_interactive and category == 'interactive':
                print(f"\n⏭️ 跳过交互式示例类别")
                continue
            
            examples = self.examples[category]
            total_examples += len(examples)
            
            print(f"\n🎯 开始 {category} 类别")
            
            for example in examples:
                if example['interactive'] and skip_interactive:
                    print(f"⏭️ 跳过交互式示例: {example['name']}")
                    continue
                
                if example['interactive']:
                    confirm = input(f"\n交互式示例: {example['name']}\n是否运行？ (y/N): ").strip().lower()
                    if confirm not in ['y', 'yes']:
                        print("⏭️ 跳过")
                        continue
                
                if self.run_example(example['file'], verbose):
                    total_successful += 1
                
                print("\n" + "-"*30)
        
        print(f"\n📊 总体执行结果: {total_successful}/{total_examples} 成功")
        return total_successful == total_examples
    
    def find_example_by_name(self, name):
        """根据名称查找示例"""
        name_lower = name.lower()
        
        for category, examples in self.examples.items():
            for example in examples:
                # 检查文件名匹配
                file_name = Path(example['file']).stem
                if name_lower in file_name.lower():
                    return example['file']
                
                # 检查示例名称匹配
                if name_lower in example['name'].lower():
                    return example['file']
        
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GraphAlgorithmKG 示例运行器")
    parser.add_argument("--list", action="store_true", help="列出所有可用示例")
    parser.add_argument("--category", choices=['basic', 'advanced', 'complete', 'interactive'],
                       help="运行指定类别的示例")
    parser.add_argument("--example", help="运行指定的示例（可使用文件名或示例名称）")
    parser.add_argument("--all", action="store_true", help="运行所有示例")
    parser.add_argument("--skip-interactive", action="store_true", help="跳过交互式示例")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    runner = ExampleRunner()
    
    if args.list:
        runner.list_examples()
        return 0
    
    if args.example:
        # 查找并运行指定示例
        example_file = runner.find_example_by_name(args.example)
        if example_file:
            success = runner.run_example(example_file, args.verbose)
            return 0 if success else 1
        else:
            print(f"❌ 未找到示例: {args.example}")
            print("💡 使用 --list 查看所有可用示例")
            return 1
    
    if args.category:
        success = runner.run_category(args.category, args.verbose)
        return 0 if success else 1
    
    if args.all:
        success = runner.run_all_examples(args.verbose, args.skip_interactive)
        return 0 if success else 1
    
    # 默认显示帮助信息
    print("🎯 GraphAlgorithmKG 示例运行器")
    print("=" * 40)
    print("使用 --help 查看所有选项")
    print("使用 --list 查看所有可用示例")
    print("使用 --category basic 运行基础示例")
    print("使用 --example 01_simple 运行特定示例")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
