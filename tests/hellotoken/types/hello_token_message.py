from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class HelloJSONValue(typing.TypedDict):
    recipient: list[int]


class HelloValue(typing.TypedDict):
    recipient: list[int]


class HelloJSON(typing.TypedDict):
    value: HelloJSONValue
    kind: typing.Literal["Hello"]


@dataclass
class Hello:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Hello"
    value: HelloValue

    def to_json(self) -> HelloJSON:
        return HelloJSON(
            kind="Hello",
            value={
                "recipient": self.value["recipient"],
            },
        )

    def to_encodable(self) -> dict:
        return {
            "Hello": {
                "recipient": self.value["recipient"],
            },
        }


HelloTokenMessageKind = typing.Union[Hello]
HelloTokenMessageJSON = typing.Union[HelloJSON]


def from_decoded(obj: dict) -> HelloTokenMessageKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Hello" in obj:
        val = obj["Hello"]
        return Hello(
            HelloValue(
                recipient=val["recipient"],
            )
        )
    raise ValueError("Invalid enum object")


def from_json(obj: HelloTokenMessageJSON) -> HelloTokenMessageKind:
    if obj["kind"] == "Hello":
        hello_json_value = typing.cast(HelloJSONValue, obj["value"])
        return Hello(
            HelloValue(
                recipient=hello_json_value["recipient"],
            )
        )
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Hello" / borsh.CStruct("recipient" / borsh.U8[32]))
