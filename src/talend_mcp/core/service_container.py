"""Dependency injection container for all services."""

from __future__ import annotations

from talend_mcp.config.schema import TalendMcpConfig
from talend_mcp.core.safety.backup import BackupManager
from talend_mcp.core.safety.circuit_breaker import CircuitBreakerRegistry
from talend_mcp.core.safety.rollback import RollbackManager
from talend_mcp.core.safety.validator import XmlValidator
from talend_mcp.core.search.indexer import ProjectIndex
from talend_mcp.core.security.audit import AuditLog
from talend_mcp.core.security.confirmation import ConfirmationRequired
from talend_mcp.core.security.environment import EnvironmentGuard
from talend_mcp.core.security.vault import Vault
from talend_mcp.core.talend.commandline import CommandLineWrapper
from talend_mcp.core.talend.properties_parser import PropertiesParser
from talend_mcp.core.talend.tac_client import TacClient
from talend_mcp.core.talend.workspace import WorkspaceService
from talend_mcp.core.talend.xml_parser import TalendXmlParser


class ServiceContainer:
    """Central container holding all initialized services.

    Created once during server startup and passed to all tool/resource registrations.
    """

    def __init__(
        self,
        config: TalendMcpConfig,
        workspace: WorkspaceService,
        xml_parser: TalendXmlParser,
        properties_parser: PropertiesParser,
        commandline: CommandLineWrapper,
        tac: TacClient,
        vault: Vault,
        audit: AuditLog,
        env_guard: EnvironmentGuard,
        circuit_breakers: CircuitBreakerRegistry,
        backup: BackupManager,
        validator: XmlValidator,
        rollback: RollbackManager,
        index: ProjectIndex,
    ):
        self.config = config
        self.workspace = workspace
        self.xml_parser = xml_parser
        self.properties_parser = properties_parser
        self.commandline = commandline
        self.tac = tac
        self.vault = vault
        self.audit = audit
        self.env_guard = env_guard
        self.circuit_breakers = circuit_breakers
        self.backup = backup
        self.validator = validator
        self.rollback = rollback
        self.index = index

    @classmethod
    async def create(cls, config: TalendMcpConfig) -> ServiceContainer:
        """Factory method to create and wire all services."""
        vault = Vault(provider=config.security.vault_provider)

        audit = AuditLog(
            log_path=config.audit.log_path
            or (config.workspace.path / ".talend-mcp-audit.jsonl"),
        )

        env_guard = EnvironmentGuard(
            environment=config.security.environment,
            allowed_write_envs=config.security.allowed_write_envs,
            read_only=config.security.read_only,
        )

        workspace = WorkspaceService(
            workspace_path=config.workspace.path,
            default_project=config.workspace.default_project,
        )

        xml_parser = TalendXmlParser()
        properties_parser = PropertiesParser()

        commandline = CommandLineWrapper(
            studio_path=config.studio.path,
            java_home=config.studio.java_home,
        )

        tac = TacClient(
            base_url=config.tac.url,
            timeout_ms=config.tac.timeout_ms,
            vault=vault,
        )

        circuit_breakers = CircuitBreakerRegistry(
            max_failures=config.safety.circuit_breaker_max_failures,
            reset_ms=config.safety.circuit_breaker_reset_ms,
        )

        backup = BackupManager(workspace_path=config.workspace.path)
        validator = XmlValidator()
        rollback = RollbackManager(backup_manager=backup)

        index = ProjectIndex(
            workspace_path=config.workspace.path,
            project=config.workspace.default_project,
        )

        return cls(
            config=config,
            workspace=workspace,
            xml_parser=xml_parser,
            properties_parser=properties_parser,
            commandline=commandline,
            tac=tac,
            vault=vault,
            audit=audit,
            env_guard=env_guard,
            circuit_breakers=circuit_breakers,
            backup=backup,
            validator=validator,
            rollback=rollback,
            index=index,
        )

    async def close(self):
        """Clean up resources."""
        await self.tac.close()
