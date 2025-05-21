#!/usr/bin/env python3
import os
import sys
import subprocess
from typing import Dict, List
import json
import requests

def map_status_code(code: str):
    if code.startswith('R'):
        return 'Renamed'
    elif code.startswith('C'):
        return 'Copied'
    return {
        'A': 'Added',
        'M': 'Modified',
        'D': 'Deleted',
        'T': 'Type Changed',
        'U': 'Unmerged Conflict',
        'X': 'Unknown'
    }.get(code, 'Unknown')

def get_diff_content(files: List) -> Dict:
    """스테이징된 파일들의 diff 내용을 가져옵니다."""
    diff_content = {}
    for file in files:
        try:
            # 파일의 diff 내용 가져오기
            diff = subprocess.check_output(
                ["git", "diff", "--cached", "--", file], 
                text=True,
                encoding='utf-8',  # 명시적 인코딩 지정
                errors='replace',  # 인코딩 오류 처리
                stderr=subprocess.STDOUT
            )
            if diff:
                diff_content[file] = {"diff": diff}
            
            # 파일 변경 유형    
            status = subprocess.check_output(
                ["git", "diff", "--cached", "--name-status","--", file], 
                text=True,  
                encoding='utf-8',  
                errors='replace',  
                stderr=subprocess.STDOUT
            )
            if status:
                diff_content[file]["status"] = map_status_code(status.split("\t")[0])
        except subprocess.CalledProcessError:
            pass
    return diff_content

def generate_commit_message(diff_content: Dict, prompt: str) -> str:
    input_message = ""

    for file, info in diff_content.items():
        
        diff = info["diff"]
        
        change_type = "UnKnown"
        if "status" in info.keys():
            change_type = info["status"]
        
        input_message += f"File: {file} ({change_type})\n"

        lines = diff.splitlines()
        filtered_lines = []

        for line in lines:
            # 중요 정보만 추출
            if line.startswith(('@@')):
                filtered_lines.append(line)
            elif line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
                content = line.strip()
                if content:
                    filtered_lines.append(line)

        if filtered_lines:
            input_message += "\n".join(filtered_lines)
            input_message += "\n\n"

    # print(input_message)
    return request_openai(input_message.strip(), prompt)

def request_openai(input_message, prompt):
    # 환경 변수에서 API 키 불러오기
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

    # 요청 본문 구성
    payload = {
        "model": "gpt-4.1-mini-2025-04-14",
        "instructions": prompt,
        "input": input_message
    }

    # 헤더 설정
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # API 요청
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        data=json.dumps(payload)
    )

    # 결과 출력
    if response.status_code == 200:
        
        json_data = json.loads(response.json()["output"][0]["content"][0]["text"])
        json_data["length"] = len(json_data["items"])
            
        return json_data
    else:
        raise Exception(f"요청 실패: {response.status_code} {response.text}")


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 스테이징된 파일 목록 가져오기
    staged_files = sys.argv[1].split() if len(sys.argv) >= 1 else []
    # prompt 가져오기
    prompt_path = "./scripts/prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"지정된 파일을 찾을 수 없습니다: {prompt_path}")

    # 파일 변경 내용 가져오기
    diff_content = get_diff_content(staged_files)
    
    # 커밋 메시지 생성
    commit_message = generate_commit_message(diff_content, prompt)
    
    print(json.dumps(commit_message, ensure_ascii=False))
if __name__ == "__main__":
    main()