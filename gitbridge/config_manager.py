"""
Configuration manager for GitBridge.
Handles loading, saving, and managing configuration.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Class for managing GitBridge configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = Path(os.environ.get(
                'GITBRIDGE_CONFIG', 
                Path.home() / '.gitbridge' / 'config.json'
            ))
        
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration data
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in config file {self.config_path}")
                return self._get_default_config()
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {"accounts": {}}
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def add_account(self, name: str, token: str) -> bool:
        """
        Add or update an account.
        
        Args:
            name: Account name
            token: Personal access token
            
        Returns:
            True if successful, False otherwise
        """
        if 'accounts' not in self.data:
            self.data['accounts'] = {}
            
        self.data['accounts'][name] = token
        return self.save()
    
    def remove_account(self, name: str) -> bool:
        """
        Remove an account.
        
        Args:
            name: Account name
            
        Returns:
            True if successful, False otherwise
        """
        if 'accounts' in self.data and name in self.data['accounts']:
            del self.data['accounts'][name]
            return self.save()
        return False
    
    def get_account_token(self, name: str) -> Optional[str]:
        """
        Get token for an account.
        
        Args:
            name: Account name
            
        Returns:
            Token if account exists, None otherwise
        """
        return self.data.get('accounts', {}).get(name)
    
    def get_accounts(self) -> Dict[str, str]:
        """
        Get all accounts.
        
        Returns:
            Dictionary of account names and tokens
        """
        return self.data.get('accounts', {})
