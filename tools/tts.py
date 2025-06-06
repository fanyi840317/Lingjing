# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import base64
import hashlib

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class TTSConfig:
    """TTS配置"""
    voice: str = "zh-CN-XiaoxiaoNeural"  # 默认中文女声
    rate: str = "medium"  # 语速: slow, medium, fast
    pitch: str = "medium"  # 音调: low, medium, high
    volume: str = "medium"  # 音量: low, medium, high
    format: str = "mp3"  # 输出格式: mp3, wav, ogg
    quality: str = "high"  # 音质: low, medium, high


@dataclass
class TTSResult:
    """TTS结果"""
    success: bool
    audio_file: Optional[str] = None
    audio_base64: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None


class TextToSpeechEngine(BaseTool):
    """文本转语音引擎"""
    name = "text_to_speech_engine"
    description = "Convert text to speech for mysterious event research reports."
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """初始化TTS引擎
        
        Args:
            config: TTS配置
        """
        super().__init__()
        self.config = config or TTSConfig()
        self.supported_voices = {
            "zh-CN": [
                "zh-CN-XiaoxiaoNeural",  # 女声，温和
                "zh-CN-YunxiNeural",     # 男声，成熟
                "zh-CN-YunyangNeural",   # 男声，专业
                "zh-CN-XiaochenNeural",  # 女声，活泼
                "zh-CN-XiaohanNeural",   # 女声，温暖
            ],
            "en-US": [
                "en-US-JennyNeural",     # 女声，友好
                "en-US-GuyNeural",       # 男声，专业
                "en-US-AriaNeural",      # 女声，自然
                "en-US-DavisNeural",     # 男声，权威
            ]
        }
    
    def _run(self, text: str, output_path: str = None, config_override: Dict[str, Any] = None) -> str:
        """执行文本转语音
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
            config_override: 配置覆盖
            
        Returns:
            TTS结果JSON
        """
        try:
            # 应用配置覆盖
            effective_config = self._apply_config_override(config_override)
            
            # 预处理文本
            processed_text = self._preprocess_text(text)
            
            # 生成音频
            result = self._generate_audio(processed_text, output_path, effective_config)
            
            return json.dumps(result.__dict__, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to convert text to speech. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _apply_config_override(self, config_override: Dict[str, Any] = None) -> TTSConfig:
        """应用配置覆盖"""
        if not config_override:
            return self.config
        
        # 创建新的配置对象
        new_config = TTSConfig(
            voice=config_override.get("voice", self.config.voice),
            rate=config_override.get("rate", self.config.rate),
            pitch=config_override.get("pitch", self.config.pitch),
            volume=config_override.get("volume", self.config.volume),
            format=config_override.get("format", self.config.format),
            quality=config_override.get("quality", self.config.quality)
        )
        
        return new_config
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除过长的空白
        text = " ".join(text.split())
        
        # 处理特殊字符和缩写
        replacements = {
            "UFO": "不明飞行物",
            "GPS": "全球定位系统",
            "AI": "人工智能",
            "API": "应用程序接口",
            "URL": "网址",
            "HTTP": "超文本传输协议",
            "JSON": "杰森格式",
            "PDF": "便携式文档格式",
            "&": "和",
            "@": "at",
            "#": "井号",
            "%": "百分之",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 处理数字
        text = self._convert_numbers_to_chinese(text)
        
        # 添加适当的停顿
        text = text.replace("。", "。<break time='500ms'/>")
        text = text.replace("！", "！<break time='500ms'/>")
        text = text.replace("？", "？<break time='500ms'/>")
        text = text.replace("；", "；<break time='300ms'/>")
        text = text.replace("，", "，<break time='200ms'/>")
        
        return text
    
    def _convert_numbers_to_chinese(self, text: str) -> str:
        """将数字转换为中文读音"""
        # 简单的数字转换，实际应用中可能需要更复杂的逻辑
        chinese_numbers = {
            "0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
            "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"
        }
        
        # 这里只做简单替换，实际应用中需要处理更复杂的数字
        import re
        
        def replace_single_digit(match):
            digit = match.group(0)
            return chinese_numbers.get(digit, digit)
        
        # 替换单独的数字
        text = re.sub(r'\b\d\b', replace_single_digit, text)
        
        return text
    
    def _generate_audio(self, text: str, output_path: str, config: TTSConfig) -> TTSResult:
        """生成音频文件"""
        try:
            # 在真实实现中，这里会调用实际的TTS服务
            # 例如：Azure Cognitive Services, Google Cloud TTS, Amazon Polly等
            
            # 模拟音频生成
            audio_content = self._mock_audio_generation(text, config)
            
            # 计算文件大小和时长
            file_size = len(audio_content)
            duration = self._estimate_duration(text)
            
            if output_path:
                # 保存到文件
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(audio_content)
                
                return TTSResult(
                    success=True,
                    audio_file=output_path,
                    duration_seconds=duration,
                    file_size_bytes=file_size
                )
            else:
                # 返回base64编码
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                
                return TTSResult(
                    success=True,
                    audio_base64=audio_base64,
                    duration_seconds=duration,
                    file_size_bytes=file_size
                )
                
        except Exception as e:
            return TTSResult(
                success=False,
                error_message=str(e)
            )
    
    def _mock_audio_generation(self, text: str, config: TTSConfig) -> bytes:
        """模拟音频生成"""
        # 在真实实现中，这里会调用实际的TTS API
        # 这里只是生成一个模拟的音频内容
        
        # 创建一个基于文本内容的伪音频数据
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # 模拟不同格式的音频头
        if config.format == "mp3":
            header = b'\xff\xfb\x90\x00'  # MP3 header
        elif config.format == "wav":
            header = b'RIFF\x00\x00\x00\x00WAVEfmt '  # WAV header
        else:
            header = b'OggS\x00\x02\x00\x00'  # OGG header
        
        # 生成伪音频数据
        audio_data = header + (text_hash * 100).encode('utf-8')[:8192]
        
        return audio_data
    
    def _estimate_duration(self, text: str) -> float:
        """估算音频时长"""
        # 简单估算：中文约每分钟200字，英文约每分钟150词
        char_count = len(text)
        
        # 假设平均语速
        chars_per_minute = 200
        duration_minutes = char_count / chars_per_minute
        
        return duration_minutes * 60  # 转换为秒
    
    def get_available_voices(self, language: str = "zh-CN") -> List[str]:
        """获取可用的语音"""
        return self.supported_voices.get(language, [])


class ReportNarrator:
    """报告朗读器"""
    
    def __init__(self, tts_engine: TextToSpeechEngine = None):
        """初始化报告朗读器
        
        Args:
            tts_engine: TTS引擎实例
        """
        self.tts_engine = tts_engine or TextToSpeechEngine()
    
    def narrate_report_section(self, section_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """朗读报告章节
        
        Args:
            section_data: 章节数据
            output_dir: 输出目录
            
        Returns:
            朗读结果
        """
        try:
            section_title = section_data.get("title", "未知章节")
            section_content = section_data.get("content", "")
            
            # 构建朗读文本
            narration_text = f"{section_title}。{section_content}"
            
            # 生成音频文件名
            safe_title = self._sanitize_filename(section_title)
            audio_filename = f"{safe_title}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            # 转换为语音
            result_json = self.tts_engine._run(narration_text, audio_path)
            result = json.loads(result_json)
            
            if "error" not in result:
                return {
                    "section_title": section_title,
                    "audio_file": audio_path,
                    "status": "success",
                    "duration": result.get("duration_seconds", 0),
                    "file_size": result.get("file_size_bytes", 0)
                }
            else:
                return {
                    "section_title": section_title,
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "section_title": section_data.get("title", "未知章节"),
                "status": "error",
                "error": str(e)
            }
    
    def narrate_full_report(self, report_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """朗读完整报告
        
        Args:
            report_data: 报告数据
            output_dir: 输出目录
            
        Returns:
            朗读结果
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            total_duration = 0
            total_size = 0
            
            # 朗读各个章节
            sections = [
                {"title": "执行摘要", "content": report_data.get("summary", "")},
                {"title": "关键发现", "content": "。".join(report_data.get("key_findings", []))},
                {"title": "事件概览", "content": self._format_overview(report_data.get("events_overview", {}))},
                {"title": "详细分析", "content": self._format_analysis(report_data.get("analysis", {}))},
                {"title": "结论", "content": "。".join(report_data.get("conclusions", []))},
                {"title": "建议", "content": "。".join(report_data.get("recommendations", []))}
            ]
            
            for section in sections:
                if section["content"].strip():
                    result = self.narrate_report_section(section, output_dir)
                    results.append(result)
                    
                    if result["status"] == "success":
                        total_duration += result.get("duration", 0)
                        total_size += result.get("file_size", 0)
            
            return {
                "status": "success",
                "output_directory": output_dir,
                "sections_narrated": len(results),
                "total_duration_seconds": total_duration,
                "total_file_size_bytes": total_size,
                "section_results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        # 移除或替换不安全的字符
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_name = safe_name.strip('. ')
        return safe_name[:50]  # 限制长度
    
    def _format_overview(self, overview: Dict[str, Any]) -> str:
        """格式化概览内容"""
        parts = []
        
        if "total_events" in overview:
            parts.append(f"总共分析了{overview['total_events']}起事件")
        
        if "time_range" in overview:
            parts.append(f"时间范围为{overview['time_range']}")
        
        if "regions" in overview:
            parts.append(f"涉及地区包括{overview['regions']}")
        
        if "main_types" in overview:
            parts.append(f"主要事件类型为{overview['main_types']}")
        
        return "。".join(parts)
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """格式化分析内容"""
        parts = []
        
        # 时间线分析
        if "timeline" in analysis:
            timeline = analysis["timeline"]
            if "trends" in timeline:
                trend = timeline["trends"].get("overall_trend", "稳定")
                parts.append(f"时间趋势分析显示事件发生呈{trend}态势")
        
        # 地理分析
        if "location" in analysis:
            location = analysis["location"]
            if "clusters" in location:
                cluster_count = len(location["clusters"])
                parts.append(f"地理分析发现{cluster_count}个主要聚集区域")
        
        # 可信度分析
        if "credibility" in analysis:
            credibility = analysis["credibility"]
            avg_score = credibility.get("average_score", 0)
            parts.append(f"平均可信度评分为{avg_score:.1f}分")
        
        # 关联分析
        if "correlation" in analysis:
            correlation = analysis["correlation"]
            if "strong_correlations" in correlation:
                corr_count = len(correlation["strong_correlations"])
                parts.append(f"发现{corr_count}组强关联事件")
        
        return "。".join(parts)


@tool
@log_io
def convert_text_to_speech(
    text: str,
    output_path: Optional[str] = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "medium",
    format: str = "mp3"
) -> str:
    """将文本转换为语音
    
    Args:
        text: 要转换的文本
        output_path: 输出音频文件路径
        voice: 语音类型
        rate: 语速 (slow, medium, fast)
        format: 音频格式 (mp3, wav, ogg)
    
    Returns:
        转换结果JSON
    """
    try:
        config_override = {
            "voice": voice,
            "rate": rate,
            "format": format
        }
        
        tts_engine = TextToSpeechEngine()
        return tts_engine._run(text, output_path, config_override)
        
    except Exception as e:
        error_msg = f"Failed to convert text to speech. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def narrate_mystery_report(
    report_data: str,
    output_directory: str
) -> str:
    """朗读神秘事件研究报告
    
    Args:
        report_data: JSON格式的报告数据
        output_directory: 输出目录
    
    Returns:
        朗读结果JSON
    """
    try:
        data = json.loads(report_data)
        narrator = ReportNarrator()
        result = narrator.narrate_full_report(data, output_directory)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to narrate mystery report. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def get_available_tts_voices(
    language: str = "zh-CN"
) -> str:
    """获取可用的TTS语音列表
    
    Args:
        language: 语言代码 (zh-CN, en-US)
    
    Returns:
        可用语音列表JSON
    """
    try:
        tts_engine = TextToSpeechEngine()
        voices = tts_engine.get_available_voices(language)
        
        return json.dumps({
            "language": language,
            "voices": voices,
            "count": len(voices)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to get available TTS voices. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def create_audio_summary(
    key_findings: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    output_path: Optional[str] = None
) -> str:
    """创建关键发现的音频摘要
    
    Args:
        key_findings: JSON格式的关键发现列表
        voice: 语音类型
        output_path: 输出音频文件路径
    
    Returns:
        音频摘要结果JSON
    """
    try:
        findings = json.loads(key_findings)
        
        # 构建摘要文本
        if isinstance(findings, list):
            summary_text = "神秘事件研究关键发现摘要。" + "。".join(findings)
        else:
            summary_text = "神秘事件研究关键发现摘要。" + str(findings)
        
        # 转换为语音
        config_override = {"voice": voice}
        tts_engine = TextToSpeechEngine()
        result = tts_engine._run(summary_text, output_path, config_override)
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to create audio summary. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)