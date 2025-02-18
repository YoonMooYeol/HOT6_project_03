from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import CSVLoader
from tqdm import tqdm
import os
from glob import glob
import uuid
import pickle
from .models import RAG_DB
import asyncio
from typing import List
import aiohttp
from tqdm.asyncio import tqdm_asyncio

class RAGProcessor:
    @staticmethod
    def load_and_preprocess_csv(csv_pattern):
        """CSV 파일들을 찾아서 반환."""
        csv_files = glob(csv_pattern)
        if not csv_files:
            print(f"CSV 파일을 찾을 수 없습니다: {csv_pattern}")
            return None
        print(f"처리할 CSV 파일: {len(csv_files)}개")
        for file in csv_files:
            print(f"- {file}")
        return csv_files

    @staticmethod
    def filter_processed_files(csv_files):
        """이미 처리된 파일을 제외하고 새로운 파일 목록만 반환."""
        processed_files = set(RAG_DB.objects.values_list('file_path', flat=True))
        new_files = [f for f in csv_files if f not in processed_files]
        print(f"처리할 새로운 CSV 파일: {len(new_files)}개")
        return new_files

    @staticmethod
    def initialize_chroma_db(db_dir):
        """Chroma DB를 초기화하거나 기존 DB를 로드."""
        print("\nChroma DB 확인 중...")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=1000)

        if os.path.exists(db_dir) and os.path.exists(f"{db_dir}/chroma.sqlite3"):
            print("기존 Chroma DB 로드 중...")
            vectorstore = Chroma(
                persist_directory=db_dir,
                embedding_function=embeddings,
                collection_name="korean_dialogue"
            )
            existing_ids = set(vectorstore._collection.get()['ids'])
            print(f"기존 문서 수: {len(existing_ids)}")
        else:
            print("새로운 Chroma DB 생성 중...")
            vectorstore = None
            existing_ids = set()

        return vectorstore, existing_ids

    @staticmethod
    def load_csv_with_metadata(csv_file):
        """CSV 파일을 로드하고 메타데이터 열을 추가."""
        print(f"\n파일 처리 중: {csv_file}")
        loader = CSVLoader(file_path=csv_file, metadata_columns=['emotion'])
        docs = loader.load()
        if not docs:
            print(f"경고: {csv_file}에 데이터가 없습니다.")
        return docs

    @staticmethod
    def filter_new_documents(docs, existing_ids, csv_file):
        """이미 존재하는 문서를 제외하고 새 문서만 필터링."""
        new_docs = []
        for idx, doc in enumerate(docs):
            doc.metadata['source_file'] = os.path.basename(csv_file)
            unique_id = str(uuid.uuid4())
            doc_id = f"doc_{unique_id}_{idx}"
            if doc_id not in existing_ids:
                doc.metadata['doc_id'] = doc_id
                new_docs.append(doc)
        print(f"새로운 문서 발견: {len(new_docs)}개")
        return new_docs

    @staticmethod
    def split_documents(docs):
        """문서를 청크로 분할."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        splits = text_splitter.split_documents(docs)
        print(f"분할 완료: {len(splits)}개 청크")
        return splits

    @staticmethod
    def prepare_data_for_chroma(splits):
        """Chroma DB에 저장할 텍스트, 메타데이터, ID 준비."""
        texts, metadatas, ids = [], [], []
        for doc in tqdm(splits, desc="데이터 처리"):
            texts.append(f"content: {doc.page_content}")
            metadatas.append({
                "emotion": doc.metadata.get('emotion', ''),
            })
            ids.append(doc.metadata.get('doc_id'))

        if len(set(ids)) != len(ids):
            raise ValueError(f"중복된 ID 발견. 총 {len(ids)}개 중 고유 ID {len(set(ids))}개.")

        return texts, metadatas, ids

    @staticmethod
    async def create_embedding_batch(texts: List[str], embedding_function) -> List[List[float]]:
        """비동기로 배치 단위 임베딩을 생성합니다."""
        try:
            embeddings = await embedding_function.aembed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"배치 임베딩 생성 중 오류: {e}")
            return []

    @staticmethod
    async def create_embeddings_async(texts: List[str]) -> List[List[float]]:
        """텍스트 리스트의 임베딩을 비동기로 생성합니다."""
        print("임베딩 생성 시작...")
        embedding_function = OpenAIEmbeddings(
            model="text-embedding-3-small",
            chunk_size=1000
        )
        
        batch_size = 100
        all_embeddings = []
        
        # 텍스트를 배치로 나누기
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        
        # 비동기로 각 배치 처리
        async for embeddings in tqdm_asyncio.as_completed(
            [RAGProcessor.create_embedding_batch(batch, embedding_function) for batch in batches],
            total=len(batches),
            desc="임베딩 생성"
        ):
            all_embeddings.extend(embeddings)
        
        print(f"임베딩 생성 완료: {len(all_embeddings)}개")
        return all_embeddings

    @staticmethod
    def create_embeddings(texts: List[str]) -> List[List[float]]:
        """동기 방식으로 비동기 임베딩 생성을 실행합니다."""
        return asyncio.run(RAGProcessor.create_embeddings_async(texts))

    @staticmethod
    def update_chroma_db(vectorstore, texts, embeddings, metadatas, ids, db_dir):
        """Chroma DB에 데이터 추가 또는 업데이트."""
        if vectorstore is None:
            print("새로운 Chroma DB 생성...")
            vectorstore = Chroma.from_embeddings(
                embeddings=embeddings,
                texts=texts,
                embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
                persist_directory=db_dir,
                metadatas=metadatas,
                ids=ids,
                collection_name="korean_dialogue"
            )
        else:
            print("기존 DB에 문서 추가...")
            vectorstore._collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        return vectorstore

    @staticmethod
    def save_processed_file_info(csv_file):
        """처리된 파일 정보를 DB에 저장."""
        RAG_DB.objects.create(file_name=os.path.basename(csv_file), file_path=csv_file)
        print(f"파일 처리 완료 및 DB 저장: {csv_file}")

class RAGQuery:
    @staticmethod
    def create_qa_chain(db_dir):
        """QA 체인 생성."""
        vectorstore = Chroma(
            persist_directory=db_dir,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
        
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            memory=memory,
            return_source_documents=True,
            verbose=True,
            output_key="answer"
        )
