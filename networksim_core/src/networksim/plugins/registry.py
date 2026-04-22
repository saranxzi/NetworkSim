from typing import Dict, List, Optional
from networksim.plugins.sandbox import PluginSandbox

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, PluginSandbox] = {}

    def register(self, node_type: str, source_code: str) -> None:
        """Compiles and stores the plugin code."""
        self._plugins[node_type] = PluginSandbox(source_code)

    def get_plugin(self, node_type: str) -> Optional[PluginSandbox]:
        """Returns the compiled plugin, if available."""
        return self._plugins.get(node_type)

    def has_plugin(self, node_type: str) -> bool:
        """Checks if a plugin exists for the node type."""
        return node_type in self._plugins

    def remove_plugin(self, node_type: str) -> None:
        """Removes the plugin from registry."""
        if node_type in self._plugins:
            del self._plugins[node_type]

    def list_plugins(self) -> List[str]:
        """Lists all registered node types."""
        return list(self._plugins.keys())
