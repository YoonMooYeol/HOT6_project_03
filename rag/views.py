from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from .method import RAGProcessor, RAGQuery


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
            3. Chroma DB 초기화 또는 로드
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
        DB_DIR = "embeddings/chroma_db"
        CSV_PATTERN = "data/rag/*.csv"

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
            vectorstore, existing_ids = RAGProcessor.initialize_chroma_db(DB_DIR)
            total_new_docs = 0
            processed_count = 0

            # 4. 각 CSV 파일 처리
            for csv_file in new_files:
                try:
                    # 4.1. CSV 파일 로드 및 메타데이터 추가
                    docs = RAGProcessor.load_csv_with_metadata(csv_file)
                    if not docs:
                        continue

                    # 4.2. 새 문서 필터링
                    new_docs = RAGProcessor.filter_new_documents(docs, existing_ids, csv_file)
                    if not new_docs:
                        continue

                    # 4.3. 문서 분할
                    total_new_docs += len(new_docs)
                    splits = RAGProcessor.split_documents(new_docs)
                    
                    # 4.4. 데이터 준비
                    texts, metadatas, ids = RAGProcessor.prepare_data_for_chroma(splits)
                    
                    # 4.5. 임베딩 생성 및 저장
                    print(f"\n임베딩 생성 중... (총 {len(texts)}개 텍스트)")
                    embeddings = RAGProcessor.create_embeddings(texts)
                    
                    # 4.6. Chroma DB 업데이트
                    vectorstore = RAGProcessor.update_chroma_db(
                        vectorstore, 
                        texts, 
                        embeddings,  
                        metadatas, 
                        ids, 
                        DB_DIR
                    )
                    
                    # 4.7. 처리 완료 기록
                    RAGProcessor.save_processed_file_info(csv_file)
                    processed_count += 1

                except Exception as e:
                    print(f"파일 처리 중 오류 발생 ({csv_file}): {e}")
                    continue

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
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RAGQueryView(APIView):
    """
    RAG 시스템을 이용한 질의응답 API 뷰
    
    Endpoints:
        POST /rag/query/: 사용자 질문을 받아 관련 문서를 검색하고 답변 생성
    """
    parser_classes = (JSONParser,)

    def post(self, request):
        """
        사용자 질문에 대한 답변을 생성합니다.
        
        Process:
            1. 사용자 질문 검증
            2. QA 체인 생성
            3. 질문 처리 및 답변 생성
            4. 답변과 참조 문서 반환
        
        Args:
            request.data: {
                'question': str  # 사용자 질문
            }
        
        Returns:
            Response: {
                'answer': str,  # GPT 모델이 생성한 답변
                'source_documents': list  # 참조한 문서 목록
            }
        """
        try:
            # 1. 질문 검증
            question = request.data.get('question')
            if not question:
                return Response({'error': '질문이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. QA 체인 생성 및 질문 처리
            print(f"받은 질문: {question}")
            qa_chain = RAGQuery.create_qa_chain("embeddings/chroma_db")
            result = qa_chain.invoke({"question": question})

            # 3. 응답 반환
            return Response({
                'answer': result['answer'],
                'source_documents': [
                    {'content': doc.page_content, 'metadata': doc.metadata}
                    for doc in result['source_documents']
                ]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


