import os
from pathlib import Path


def fix_imports():
    # 获取所有测试文件
    test_files = Path('tests').rglob('test_*.py')
    
    for file_path in test_files:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # 替换导入语句
        content = content.replace('from src.', 'from auto_questionnaire.')
        content = content.replace('import src.', 'import auto_questionnaire.')
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")

if __name__ == '__main__':
    fix_imports() 