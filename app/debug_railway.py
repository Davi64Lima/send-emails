#!/usr/bin/env python3
"""
Script de debug específico para Railway
Força a saída de logs para stdout/stderr
"""

import os
import sys
import logging
import time
from datetime import datetime

# Configurar logging para forçar saída
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ],
    force=True
)

logger = logging.getLogger(__name__)

def debug_environment():
    """Debug das variáveis de ambiente"""
    logger.info("=== RAILWAY DEBUG START ===")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    # Variáveis de ambiente importantes
    env_vars = [
        'DB_NAME', 'DB_USER', 'DB_PASS', 'DB_HOST', 'DB_PORT',
        'REDIS_HOST', 'REDIS_PORT', 'PORT', 'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID'
    ]
    
    logger.info("=== Environment Variables ===")
    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        logger.info(f"{var}: {value}")
    
    # Listar todas as variáveis de ambiente
    logger.info("=== All Environment Variables ===")
    for key, value in os.environ.items():
        if 'PASS' not in key.upper() and 'KEY' not in key.upper():
            logger.info(f"{key}: {value}")
    
    logger.info("=== RAILWAY DEBUG END ===")

def test_stdout_stderr():
    """Teste de saída para stdout e stderr"""
    logger.info("=== Testing stdout/stderr output ===")
    
    # Teste stdout
    print("STDOUT: This is a test message to stdout")
    print("STDOUT: Another test message")
    
    # Teste stderr
    print("STDERR: This is a test message to stderr", file=sys.stderr)
    print("STDERR: Another error message", file=sys.stderr)
    
    # Teste logging
    logger.debug("DEBUG: This is a debug message")
    logger.info("INFO: This is an info message")
    logger.warning("WARNING: This is a warning message")
    logger.error("ERROR: This is an error message")
    
    logger.info("=== stdout/stderr test completed ===")

def continuous_logging():
    """Logging contínuo para testar"""
    logger.info("=== Starting continuous logging test ===")
    
    for i in range(10):
        logger.info(f"Continuous log message #{i+1}")
        print(f"STDOUT: Continuous stdout message #{i+1}")
        time.sleep(1)
    
    logger.info("=== Continuous logging test completed ===")

if __name__ == "__main__":
    debug_environment()
    test_stdout_stderr()
    continuous_logging()
    
    # Manter o script rodando por um tempo
    logger.info("=== Debug script completed, keeping alive for 30 seconds ===")
    time.sleep(30)
    logger.info("=== Debug script finished ===") 