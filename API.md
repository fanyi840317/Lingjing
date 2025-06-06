# 神秘事件研究系统 - API文档

## 📋 目录

- [概述](#概述)
- [认证](#认证)
- [基础信息](#基础信息)
- [核心API](#核心api)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [速率限制](#速率限制)
- [示例代码](#示例代码)
- [SDK和工具](#sdk和工具)

## 🌟 概述

神秘事件研究系统提供了一套完整的RESTful API，用于执行神秘事件研究、数据分析和报告生成。API支持多种查询类型，包括文本搜索、学术研究、可信度分析和关联分析。

### 主要功能

- 🔍 **智能搜索**: 多源数据搜索和聚合
- 📊 **数据分析**: 可信度评估和关联分析
- 🤖 **AI驱动**: 基于大语言模型的智能处理
- 📈 **报告生成**: 自动化研究报告生成
- 🗄️ **数据存储**: 图数据库存储和检索

### API版本

当前版本: `v1`

基础URL: `https://api.mystery-research.com/v1`

## 🔐 认证

### API密钥认证

所有API请求都需要包含有效的API密钥。

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### 获取API密钥

1. 注册账户
2. 访问控制台
3. 生成API密钥
4. 配置权限范围

## ℹ️ 基础信息

### 系统状态

```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-01T10:00:00Z",
  "services": {
    "database": "connected",
    "ai_service": "available",
    "search_engine": "operational"
  }
}
```

### 系统信息

```http
GET /info
```

**响应示例**:
```json
{
  "name": "Mystery Event Research System",
  "version": "1.0.0",
  "description": "AI-powered mystery event research and analysis platform",
  "supported_languages": ["zh-CN", "en-US", "ja-JP"],
  "supported_event_types": [
    "UFO_SIGHTING",
    "DISAPPEARANCE",
    "PARANORMAL",
    "ANCIENT_MYSTERY",
    "CRYPTOGRAPHIC"
  ],
  "api_version": "v1",
  "documentation": "https://api.mystery-research.com/docs"
}
```

## 🔧 核心API

### 1. 研究查询

#### 执行研究查询

```http
POST /research/query
```

**请求体**:
```json
{
  "query": "研究百慕大三角的神秘失踪事件",
  "locale": "zh-CN",
  "options": {
    "max_plan_iterations": 5,
    "max_step_num": 20,
    "enable_background_investigation": true,
    "enable_academic_search": true,
    "enable_credibility_filter": true,
    "enable_correlation_analysis": true,
    "enable_graph_storage": true
  },
  "filters": {
    "event_types": ["DISAPPEARANCE", "PARANORMAL"],
    "date_range": {
      "start": "2000-01-01",
      "end": "2024-12-01"
    },
    "credibility_threshold": 0.5,
    "location": "百慕大三角"
  }
}
```

**响应示例**:
```json
{
  "query_id": "qry_1234567890abcdef",
  "status": "completed",
  "created_at": "2024-12-01T10:00:00Z",
  "completed_at": "2024-12-01T10:05:30Z",
  "results": {
    "mystery_events": [
      {
        "id": "evt_abc123",
        "title": "MH370航班失踪事件",
        "description": "马来西亚航空MH370航班在飞行途中神秘失踪",
        "event_type": "DISAPPEARANCE",
        "location": "南印度洋",
        "date": "2014-03-08",
        "source_url": "https://example.com/mh370",
        "credibility_score": 0.92,
        "metadata": {
          "witnesses": 0,
          "official_reports": 15,
          "media_coverage": "high"
        }
      }
    ],
    "academic_sources": [
      {
        "id": "src_def456",
        "title": "航空失踪事件的统计分析",
        "authors": ["Dr. Smith", "Prof. Johnson"],
        "journal": "Aviation Safety Research",
        "year": 2023,
        "url": "https://academic.example.com/aviation-analysis",
        "relevance_score": 0.88
      }
    ],
    "correlation_results": [
      {
        "event_pair": ["evt_abc123", "evt_xyz789"],
        "correlation_type": "temporal",
        "strength": 0.75,
        "description": "两个事件在时间上存在相关性"
      }
    ],
    "final_report": "# 百慕大三角神秘失踪事件研究报告\n\n## 执行摘要\n..."
  },
  "statistics": {
    "total_events_found": 15,
    "total_sources_found": 8,
    "processing_time_seconds": 330,
    "api_calls_made": 45
  }
}
```

#### 获取查询状态

```http
GET /research/query/{query_id}
```

**响应示例**:
```json
{
  "query_id": "qry_1234567890abcdef",
  "status": "processing",
  "progress": {
    "current_step": 3,
    "total_steps": 7,
    "current_operation": "执行学术搜索",
    "percentage": 42.8
  },
  "created_at": "2024-12-01T10:00:00Z",
  "estimated_completion": "2024-12-01T10:06:00Z"
}
```

#### 取消查询

```http
DELETE /research/query/{query_id}
```

### 2. 事件管理

#### 获取神秘事件列表

```http
GET /events
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `event_type`: 事件类型过滤
- `location`: 地点过滤
- `date_from`: 开始日期
- `date_to`: 结束日期
- `min_credibility`: 最小可信度
- `search`: 搜索关键词

**响应示例**:
```json
{
  "events": [
    {
      "id": "evt_abc123",
      "title": "罗斯威尔UFO事件",
      "description": "1947年在新墨西哥州罗斯威尔发生的UFO坠毁事件",
      "event_type": "UFO_SIGHTING",
      "location": "新墨西哥州罗斯威尔",
      "date": "1947-07-08",
      "credibility_score": 0.78,
      "created_at": "2024-12-01T09:00:00Z",
      "updated_at": "2024-12-01T09:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "pages": 8
  }
}
```

#### 获取单个事件详情

```http
GET /events/{event_id}
```

**响应示例**:
```json
{
  "id": "evt_abc123",
  "title": "罗斯威尔UFO事件",
  "description": "1947年在新墨西哥州罗斯威尔发生的UFO坠毁事件，引发了大量争议和猜测",
  "event_type": "UFO_SIGHTING",
  "location": "新墨西哥州罗斯威尔",
  "date": "1947-07-08",
  "source_url": "https://example.com/roswell",
  "credibility_score": 0.78,
  "metadata": {
    "witnesses": 12,
    "official_reports": 3,
    "media_coverage": "extensive",
    "government_involvement": true
  },
  "related_events": [
    {
      "id": "evt_def456",
      "title": "其他UFO目击事件",
      "correlation_strength": 0.65
    }
  ],
  "sources": [
    {
      "id": "src_ghi789",
      "title": "罗斯威尔事件官方报告",
      "type": "government_document",
      "url": "https://example.com/official-report"
    }
  ],
  "created_at": "2024-12-01T09:00:00Z",
  "updated_at": "2024-12-01T09:30:00Z"
}
```

#### 创建新事件

```http
POST /events
```

**请求体**:
```json
{
  "title": "新发现的神秘事件",
  "description": "详细描述事件的经过和特征",
  "event_type": "PARANORMAL",
  "location": "事件发生地点",
  "date": "2024-11-15",
  "source_url": "https://example.com/source",
  "metadata": {
    "witnesses": 5,
    "duration_minutes": 30,
    "weather_conditions": "clear"
  }
}
```

#### 更新事件

```http
PUT /events/{event_id}
```

#### 删除事件

```http
DELETE /events/{event_id}
```

### 3. 分析服务

#### 可信度分析

```http
POST /analysis/credibility
```

**请求体**:
```json
{
  "events": ["evt_abc123", "evt_def456"],
  "sources": ["src_ghi789"],
  "analysis_options": {
    "include_source_analysis": true,
    "include_cross_reference": true,
    "include_expert_validation": false
  }
}
```

**响应示例**:
```json
{
  "analysis_id": "ana_credibility_123",
  "results": {
    "events": [
      {
        "event_id": "evt_abc123",
        "original_score": 0.65,
        "updated_score": 0.78,
        "factors": {
          "source_reliability": 0.8,
          "witness_credibility": 0.7,
          "evidence_quality": 0.85,
          "consistency": 0.75
        },
        "explanation": "可信度提升主要由于发现了新的可靠证据"
      }
    ],
    "sources": [
      {
        "source_id": "src_ghi789",
        "credibility_score": 0.92,
        "factors": {
          "author_expertise": 0.9,
          "publication_quality": 0.95,
          "peer_review": true,
          "citation_count": 45
        }
      }
    ]
  },
  "created_at": "2024-12-01T10:15:00Z"
}
```

#### 关联分析

```http
POST /analysis/correlation
```

**请求体**:
```json
{
  "events": ["evt_abc123", "evt_def456", "evt_ghi789"],
  "analysis_types": ["temporal", "spatial", "thematic"],
  "options": {
    "min_correlation_strength": 0.3,
    "max_results": 50,
    "include_weak_correlations": false
  }
}
```

**响应示例**:
```json
{
  "analysis_id": "ana_correlation_456",
  "correlations": [
    {
      "event_pair": ["evt_abc123", "evt_def456"],
      "correlation_type": "temporal",
      "strength": 0.85,
      "description": "两个事件发生时间相近，间隔仅3天",
      "details": {
        "time_difference_days": 3,
        "seasonal_pattern": "summer_peak"
      }
    },
    {
      "event_pair": ["evt_abc123", "evt_ghi789"],
      "correlation_type": "spatial",
      "strength": 0.72,
      "description": "两个事件发生地点距离较近",
      "details": {
        "distance_km": 15.6,
        "geographic_region": "desert_area"
      }
    }
  ],
  "statistics": {
    "total_pairs_analyzed": 3,
    "significant_correlations": 2,
    "average_strength": 0.785
  },
  "created_at": "2024-12-01T10:20:00Z"
}
```

### 4. 搜索服务

#### 多源搜索

```http
POST /search/multi-source
```

**请求体**:
```json
{
  "query": "外星人目击报告",
  "sources": ["web", "academic", "news", "social_media"],
  "filters": {
    "language": "zh-CN",
    "date_range": {
      "start": "2020-01-01",
      "end": "2024-12-01"
    },
    "location": "中国",
    "content_type": ["article", "report", "video"]
  },
  "options": {
    "max_results_per_source": 20,
    "include_duplicates": false,
    "relevance_threshold": 0.6
  }
}
```

**响应示例**:
```json
{
  "search_id": "srch_789abc",
  "results": {
    "web": [
      {
        "title": "中国UFO目击事件汇总",
        "url": "https://example.com/ufo-china",
        "snippet": "近年来中国各地报告的UFO目击事件统计...",
        "relevance_score": 0.89,
        "source_type": "news_article",
        "publish_date": "2024-10-15"
      }
    ],
    "academic": [
      {
        "title": "不明飞行物现象的心理学研究",
        "authors": ["张教授", "李博士"],
        "journal": "心理学研究",
        "year": 2023,
        "doi": "10.1000/example.doi",
        "relevance_score": 0.82
      }
    ]
  },
  "statistics": {
    "total_results": 45,
    "sources_searched": 4,
    "search_time_ms": 2500,
    "duplicates_removed": 8
  },
  "created_at": "2024-12-01T10:25:00Z"
}
```

### 5. 报告生成

#### 生成研究报告

```http
POST /reports/generate
```

**请求体**:
```json
{
  "title": "百慕大三角神秘现象研究报告",
  "events": ["evt_abc123", "evt_def456"],
  "sources": ["src_ghi789", "src_jkl012"],
  "analysis_results": ["ana_credibility_123", "ana_correlation_456"],
  "template": "comprehensive",
  "options": {
    "include_executive_summary": true,
    "include_methodology": true,
    "include_data_visualization": true,
    "include_recommendations": true,
    "language": "zh-CN",
    "format": "markdown"
  }
}
```

**响应示例**:
```json
{
  "report_id": "rpt_345def",
  "status": "completed",
  "content": "# 百慕大三角神秘现象研究报告\n\n## 执行摘要\n...",
  "metadata": {
    "word_count": 2500,
    "sections": 8,
    "charts_included": 3,
    "references": 15
  },
  "download_urls": {
    "markdown": "https://api.mystery-research.com/reports/rpt_345def.md",
    "pdf": "https://api.mystery-research.com/reports/rpt_345def.pdf",
    "html": "https://api.mystery-research.com/reports/rpt_345def.html"
  },
  "created_at": "2024-12-01T10:30:00Z"
}
```

#### 获取报告列表

```http
GET /reports
```

#### 获取报告详情

```http
GET /reports/{report_id}
```

#### 下载报告

```http
GET /reports/{report_id}/download?format=pdf
```

## 📊 数据模型

### MysteryEvent

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "event_type": "enum",
  "location": "string",
  "date": "string (ISO 8601)",
  "source_url": "string (URL)",
  "credibility_score": "number (0-1)",
  "metadata": "object",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Document

```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "source_url": "string (URL)",
  "doc_type": "string",
  "metadata": "object",
  "relevance_score": "number (0-1)",
  "created_at": "string (ISO 8601)"
}
```

### CorrelationResult

```json
{
  "id": "string",
  "event_pair": ["string", "string"],
  "correlation_type": "enum",
  "strength": "number (0-1)",
  "description": "string",
  "details": "object",
  "created_at": "string (ISO 8601)"
}
```

### 枚举类型

#### EventType
```json
[
  "UFO_SIGHTING",
  "DISAPPEARANCE",
  "PARANORMAL",
  "SUPERNATURAL",
  "ANCIENT_MYSTERY",
  "ARCHAEOLOGICAL",
  "CRYPTOGRAPHIC",
  "HISTORICAL",
  "SCIENTIFIC_ANOMALY",
  "CONSPIRACY",
  "URBAN_LEGEND",
  "FOLKLORE",
  "OTHER"
]
```

#### CorrelationType
```json
[
  "temporal",
  "spatial",
  "thematic",
  "causal",
  "statistical"
]
```

## ❌ 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "query",
      "issue": "查询字符串不能为空"
    },
    "request_id": "req_123456789",
    "timestamp": "2024-12-01T10:00:00Z"
  }
}
```

### 常见错误代码

| 状态码 | 错误代码 | 描述 |
|--------|----------|------|
| 400 | INVALID_REQUEST | 请求参数无效 |
| 401 | UNAUTHORIZED | 未提供有效的API密钥 |
| 403 | FORBIDDEN | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 超出速率限制 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |
| 502 | SERVICE_UNAVAILABLE | 服务不可用 |
| 503 | MAINTENANCE | 系统维护中 |

## 🚦 速率限制

### 限制规则

| 端点类型 | 限制 | 时间窗口 |
|----------|------|----------|
| 搜索查询 | 100次 | 1小时 |
| 事件操作 | 1000次 | 1小时 |
| 分析服务 | 50次 | 1小时 |
| 报告生成 | 20次 | 1小时 |
| 其他操作 | 500次 | 1小时 |

### 响应头

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701432000
X-RateLimit-Window: 3600
```

### 超限响应

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API调用频率超出限制",
    "details": {
      "limit": 100,
      "window_seconds": 3600,
      "reset_at": "2024-12-01T11:00:00Z"
    }
  }
}
```

## 💻 示例代码

### Python

```python
import requests
import json

class MysteryResearchAPI:
    def __init__(self, api_key, base_url="https://api.mystery-research.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def research_query(self, query, locale="zh-CN", **options):
        """执行研究查询"""
        payload = {
            "query": query,
            "locale": locale,
            "options": options
        }
        
        response = self.session.post(
            f"{self.base_url}/research/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_query_status(self, query_id):
        """获取查询状态"""
        response = self.session.get(
            f"{self.base_url}/research/query/{query_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_events(self, **filters):
        """获取事件列表"""
        response = self.session.get(
            f"{self.base_url}/events",
            params=filters
        )
        response.raise_for_status()
        return response.json()
    
    def create_event(self, event_data):
        """创建新事件"""
        response = self.session.post(
            f"{self.base_url}/events",
            json=event_data
        )
        response.raise_for_status()
        return response.json()

# 使用示例
api = MysteryResearchAPI("your_api_key_here")

# 执行研究查询
result = api.research_query(
    query="研究百慕大三角的神秘现象",
    enable_academic_search=True,
    enable_correlation_analysis=True
)

print(f"查询ID: {result['query_id']}")
print(f"状态: {result['status']}")

# 获取事件列表
events = api.get_events(
    event_type="DISAPPEARANCE",
    min_credibility=0.7,
    limit=10
)

print(f"找到 {len(events['events'])} 个事件")
```

### JavaScript

```javascript
class MysteryResearchAPI {
    constructor(apiKey, baseUrl = 'https://api.mystery-research.com/v1') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API Error: ${error.error.message}`);
        }
        
        return response.json();
    }
    
    async researchQuery(query, locale = 'zh-CN', options = {}) {
        return this.request('/research/query', {
            method: 'POST',
            body: JSON.stringify({
                query,
                locale,
                options
            })
        });
    }
    
    async getQueryStatus(queryId) {
        return this.request(`/research/query/${queryId}`);
    }
    
    async getEvents(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/events?${params}`);
    }
    
    async createEvent(eventData) {
        return this.request('/events', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    }
}

// 使用示例
const api = new MysteryResearchAPI('your_api_key_here');

// 执行研究查询
api.researchQuery('研究UFO目击事件', 'zh-CN', {
    enable_academic_search: true,
    enable_correlation_analysis: true
}).then(result => {
    console.log('查询ID:', result.query_id);
    console.log('状态:', result.status);
}).catch(error => {
    console.error('查询失败:', error.message);
});
```

### cURL

```bash
# 执行研究查询
curl -X POST "https://api.mystery-research.com/v1/research/query" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "研究百慕大三角的神秘现象",
    "locale": "zh-CN",
    "options": {
      "enable_academic_search": true,
      "enable_correlation_analysis": true
    }
  }'

# 获取查询状态
curl -X GET "https://api.mystery-research.com/v1/research/query/qry_1234567890abcdef" \
  -H "Authorization: Bearer YOUR_API_KEY"

# 获取事件列表
curl -X GET "https://api.mystery-research.com/v1/events?event_type=UFO_SIGHTING&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 🛠️ SDK和工具

### 官方SDK

- **Python SDK**: `pip install mystery-research-sdk`
- **JavaScript SDK**: `npm install mystery-research-sdk`
- **Go SDK**: `go get github.com/mystery-research/go-sdk`

### 第三方工具

- **Postman Collection**: [下载链接](https://api.mystery-research.com/postman)
- **OpenAPI Specification**: [下载链接](https://api.mystery-research.com/openapi.json)
- **Swagger UI**: [在线文档](https://api.mystery-research.com/docs)

### CLI工具

```bash
# 安装CLI工具
npm install -g mystery-research-cli

# 配置API密钥
mystery-research config set-key YOUR_API_KEY

# 执行查询
mystery-research query "研究UFO事件" --locale zh-CN

# 获取事件列表
mystery-research events list --type UFO_SIGHTING
```

## 📞 支持和反馈

- **API文档**: https://api.mystery-research.com/docs
- **状态页面**: https://status.mystery-research.com
- **技术支持**: api-support@mystery-research.com
- **GitHub**: https://github.com/mystery-research/api-issues

---

*最后更新: 2024年12月*