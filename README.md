# HOT6_project_03
핫식스프로젝트 백엔드

## 가상환경 설정

1. 파이썬 가상환경 생성
```bash
python -m venv venv
```

2. 가상환경 활성화
- Windows
```bash
venv\Scripts\activate
```
- Mac/Linux
```bash
source venv/bin/activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt 
```

4. 가상환경 비활성화
```bash
deactivate
```

## Django 프로젝트 실행 방법

1. 환경 변수 설정
- 프로젝트 루트에 `.env` 파일 생성
```bash
DJANGO_SETTINGS_MODULE=config.settings
```

2. Django 마이그레이션
```bash
python manage.py migrate
```

3. 서버 실행
```bash
python manage.py runserver
```

## API 인증
이 프로젝트는 JWT(JSON Web Token) 인증을 사용합니다. API 요청 시 Authorization 헤더에 JWT 토큰을 포함해야 합니다.

## API 엔드포인트

### RAG API
- `GET /v1/rag/rag/`: RAG 설정 정보 조회
- `POST /v1/rag/rag/`: 새로운 RAG 설정 생성

각 엔드포인트의 자세한 요청/응답 형식은 API 문서를 참조하세요.
