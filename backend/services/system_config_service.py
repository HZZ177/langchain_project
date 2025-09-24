"""
系统配置管理服务
"""
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.data.models.system_config import SystemConfig
from backend.core.logger import logger


class SystemConfigService:
    """系统配置管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_config(self, key: str, default_value: Any = None) -> Any:
        """获取单个配置项"""
        config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if not config:
            return default_value
        
        try:
            return json.loads(config.value) if config.value else default_value
        except json.JSONDecodeError:
            logger.error(f"配置项 {key} 的值不是有效的JSON格式: {config.value}")
            return default_value
    
    def set_config(self, key: str, value: Any, description: str = None) -> bool:
        """设置单个配置项"""
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            
            config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if config:
                # 更新现有配置
                config.value = json_value
                if description:
                    config.description = description
            else:
                # 创建新配置
                config = SystemConfig(
                    key=key,
                    value=json_value,
                    description=description
                )
                self.db.add(config)
            
            self.db.commit()
            logger.info(f"系统配置已更新: {key}")
            return True
            
        except Exception as e:
            logger.error(f"设置配置项 {key} 失败: {e}")
            self.db.rollback()
            return False
    
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置项"""
        configs = {}
        db_configs = self.db.query(SystemConfig).all()
        
        for config in db_configs:
            try:
                configs[config.key] = json.loads(config.value) if config.value else None
            except json.JSONDecodeError:
                logger.error(f"配置项 {config.key} 的值不是有效的JSON格式: {config.value}")
                configs[config.key] = None
        
        return configs
    
    def update_configs(self, configs: Dict[str, Any]) -> bool:
        """批量更新配置项"""
        try:
            for key, value in configs.items():
                self.set_config(key, value)
            return True
        except Exception as e:
            logger.error(f"批量更新配置失败: {e}")
            return False
    
    def get_title_generation_config(self) -> Dict[str, Any]:
        """获取标题生成配置"""
        default_config = {
            "enabled": True,
            "model": "gemini-2.5-flash-preview-05-20",
            "api_key": "sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2",
            "base_url": "https://x666.me/v1",
            "temperature": 0.3,
            "max_tokens": None,
            "trigger_rounds": 2
        }

        return self.get_config("title_generation", default_config)
    
    def update_title_generation_config(self, config: Dict[str, Any]) -> bool:
        """更新标题生成配置"""
        return self.set_config(
            "title_generation", 
            config, 
            "会话标题自动生成功能配置"
        )
    
    def delete_config(self, key: str) -> bool:
        """删除配置项"""
        try:
            config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if config:
                self.db.delete(config)
                self.db.commit()
                logger.info(f"配置项已删除: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除配置项 {key} 失败: {e}")
            self.db.rollback()
            return False
    
    def init_default_configs(self):
        """初始化默认配置"""
        # 检查是否已存在标题生成配置
        if not self.db.query(SystemConfig).filter(SystemConfig.key == "title_generation").first():
            default_title_config = {
                "enabled": True,
                "model": "gemini-2.5-flash-preview-05-20",
                "api_key": "sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2",
                "base_url": "https://x666.me/v1",
                "temperature": 0.3,
                "max_tokens": None,
                "trigger_rounds": 2
            }
            
            self.set_config(
                "title_generation",
                default_title_config,
                "会话标题自动生成功能配置"
            )
            logger.info("已初始化默认标题生成配置")


def get_system_config_service(db: Session) -> SystemConfigService:
    """获取系统配置服务实例"""
    return SystemConfigService(db)
