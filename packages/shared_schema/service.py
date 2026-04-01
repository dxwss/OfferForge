from typing import Any, Dict, Iterable

from .schema import SCHEMA_REGISTRY, SchemaModel


class SharedSchemaService:
    def get_model(self, schema_name: str) -> type:
        try:
            return SCHEMA_REGISTRY[schema_name]
        except KeyError as exc:
            raise KeyError("Unknown schema: %s" % schema_name) from exc

    def list_models(self) -> Iterable[str]:
        return sorted(SCHEMA_REGISTRY.keys())

    def serialize(self, model: SchemaModel) -> Dict[str, Any]:
        if not isinstance(model, SchemaModel):
            raise TypeError("model must inherit from SchemaModel.")
        return model.to_dict()

    def deserialize(self, schema_name: str, payload: Dict[str, Any]) -> SchemaModel:
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary.")
        model_cls = self.get_model(schema_name)
        return model_cls.from_dict(payload)

    def validate_payload(self, schema_name: str, payload: Dict[str, Any]) -> SchemaModel:
        return self.deserialize(schema_name, payload)
