# app/core/aws_toolkit.py
import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AWSToolkitDetector:
    """Detecta e gerencia credenciais do AWS Toolkit para VS Code."""
    
    def __init__(self):
        self.aws_profiles_path = Path.home() / ".aws" / "credentials"
        self.aws_config_path = Path.home() / ".aws" / "config"
        self.vscode_aws_path = self._get_vscode_aws_path()
        
        logger.debug("AWS Toolkit Detector inicializado")
    
    def _get_vscode_aws_path(self) -> Optional[Path]:
        """Tenta encontrar o path onde VS Code armazena credenciais AWS."""
        possible_paths = [
            Path.home() / ".vscode" / "aws" / "credentials",
            Path.home() / ".config" / "Code" / "User" / "aws" / "credentials",
            Path.home() / "AppData" / "Roaming" / "Code" / "User" / "aws" / "credentials",  # Windows
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def detect_credentials(self) -> bool:
        """Detecta se há credenciais AWS disponíveis via Toolkit."""
        # 1. Verifica variáveis de ambiente
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            logger.info("Credenciais AWS encontradas em variáveis de ambiente")
            return True
        
        # 2. Verifica AWS Toolkit (VS Code)
        if self.vscode_aws_path and self.vscode_aws_path.exists():
            logger.info("Credenciais AWS Toolkit (VS Code) detectadas")
            return True
        
        # 3. Verifica AWS CLI profiles
        if self.aws_profiles_path.exists():
            logger.info("Perfis AWS CLI detectados")
            return True
        
        # 4. Verifica IAM Role (EC2/EKS)
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Tenta criar um cliente sem credenciais explícitas
            sts = boto3.client('sts')
            sts.get_caller_identity()
            logger.info("Credenciais AWS detectadas via IAM Role")
            return True
        except Exception as e:
            logger.debug(f"Nenhuma credencial IAM Role detectada: {e}")
        
        logger.warning("Nenhuma credencial AWS detectada")
        return False
    
    def get_credentials(self, profile: str = "default") -> Optional[Dict]:
        """
        Obtém credenciais AWS, priorizando AWS Toolkit.
        
        Ordem de prioridade:
        1. AWS Toolkit (VS Code)
        2. Variáveis de ambiente
        3. AWS CLI profiles
        4. IAM Role metadata
        """
        creds = {}
        
        # 1. Tenta AWS Toolkit primeiro
        if self.vscode_aws_path:
            try:
                toolkit_creds = self._parse_toolkit_credentials(profile)
                if toolkit_creds:
                    logger.info(f"Usando credenciais do AWS Toolkit (profile: {profile})")
                    return toolkit_creds
            except Exception as e:
                logger.debug(f"Erro ao ler AWS Toolkit: {e}")
        
        # 2. Variáveis de ambiente
        env_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        env_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        env_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        if env_access_key and env_secret_key:
            logger.info("Usando credenciais de variáveis de ambiente")
            return {
                "access_key": env_access_key,
                "secret_key": env_secret_key,
                "region": env_region,
                "source": "environment"
            }
        
        # 3. AWS CLI profiles
        if self.aws_profiles_path.exists():
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(self.aws_profiles_path)
                
                if profile in config:
                    section = config[profile]
                    
                    # Verifica se é um profile com source_profile
                    if "source_profile" in section:
                        source_profile = section["source_profile"]
                        if source_profile in config:
                            source_section = config[source_profile]
                            creds = {
                                "access_key": source_section.get("aws_access_key_id"),
                                "secret_key": source_section.get("aws_secret_access_key"),
                                "region": self._get_region_from_config(profile),
                                "source": f"aws_cli_profile:{profile}"
                            }
                    else:
                        creds = {
                            "access_key": section.get("aws_access_key_id"),
                            "secret_key": section.get("aws_secret_access_key"),
                            "region": self._get_region_from_config(profile),
                            "source": f"aws_cli_profile:{profile}"
                        }
                    
                    if creds.get("access_key") and creds.get("secret_key"):
                        logger.info(f"Usando credenciais do AWS CLI (profile: {profile})")
                        return creds
            except Exception as e:
                logger.debug(f"Erro ao ler AWS CLI profiles: {e}")
        
        # 4. Tenta IAM Role
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Usa boto3 sem credenciais explícitas
            session = boto3.Session()
            current_creds = session.get_credentials()
            
            if current_creds:
                frozen_creds = current_creds.get_frozen_credentials()
                region = session.region_name or "us-east-1"
                
                logger.info("Usando credenciais IAM Role")
                return {
                    "access_key": frozen_creds.access_key,
                    "secret_key": frozen_creds.secret_key,
                    "token": frozen_creds.token,
                    "region": region,
                    "source": "iam_role"
                }
        except Exception as e:
            logger.debug(f"Erro ao obter IAM Role credentials: {e}")
        
        logger.warning("Não foi possível obter credenciais AWS")
        return None
    
    def _parse_toolkit_credentials(self, profile: str) -> Optional[Dict]:
        """Parse credenciais do AWS Toolkit."""
        if not self.vscode_aws_path or not self.vscode_aws_path.exists():
            return None
        
        try:
            # AWS Toolkit armazena em formato JSON
            with open(self.vscode_aws_path, 'r') as f:
                data = json.load(f)
            
            # Estrutura pode variar, tenta padrões comuns
            if "profiles" in data:
                profiles = data["profiles"]
                if profile in profiles:
                    profile_data = profiles[profile]
                    return {
                        "access_key": profile_data.get("aws_access_key_id"),
                        "secret_key": profile_data.get("aws_secret_access_key"),
                        "region": profile_data.get("region", "us-east-1"),
                        "source": "aws_toolkit"
                    }
            
            # Tenta formato alternativo
            for key, value in data.items():
                if isinstance(value, dict) and "aws_access_key_id" in value:
                    if key == profile or profile == "default":
                        return {
                            "access_key": value.get("aws_access_key_id"),
                            "secret_key": value.get("aws_secret_access_key"),
                            "region": value.get("region", "us-east-1"),
                            "source": "aws_toolkit"
                        }
        
        except json.JSONDecodeError:
            # Pode ser formato INI (como AWS CLI)
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(self.vscode_aws_path)
                
                if profile in config:
                    section = config[profile]
                    return {
                        "access_key": section.get("aws_access_key_id"),
                        "secret_key": section.get("aws_secret_access_key"),
                        "region": section.get("region", "us-east-1"),
                        "source": "aws_toolkit"
                    }
            except:
                pass
        
        return None
    
    def _get_region_from_config(self, profile: str) -> str:
        """Obtém região do arquivo de config AWS."""
        if not self.aws_config_path.exists():
            return "us-east-1"
        
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(self.aws_config_path)
            
            profile_section = f"profile {profile}" if profile != "default" else "default"
            
            if profile_section in config:
                return config[profile_section].get("region", "us-east-1")
        except:
            pass
        
        return "us-east-1"
    
    def setup_boto3_session(self, profile: str = "default"):
        """Configura sessão boto3 usando credenciais detectadas."""
        import boto3
        
        creds = self.get_credentials(profile)
        
        if not creds:
            raise ValueError("Não foi possível obter credenciais AWS")
        
        # Configura sessão boto3
        session_kwargs = {
            "region_name": creds.get("region", "us-east-1")
        }
        
        # Se tem token (para IAM Role temporária)
        if "token" in creds:
            session_kwargs.update({
                "aws_access_key_id": creds["access_key"],
                "aws_secret_access_key": creds["secret_key"],
                "aws_session_token": creds["token"]
            })
        else:
            session_kwargs.update({
                "aws_access_key_id": creds["access_key"],
                "aws_secret_access_key": creds["secret_key"]
            })
        
        logger.info(f"Configurando sessão boto3 com fonte: {creds.get('source')}")
        return boto3.Session(**session_kwargs)