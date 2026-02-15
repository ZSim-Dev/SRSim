from typing import ClassVar

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RequestModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )


class ResponseBaseModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
