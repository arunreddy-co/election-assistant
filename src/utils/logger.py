"""Structured JSON logging utility for the VoteReady application."""

import os
import json
import logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """Formatter to output logs in structured JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage()
        }
        
        # Avoid logging sensitive information
        if hasattr(record, "voter_id"):
            log_data["voter_id"] = "***REDACTED***"
            
        return json.dumps(log_data)

def get_logger(module_name: str) -> logging.Logger:
    """Get a configured logger with structured JSON formatting.
    
    Args:
        module_name: Name of the module requesting the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(module_name)
    
    # Avoid adding duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
        # Read log level from environment
        env = os.getenv("ENV", "development")
        log_level = logging.DEBUG if env == "development" else logging.INFO
        logger.setLevel(log_level)
        
        # Prevent log messages from propagating to the root logger
        logger.propagate = False
        
    return logger
