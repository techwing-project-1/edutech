from typing import Optional, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3

from app.infrastructure.opensearch.logger import opensearch_logger
from app.infrastructure.opensearch.exceptions import (
    ConfigurationError,
    OpenSearchConnectionError,
    AuthenticationError,
    ClusterUnavailable
)
from app.infrastructure.opensearch.config import opensearch_settings

# Disable warnings for unverified HTTPS requests if we ever need self-signed certs (not recommended for prod)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OpenSearchClientManager:
    """
    Singleton manager for the OpenSearch connection.
    Handles HTTPS connection, HTTP Basic Authentication, retry logic, and connection pooling.
    """
    _instance: Optional['OpenSearchClientManager'] = None
    _client: Optional[OpenSearch] = None

    def __new__(cls) -> 'OpenSearchClientManager':
        if cls._instance is None:
            cls._instance = super(OpenSearchClientManager, cls).__new__(cls)
        return cls._instance

    def get_client(self) -> OpenSearch:
        """Returns the active OpenSearch client, initializing it if necessary."""
        if self._client is None:
            self._initialize_client()
        return self._client

    def _initialize_client(self) -> None:
        """Initializes the OpenSearch client with configuration."""
        if not opensearch_settings:
            raise ConfigurationError("Cannot initialize OpenSearch client: configuration is missing.")
            
        endpoint = opensearch_settings.OPENSEARCH_ENDPOINT
        username = opensearch_settings.OPENSEARCH_USERNAME
        password = opensearch_settings.OPENSEARCH_PASSWORD
        
        # Remove https:// from endpoint if present since OpenSearch client handles it via use_ssl
        if endpoint.startswith("https://"):
            endpoint = endpoint[8:]
        elif endpoint.startswith("http://"):
            endpoint = endpoint[7:]

        try:
            opensearch_logger.info("Initializing OpenSearch client (HTTPS enabled, Basic Auth)...")
            self._client = OpenSearch(
                hosts=[{'host': endpoint, 'port': 443}],
                http_auth=(username, password),
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=opensearch_settings.OPENSEARCH_TIMEOUT,
                max_retries=opensearch_settings.OPENSEARCH_MAX_RETRIES,
                retry_on_timeout=True
            )
            opensearch_logger.info("OpenSearch client initialized successfully.")
        except Exception as e:
            opensearch_logger.error(f"Failed to initialize OpenSearch client: {str(e)}")
            raise OpenSearchConnectionError(f"Failed to initialize OpenSearch client: {str(e)}")

    def check_connection(self) -> Dict[str, Any]:
        """
        Verifies cluster reachability, authentication, and health status.
        Returns a structured dictionary of cluster info, or raises an exception.
        """
        client = self.get_client()
        
        try:
            # Check cluster info (tests authentication and basic reachability)
            info = client.info()
            version = info.get("version", {}).get("number", "unknown")
            cluster_name = info.get("cluster_name", "unknown")
            
            # Check cluster health
            health = client.cluster.health()
            status = health.get("status", "unknown")
            
            opensearch_logger.info(f"OpenSearch Connection Verified. Cluster: '{cluster_name}', Version: '{version}', Health: '{status}'")
            
            if status == "red":
                opensearch_logger.warning("OpenSearch cluster status is RED. It may be unavailable for writes.")
                
            return {
                "connected": True,
                "cluster_name": cluster_name,
                "version": version,
                "status": status,
                "number_of_nodes": health.get("number_of_nodes", 0)
            }
            
        except Exception as e:
            error_msg = str(e)
            opensearch_logger.error(f"OpenSearch health check failed: {error_msg}")
            
            if "401" in error_msg or "403" in error_msg or "Unauthorized" in error_msg:
                raise AuthenticationError(f"OpenSearch authentication failed: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise OpenSearchConnectionError(f"OpenSearch connection timed out: {error_msg}")
            else:
                raise ClusterUnavailable(f"OpenSearch cluster is unavailable: {error_msg}")

# Global singleton instance
opensearch_manager = OpenSearchClientManager()
