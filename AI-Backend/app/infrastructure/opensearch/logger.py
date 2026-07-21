import logging
import sys

def get_opensearch_logger(name: str = "opensearch") -> logging.Logger:
    """
    Dedicated logger for OpenSearch infrastructure.
    Ensures credentials are not logged by controlling formatting.
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

opensearch_logger = get_opensearch_logger()
