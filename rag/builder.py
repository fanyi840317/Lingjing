# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

from config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from .ragflow import RAGFlowRetriever
from .neo4j_retriever import Neo4jRetriever
from .retriever import Retriever


def build_retriever() -> Retriever | None:
    """构建检索器实例"""
    if SELECTED_RAG_PROVIDER == RAGProvider.RAGFLOW.value:
        return RAGFlowRetriever()
    elif SELECTED_RAG_PROVIDER == RAGProvider.NEO4J.value:
        return Neo4jRetriever()
    elif SELECTED_RAG_PROVIDER == RAGProvider.ELASTICSEARCH.value:
        # TODO: 实现Elasticsearch检索器
        raise NotImplementedError("Elasticsearch retriever not implemented yet")
    elif SELECTED_RAG_PROVIDER:
        raise ValueError(f"Unsupported RAG provider: {SELECTED_RAG_PROVIDER}")
    return None


def build_graph_retriever() -> Neo4jRetriever:
    """构建图数据库检索器"""
    return Neo4jRetriever()


def build_hybrid_retriever() -> list[Retriever]:
    """构建混合检索器，同时使用多种检索方式"""
    retrievers = []
    
    # 添加主要检索器
    main_retriever = build_retriever()
    if main_retriever:
        retrievers.append(main_retriever)
    
    # 总是添加Neo4j检索器用于关联分析
    try:
        graph_retriever = build_graph_retriever()
        if graph_retriever not in retrievers:
            retrievers.append(graph_retriever)
    except Exception:
        # Neo4j不可用时忽略
        pass
    
    return retrievers