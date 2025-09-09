#!/usr/bin/env python3
"""
统一测试运行器
支持分类运行不同类型的测试
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    print("-" * 50)
    
    start_time = time.time()
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit/", "-v", "--tb=short", "--color=yes"
    ], cwd=Path(__file__).parent.parent)
    
    duration = time.time() - start_time
    print(f"⏱️ 单元测试耗时: {duration:.2f}秒")
    return result.returncode == 0

def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    print("-" * 50)
    
    start_time = time.time()
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/", "-v", "--tb=short", "--color=yes"
    ], cwd=Path(__file__).parent.parent)
    
    duration = time.time() - start_time
    print(f"⏱️ 集成测试耗时: {duration:.2f}秒")
    return result.returncode == 0

def run_system_tests():
    """运行系统测试"""
    print("🖥️ 运行系统测试...")
    print("-" * 50)
    
    start_time = time.time()
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/system/", "-v", "--tb=short", "--color=yes"
    ], cwd=Path(__file__).parent.parent)
    
    duration = time.time() - start_time
    print(f"⏱️ 系统测试耗时: {duration:.2f}秒")
    return result.returncode == 0

def run_specific_test(test_path):
    """运行指定的测试文件"""
    print(f"🎯 运行指定测试: {test_path}")
    print("-" * 50)
    
    start_time = time.time()
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_path, "-v", "--tb=short", "--color=yes"
    ], cwd=Path(__file__).parent.parent)
    
    duration = time.time() - start_time
    print(f"⏱️ 测试耗时: {duration:.2f}秒")
    return result.returncode == 0

def run_all_tests():
    """运行所有测试"""
    print("🚀 运行所有测试")
    print("=" * 60)
    
    start_time = time.time()
    success_count = 0
    total_count = 3
    
    tests = [
        ("单元测试", run_unit_tests),
        ("集成测试", run_integration_tests), 
        ("系统测试", run_system_tests)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 开始 {test_name}")
        if test_func():
            success_count += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    total_duration = time.time() - start_time
    print(f"\n📊 测试总结:")
    print(f"   通过: {success_count}/{total_count}")
    print(f"   总耗时: {total_duration:.2f}秒")
    print(f"   成功率: {success_count/total_count*100:.1f}%")
    
    return success_count == total_count

def list_available_tests():
    """列出可用的测试文件"""
    print("📋 可用的测试文件:")
    
    test_dirs = ["tests/unit", "tests/integration", "tests/system"]
    
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            print(f"\n📁 {test_dir}:")
            for test_file in test_path.glob("test_*.py"):
                print(f"   - {test_file.name}")

def main():
    parser = argparse.ArgumentParser(description="统一测试运行器")
    parser.add_argument("--type", choices=["unit", "integration", "system", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--file", help="运行指定的测试文件")
    parser.add_argument("--list", action="store_true", help="列出可用的测试文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_tests()
        return
    
    if args.file:
        success = run_specific_test(args.file)
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "system":
        success = run_system_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
