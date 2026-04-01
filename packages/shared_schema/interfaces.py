from typing import Any, Dict, Iterable, Protocol


class SerializableContract(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        ...


class SharedSchemaSerializer(Protocol):
    def serialize(self, model: SerializableContract) -> Dict[str, Any]:
        ...

    def deserialize(self, schema_name: str, payload: Dict[str, Any]) -> SerializableContract:
        ...


class SharedSchemaRegistry(Protocol):
    def get_model(self, schema_name: str) -> type:
        ...

    def list_models(self) -> Iterable[str]:
        ...
