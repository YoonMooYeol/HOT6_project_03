from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from .method import RAGProcessor, RAGQuery
from dotenv import load_dotenv
import os
from tqdm import tqdm

# 환경 변수 로드
load_dotenv()

# RAGProcessor에서 정의된 경로 사용
DB_DIR = RAGProcessor.DB_DIR
CSV_PATTERN = "data/rag/*.csv"

# DB_DIR이 존재하지 않으면 생성
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

class RAGSetupView(APIView):
    """
    RAG 시스템 초기 설정을 위한 API 뷰
    
    Endpoints:
        POST /rag/setup/: CSV 파일을 읽어 Chroma DB에 임베딩을 저장
    """

    def get(self, request):
        """API 엔드포인트 설명을 반환합니다."""
        return Response({
            'message': 'RAG 시스템 설정 API',
            'usage': {
                'method': 'POST',
                'description': 'CSV 파일을 처리하여 RAG 시스템의 벡터 데이터베이스를 구축합니다.',
                'endpoint': '/v1/rag/setup/'
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        CSV 파일을 처리하여 RAG 시스템의 벡터 데이터베이스를 구축합니다.
        
        Process:
            1. CSV 파일 로드 및 전처리
            2. 새로운(미처리) 파일 필터링
            3. Chroma DB 초기화
            4. 각 CSV 파일별 처리:
                - 메타데이터와 함께 문서 로드
                - 새로운 문서 필터링
                - 문서 분할(청크)
                - Chroma DB에 데이터 저장
            5. 처리 결과 반환
        
        Returns:
            Response: {
                'message': str,
                'processed_files': int,
                'new_docs': int,
                'total_docs': int
            }
        """

        try:
            # 1. CSV 파일 로드
            csv_files = RAGProcessor.load_and_preprocess_csv(CSV_PATTERN)
            new_files = RAGProcessor.filter_processed_files(csv_files)

            # 2. 새로운 파일이 없는 경우 처리
            if not new_files:
                return Response({
                    'message': '새로운 파일이 없습니다.',
                    'processed_files': len(csv_files)
                }, status=status.HTTP_200_OK)

            # 3. Chroma DB 초기화
            vectorstore, existing_ids = RAGProcessor.initialize_chroma_db()

            # 4. 파일 처리 및 DB 업데이트
            vectorstore, total_new_docs, processed_count = RAGProcessor.process_files(
                new_files, existing_ids, vectorstore, RAGProcessor.DB_DIR
            )

            # 5. 처리 결과 반환
            if vectorstore:
                total_docs = vectorstore._collection.count()
                return Response({
                    'message': '새로운 데이터 처리 완료',
                    'processed_files': processed_count,
                    'new_docs': total_new_docs,
                    'total_docs': total_docs
                }, status=status.HTTP_201_CREATED)

            return Response({
                'message': '처리된 문서가 없습니다.',
                'processed_files': processed_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RAGQueryView(APIView):
    parser_classes = (JSONParser,)
    """
    RAG 질의응답 API
    
    Endpoints:
        POST /rag/query/: 사용자 질문에 대한 답변을 생성
    """
    def get(self, request):
        """API 사용 방법을 반환합니다."""
        return Response({
            "question": "너 지금 또 감정적이야"
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """사용자 질문에 대한 답변을 생성합니다."""
        try:
            # 질문 추출
            question = request.data.get('question')
            if not question:
                return Response(
                    {'error': '질문이 필요합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 답변 생성
            result = RAGQuery.get_answer(question)
            
            # 출력값 정리 - 따옴표와 백슬래시 제거
            cleaned_output = result.replace('"', '').replace('\\', '')
            
            return Response(cleaned_output, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

