#!/usr/bin/env python3
import os

def seeker(root_dir='.'):
    """
    root_dir부터 시작하여 모든 하위 디렉토리까지 탐색하면서
    확장자가 .py 인 모든 파일의 경로와 파일 내용을 순서대로 출력합니다.
    """
    for current_path, dirs, files in os.walk(root_dir):
        for file_name in files:
            if file_name.endswith('.py'):
                full_path = os.path.join(current_path, file_name)
                print(full_path)  # 경로명 출력
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content)  # 파일 내용 출력
                except Exception as e:
                    print(f"파일을 열 수 없습니다: {e}")

if __name__ == "__main__":
    seeker()
