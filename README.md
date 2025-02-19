# 백엔드
## 1. 기본 구조
- Django + DRF 설정 완료
- 데이터베이스 설정 (SQLite3)
- OpenAI API 연동

## 2. 모델
```md
# Message 모델
- id
- user (ForeignKey)
- input_content (원본 메시지)
- output_content (선택된 변환 메시지)
- translated_content (3개의 변환 옵션)
- warm_mode (다정모드 상태)
- created_at, updated_at

# UserSettings 모델
- user (OneToOneField)
- warm_mode (다정모드 ON/OFF)
```

## 3. 서비스
```md
# MessageTranslator 서비스
- 메시지 변환 로직 구현
- 다정모드 상태에 따라 다르게 처리


## 4. API 엔드포인트
```md
GET /api/v1/chat/json-drf/
- 메시지 목록 조회

POST /api/v1/chat/json-drf/
- 메시지 전송
- 다정모드 상태에 따라 다르게 처리

POST /api/v1/chat/select-translation/<message_id>/
- 3개 변환 옵션 중 하나 선택

POST /api/v1/chat/toggle-warm-mode/
- 다정모드 ON/OFF 전환
```

## 5. 구현 상황
### 구현된 기능 ✅
- 메시지 전송 및 데이터베이스(SQLite) 저장
- GPT를 통한 메시지 변환 (3개 옵션)
- 변환된 메시지 중 선택 기능
- 다정모드 토글 기능
- 사용자별 다정모드 설정 유지

### 아직 구현되지 않은 기능 ❌
- 사용자 구분 기능
- 현재는 superuser(user_id 1)로만 수행 중
- 사용자 인증/인가 (JWT)
- 데이터베이스 PostgreSQL 전환
- ...
