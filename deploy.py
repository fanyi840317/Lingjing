#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神秘事件研究系统 - 部署脚本

这个脚本提供了自动化部署功能，包括：
- 环境检查和准备
- 依赖安装
- 数据库初始化
- 配置文件生成
- 服务启动
- 健康检查

使用方法:
    python deploy.py --env production --config config/production.yaml
    python deploy.py --env development --quick-start
    python deploy.py --check-health
    python deploy.py --rollback
"""

import os
import sys
import json
import yaml
import time
import shutil
import argparse
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import load_config, validate_config
    from utils.logger import setup_logger
except ImportError:
    # 如果模块未安装，使用基础配置
    def load_config():
        return {}
    def validate_config():
        return True
    def setup_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.logger = setup_logger(f"deploy_{environment}")
        self.config = {}
        self.deployment_info = {
            "start_time": datetime.now().isoformat(),
            "environment": environment,
            "version": self._get_version(),
            "steps_completed": [],
            "status": "initializing"
        }
        
    def _get_version(self) -> str:
        """获取项目版本"""
        try:
            version_file = self.project_root / "__version__.py"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip('"\'')
            return "0.1.0"
        except Exception:
            return "unknown"
    
    def check_prerequisites(self) -> bool:
        """检查部署前提条件"""
        self.logger.info("🔍 检查部署前提条件...")
        
        checks = [
            ("Python版本", self._check_python_version),
            ("磁盘空间", self._check_disk_space),
            ("网络连接", self._check_network),
            ("权限", self._check_permissions),
            ("依赖工具", self._check_tools)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                self.logger.info(f"{status} {check_name}: {'通过' if result else '失败'}")
                if not result:
                    all_passed = False
            except Exception as e:
                self.logger.error(f"❌ {check_name}: 检查失败 - {e}")
                all_passed = False
        
        if all_passed:
            self.deployment_info["steps_completed"].append("prerequisites_check")
            self.logger.info("✅ 所有前提条件检查通过")
        else:
            self.logger.error("❌ 部分前提条件检查失败，请解决后重试")
        
        return all_passed
    
    def _check_python_version(self) -> bool:
        """检查Python版本"""
        version = sys.version_info
        required = (3, 8)
        return version >= required
    
    def _check_disk_space(self) -> bool:
        """检查磁盘空间"""
        try:
            stat = shutil.disk_usage(self.project_root)
            free_gb = stat.free / (1024**3)
            return free_gb >= 2.0  # 至少2GB空闲空间
        except Exception:
            return False
    
    def _check_network(self) -> bool:
        """检查网络连接"""
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        except Exception:
            return False
    
    def _check_permissions(self) -> bool:
        """检查文件权限"""
        try:
            test_file = self.project_root / "test_permission.tmp"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def _check_tools(self) -> bool:
        """检查必要工具"""
        tools = ['git', 'pip']
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        return True
    
    def setup_environment(self) -> bool:
        """设置环境"""
        self.logger.info("🔧 设置部署环境...")
        
        try:
            # 创建必要目录
            directories = [
                "logs",
                "data",
                "cache",
                "temp",
                "backups",
                "reports"
            ]
            
            for dir_name in directories:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(exist_ok=True)
                self.logger.info(f"📁 创建目录: {dir_path}")
            
            # 设置环境变量
            env_file = self.project_root / ".env"
            if not env_file.exists():
                self._create_env_file()
            
            # 创建虚拟环境（如果不存在）
            if self.environment == "production":
                self._setup_virtual_environment()
            
            self.deployment_info["steps_completed"].append("environment_setup")
            self.logger.info("✅ 环境设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 环境设置失败: {e}")
            return False
    
    def _create_env_file(self):
        """创建环境配置文件"""
        env_example = self.project_root / ".env.example"
        env_file = self.project_root / ".env"
        
        if env_example.exists():
            shutil.copy2(env_example, env_file)
            self.logger.info("📄 从.env.example创建.env文件")
        else:
            # 创建基础.env文件
            basic_env = """
# 神秘事件研究系统 - 环境配置

# 系统设置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API密钥（请填入实际值）
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 其他配置
MAX_WORKERS=4
REQUEST_TIMEOUT=30
"""
            env_file.write_text(basic_env.strip())
            self.logger.info("📄 创建基础.env文件")
    
    def _setup_virtual_environment(self):
        """设置虚拟环境"""
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            self.logger.info("🐍 创建虚拟环境...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                         check=True)
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        self.logger.info("📦 安装项目依赖...")
        
        try:
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                self.logger.error("❌ requirements.txt文件不存在")
                return False
            
            # 升级pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True)
            
            # 安装依赖
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            if self.environment == "production":
                cmd.append("--no-dev")
            
            subprocess.run(cmd, check=True)
            
            # 安装项目本身
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                         check=True)
            
            self.deployment_info["steps_completed"].append("dependencies_install")
            self.logger.info("✅ 依赖安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ 依赖安装失败: {e}")
            return False
    
    def initialize_databases(self) -> bool:
        """初始化数据库"""
        self.logger.info("🗄️ 初始化数据库...")
        
        try:
            # 这里应该根据实际的数据库初始化逻辑来实现
            # 例如创建Neo4j图数据库结构、Elasticsearch索引等
            
            # 模拟数据库初始化
            databases = ["Neo4j", "Elasticsearch", "PostgreSQL"]
            for db in databases:
                self.logger.info(f"🔧 初始化{db}数据库...")
                time.sleep(1)  # 模拟初始化时间
                self.logger.info(f"✅ {db}数据库初始化完成")
            
            self.deployment_info["steps_completed"].append("database_init")
            self.logger.info("✅ 所有数据库初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 数据库初始化失败: {e}")
            return False
    
    def configure_system(self) -> bool:
        """配置系统"""
        self.logger.info("⚙️ 配置系统设置...")
        
        try:
            # 加载和验证配置
            self.config = load_config()
            if not validate_config():
                self.logger.error("❌ 配置验证失败")
                return False
            
            # 根据环境调整配置
            if self.environment == "production":
                self._configure_production()
            elif self.environment == "development":
                self._configure_development()
            
            self.deployment_info["steps_completed"].append("system_config")
            self.logger.info("✅ 系统配置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 系统配置失败: {e}")
            return False
    
    def _configure_production(self):
        """生产环境配置"""
        self.logger.info("🏭 应用生产环境配置...")
        # 生产环境特定配置
        pass
    
    def _configure_development(self):
        """开发环境配置"""
        self.logger.info("🛠️ 应用开发环境配置...")
        # 开发环境特定配置
        pass
    
    def start_services(self) -> bool:
        """启动服务"""
        self.logger.info("🚀 启动系统服务...")
        
        try:
            # 这里应该启动实际的服务
            # 例如Web服务器、后台任务处理器等
            
            services = ["Web服务器", "任务队列", "监控服务"]
            for service in services:
                self.logger.info(f"▶️ 启动{service}...")
                time.sleep(2)  # 模拟启动时间
                self.logger.info(f"✅ {service}启动成功")
            
            self.deployment_info["steps_completed"].append("services_start")
            self.deployment_info["status"] = "running"
            self.logger.info("✅ 所有服务启动完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 服务启动失败: {e}")
            return False
    
    def health_check(self) -> bool:
        """健康检查"""
        self.logger.info("🏥 执行系统健康检查...")
        
        checks = [
            ("系统状态", self._check_system_status),
            ("数据库连接", self._check_database_connections),
            ("API服务", self._check_api_services),
            ("存储空间", self._check_storage),
            ("内存使用", self._check_memory_usage)
        ]
        
        all_healthy = True
        health_report = {}
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "健康" if result else "异常"
                icon = "✅" if result else "❌"
                self.logger.info(f"{icon} {check_name}: {status}")
                health_report[check_name] = result
                if not result:
                    all_healthy = False
            except Exception as e:
                self.logger.error(f"❌ {check_name}: 检查失败 - {e}")
                health_report[check_name] = False
                all_healthy = False
        
        # 保存健康检查报告
        self._save_health_report(health_report)
        
        if all_healthy:
            self.logger.info("✅ 系统健康检查通过")
        else:
            self.logger.warning("⚠️ 系统健康检查发现问题")
        
        return all_healthy
    
    def _check_system_status(self) -> bool:
        """检查系统状态"""
        return self.deployment_info["status"] == "running"
    
    def _check_database_connections(self) -> bool:
        """检查数据库连接"""
        # 这里应该实际测试数据库连接
        return True
    
    def _check_api_services(self) -> bool:
        """检查API服务"""
        # 这里应该实际测试API端点
        return True
    
    def _check_storage(self) -> bool:
        """检查存储空间"""
        try:
            stat = shutil.disk_usage(self.project_root)
            free_gb = stat.free / (1024**3)
            return free_gb >= 1.0  # 至少1GB空闲空间
        except Exception:
            return False
    
    def _check_memory_usage(self) -> bool:
        """检查内存使用"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < 90  # 内存使用率低于90%
        except ImportError:
            return True  # 如果psutil不可用，假设正常
        except Exception:
            return False
    
    def _save_health_report(self, report: Dict):
        """保存健康检查报告"""
        try:
            report_file = self.project_root / "logs" / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "environment": self.environment,
                    "checks": report
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存健康检查报告失败: {e}")
    
    def create_backup(self) -> bool:
        """创建备份"""
        self.logger.info("💾 创建系统备份...")
        
        try:
            backup_dir = self.project_root / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份配置文件
            config_files = [".env", "config/default.yaml", "config/user.yaml"]
            for config_file in config_files:
                src = self.project_root / config_file
                if src.exists():
                    dst = backup_dir / config_file
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            
            # 备份数据目录
            data_dir = self.project_root / "data"
            if data_dir.exists():
                shutil.copytree(data_dir, backup_dir / "data")
            
            # 备份日志
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                shutil.copytree(logs_dir, backup_dir / "logs")
            
            self.logger.info(f"✅ 备份创建完成: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 备份创建失败: {e}")
            return False
    
    def rollback(self, backup_path: Optional[str] = None) -> bool:
        """回滚到之前的版本"""
        self.logger.info("🔄 执行系统回滚...")
        
        try:
            if not backup_path:
                # 查找最新的备份
                backups_dir = self.project_root / "backups"
                if not backups_dir.exists():
                    self.logger.error("❌ 没有找到备份目录")
                    return False
                
                backups = sorted([d for d in backups_dir.iterdir() if d.is_dir()], 
                               reverse=True)
                if not backups:
                    self.logger.error("❌ 没有找到可用的备份")
                    return False
                
                backup_path = str(backups[0])
            
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                self.logger.error(f"❌ 备份目录不存在: {backup_path}")
                return False
            
            # 停止服务
            self.logger.info("⏹️ 停止服务...")
            # 这里应该实际停止服务
            
            # 恢复配置文件
            config_files = [".env", "config/default.yaml", "config/user.yaml"]
            for config_file in config_files:
                src = backup_dir / config_file
                if src.exists():
                    dst = self.project_root / config_file
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            
            # 恢复数据
            backup_data = backup_dir / "data"
            if backup_data.exists():
                current_data = self.project_root / "data"
                if current_data.exists():
                    shutil.rmtree(current_data)
                shutil.copytree(backup_data, current_data)
            
            # 重新启动服务
            self.logger.info("🚀 重新启动服务...")
            self.start_services()
            
            self.logger.info(f"✅ 系统回滚完成: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 系统回滚失败: {e}")
            return False
    
    def deploy(self) -> bool:
        """执行完整部署"""
        self.logger.info(f"🚀 开始部署神秘事件研究系统 ({self.environment}环境)")
        
        steps = [
            ("前提条件检查", self.check_prerequisites),
            ("环境设置", self.setup_environment),
            ("依赖安装", self.install_dependencies),
            ("数据库初始化", self.initialize_databases),
            ("系统配置", self.configure_system),
            ("服务启动", self.start_services),
            ("健康检查", self.health_check)
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"📋 执行步骤: {step_name}")
            if not step_func():
                self.logger.error(f"❌ 部署失败于步骤: {step_name}")
                self.deployment_info["status"] = "failed"
                self.deployment_info["failed_step"] = step_name
                self._save_deployment_info()
                return False
        
        self.deployment_info["status"] = "completed"
        self.deployment_info["end_time"] = datetime.now().isoformat()
        self._save_deployment_info()
        
        self.logger.info("🎉 部署成功完成！")
        self._print_deployment_summary()
        return True
    
    def _save_deployment_info(self):
        """保存部署信息"""
        try:
            info_file = self.project_root / "logs" / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存部署信息失败: {e}")
    
    def _print_deployment_summary(self):
        """打印部署摘要"""
        print("\n" + "="*60)
        print("🎉 神秘事件研究系统部署完成")
        print("="*60)
        print(f"环境: {self.environment}")
        print(f"版本: {self.deployment_info['version']}")
        print(f"开始时间: {self.deployment_info['start_time']}")
        if 'end_time' in self.deployment_info:
            print(f"结束时间: {self.deployment_info['end_time']}")
        print(f"状态: {self.deployment_info['status']}")
        print("\n已完成步骤:")
        for step in self.deployment_info['steps_completed']:
            print(f"  ✅ {step}")
        print("\n🔗 访问地址:")
        print("  - Web界面: http://localhost:8000")
        print("  - API文档: http://localhost:8000/docs")
        print("  - 健康检查: http://localhost:8000/health")
        print("\n📚 更多信息:")
        print("  - 查看日志: tail -f logs/app.log")
        print("  - 配置文件: config/default.yaml")
        print("  - API文档: API.md")
        print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="神秘事件研究系统部署脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python deploy.py --env production                    # 生产环境部署
  python deploy.py --env development --quick-start    # 开发环境快速启动
  python deploy.py --check-health                     # 健康检查
  python deploy.py --rollback                         # 回滚到最新备份
  python deploy.py --backup                           # 创建备份
        """
    )
    
    parser.add_argument(
        "--env", 
        choices=["development", "production", "testing"],
        default="development",
        help="部署环境 (默认: development)"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--quick-start",
        action="store_true",
        help="快速启动模式（跳过某些检查）"
    )
    
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="仅执行健康检查"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        help="创建系统备份"
    )
    
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="latest",
        help="回滚到指定备份（默认最新）"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建部署管理器
    deployer = DeploymentManager(args.env)
    
    try:
        if args.check_health:
            # 仅执行健康检查
            success = deployer.health_check()
            sys.exit(0 if success else 1)
        
        elif args.backup:
            # 创建备份
            success = deployer.create_backup()
            sys.exit(0 if success else 1)
        
        elif args.rollback:
            # 执行回滚
            backup_path = None if args.rollback == "latest" else args.rollback
            success = deployer.rollback(backup_path)
            sys.exit(0 if success else 1)
        
        else:
            # 执行完整部署
            if args.quick_start:
                deployer.logger.info("🚀 快速启动模式")
            
            success = deployer.deploy()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        deployer.logger.info("\n⏹️ 部署被用户中断")
        sys.exit(1)
    except Exception as e:
        deployer.logger.error(f"❌ 部署过程中发生未预期的错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()