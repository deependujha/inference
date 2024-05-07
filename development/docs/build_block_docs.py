import json
import os
import re
from typing import Dict, List, Set, Tuple, Type

from inference.core.utils.file_system import dump_text_lines, read_text_file
from inference.enterprise.workflows.entities.base import OutputDefinition
from inference.enterprise.workflows.entities.types import STEP_AS_SELECTED_ELEMENT
from inference.enterprise.workflows.execution_engine.introspection.blocks_loader import (
    describe_available_blocks,
)
from inference.enterprise.workflows.execution_engine.introspection.connections_discovery import (
    discover_blocks_connections,
)
from inference.enterprise.workflows.execution_engine.introspection.entities import (
    SelectorDefinition, BlockDescription,
)
from inference.enterprise.workflows.execution_engine.introspection.schema_parser import (
    parse_block_manifest_schema,
)
from inference.enterprise.workflows.prototypes.block import WorkflowBlock

DOCS_ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "docs",
    )
)

BLOCK_DOCUMENTATION_FILE = os.path.join(DOCS_ROOT_DIR, "workflows", "blocks.md")
KINDS_DOCUMENTATION_FILE = os.path.join(DOCS_ROOT_DIR, "workflows", "kinds.md")
BLOCK_DOCUMENTATION_DIRECTORY = os.path.join(DOCS_ROOT_DIR, "workflows", "blocks")
KINDS_DOCUMENTATION_DIRECTORY = os.path.join(DOCS_ROOT_DIR, "workflows", "kinds")
AUTOGENERATED_BLOCKS_LIST_TOKEN = "<!--- AUTOGENERATED_BLOCKS_LIST -->"
AUTOGENERATED_KINDS_LIST_TOKEN = "<!--- AUTOGENERATED_KINDS_LIST -->"

USER_CONFIGURATION_HEADER = [
    "| **Name** | **Type** | **Description** | Refs |",
    "|:---------|:---------|:----------------|:-----|",
]

BLOCK_DOCUMENTATION_TEMPLATE = """
# {class_name}

{description}

## Properties

{block_inputs}

The **Refs** column marks possibility to parametrise the property with dynamic values available 
in `workflow` runtime. See *Bindings* for more info.

## Available Connections

Check what blocks you can connect to `{class_name}`.

- inputs: {input_connections}
- outputs: {output_connections}

The available connections depend on its binding kinds. Check what binding kinds 
`{class_name}` has.

??? tip "Bindings"

    - input
    
{block_input_bindings}

    - output
    
{block_output_bindings}


??? tip "Example JSON definition of {class_name} step"

    ```json
    {example}
    ```
"""

BLOCK_CARD_TEMPLATE = '<p class="card block-card" data-url="{data_url}" data-name="{data_name}" data-desc="{data_desc}" data-labels="{data_labels}" data-author="{data_authors}"></p>\n'

KIND_PAGE_TEMPLATE = """
# Kind `{kind_name}`
{description}

## Details
{details}
"""


def main() -> None:
    os.makedirs(BLOCK_DOCUMENTATION_DIRECTORY, exist_ok=True)
    os.makedirs(KINDS_DOCUMENTATION_DIRECTORY, exist_ok=True)
    lines = read_text_file(
        path=BLOCK_DOCUMENTATION_FILE,
        split_lines=True,
    )
    start_index, end_index = get_auto_generation_markers(
        documentation_lines=lines,
        token=AUTOGENERATED_BLOCKS_LIST_TOKEN,
    )
    block_card_lines = []
    blocks_description = describe_available_blocks()
    block_type2manifest_type_identifier = {
        block.block_class: block.manifest_type_identifier
        for block in blocks_description.blocks
    }
    blocks_connections = discover_blocks_connections(
        blocks_description=blocks_description
    )
    generated_kinds_index_lines = []
    for declared_kind in blocks_description.declared_kinds:
        description = (
            declared_kind.description
            if declared_kind.description is not None
            else "Not available."
        )
        details = (
            declared_kind.docs if declared_kind.docs is not None else "Not available."
        )
        kind_page = KIND_PAGE_TEMPLATE.format(
            kind_name=declared_kind.name, description=description, details=details
        )
        relative_link = (
            f"/workflows/kinds/{slugify_kind_name(kind_name=declared_kind.name)}"
        )
        generated_kinds_index_lines.append(
            f"* [`{declared_kind.name}`]({relative_link}): {description}\n"
        )
        kind_file_path = build_kind_page_path(kind_name=declared_kind.name)
        with open(kind_file_path, "w") as documentation_file:
            documentation_file.write(kind_page)
    kinds_index_lines = read_text_file(
        path=KINDS_DOCUMENTATION_FILE,
        split_lines=True,
    )
    kinds_start_index, kinds_end_index = get_auto_generation_markers(
        documentation_lines=kinds_index_lines,
        token=AUTOGENERATED_KINDS_LIST_TOKEN,
    )
    kinds_index_lines = (
        kinds_index_lines[: kinds_start_index + 1]
        + generated_kinds_index_lines
        + kinds_index_lines[kinds_end_index:]
    )
    dump_text_lines(
        path=KINDS_DOCUMENTATION_FILE,
        content=kinds_index_lines,
        allow_override=True,
        lines_connector="",
    )
    for block in blocks_description.blocks:
        block_type = block.block_schema.get("block_type", "").upper()
        block_license = block.block_schema.get("license", "").upper()

        short_description = block.block_schema.get("short_description", "")
        long_description = block.block_schema.get("long_description", "")

        documentation_file_name = camel_to_snake(block.manifest_type_identifier) + ".md"
        documentation_file_path = os.path.join(
            BLOCK_DOCUMENTATION_DIRECTORY, documentation_file_name
        )
        example_definition = generate_example_step_definition(block=block)
        documentation_content = BLOCK_DOCUMENTATION_TEMPLATE.format(
            class_name=block.manifest_type_identifier,
            description=long_description,
            block_inputs=format_block_inputs(block.block_schema),
            block_input_bindings=format_input_bindings(block.block_schema),
            block_output_bindings=format_block_outputs(block.outputs_manifest),
            input_connections=format_block_connections(
                connections=blocks_connections.input_connections.block_wise[
                    block.block_class
                ],
                block_type2manifest_type_identifier=block_type2manifest_type_identifier,
            ),
            output_connections=format_block_connections(
                connections=blocks_connections.output_connections.block_wise[
                    block.block_class
                ],
                block_type2manifest_type_identifier=block_type2manifest_type_identifier,
            ),
            example="\n\t".join(json.dumps(example_definition, indent=4).split("\n")),
        )
        with open(documentation_file_path, "w") as documentation_file:
            documentation_file.write(documentation_content)
        block_card_line = BLOCK_CARD_TEMPLATE.format(
            data_url=camel_to_snake(block.manifest_type_identifier),
            data_name=block.manifest_type_identifier,
            data_desc=short_description,
            data_labels=", ".join([block_type, block_license]),
            data_authors="",
        )
        block_card_lines.append(block_card_line)

    lines = lines[: start_index + 1] + block_card_lines + lines[end_index:]
    dump_text_lines(
        path=BLOCK_DOCUMENTATION_FILE,
        content=lines,
        allow_override=True,
        lines_connector="",
    )


def get_auto_generation_markers(
    documentation_lines: List[str],
    token: str,
) -> Tuple[int, int]:
    lines_with_token_indexes = search_lines_with_token(
        lines=documentation_lines, token=token
    )
    if len(lines_with_token_indexes) != 2:
        raise RuntimeError(
            f"Please inject two {AUTOGENERATED_BLOCKS_LIST_TOKEN} "
            f"tokens to signal start and end of autogenerated table."
        )
    return lines_with_token_indexes[0], lines_with_token_indexes[-1]


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def build_kind_page_path(kind_name: str) -> str:
    kind_file_name = f"{slugify_kind_name(kind_name=kind_name)}.md"
    return os.path.join(KINDS_DOCUMENTATION_DIRECTORY, kind_file_name)


def slugify_kind_name(kind_name: str) -> str:
    kind_name = re.sub(r"[\[\] ]+", r"_", kind_name.lower())
    kind_name = camel_to_snake(name=kind_name)
    return kind_name.strip("_")


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def format_block_inputs(block_schema: dict) -> str:
    parsed_schema = parse_block_manifest_schema(schema=block_schema)
    rows = []
    for input_description in parsed_schema.primitive_types.values():
        ref_appear = input_description.property_name in parsed_schema.selectors
        rows.append(
            f"| `{input_description.property_name}` | `{input_description.type_annotation}` | "
            f"{input_description.property_description}. | {'✅' if ref_appear else '❌'} |"
        )
    return "\n".join(USER_CONFIGURATION_HEADER + rows)


def format_input_bindings(block_schema: dict) -> str:
    parsed_schema = parse_block_manifest_schema(schema=block_schema)
    rows = []
    for selector in parsed_schema.selectors.values():
        kinds_annotation = prepare_selector_kinds_annotation(selector=selector)
        rows.append(
            f"        - `{selector.property_name}` (*{kinds_annotation}*): {selector.property_description}."
        )
    return "\n".join(rows)


def prepare_selector_kinds_annotation(selector: SelectorDefinition) -> str:
    type_annotation_chunks = set()
    for allowed_reference in selector.allowed_references:
        if allowed_reference.selected_element == STEP_AS_SELECTED_ELEMENT:
            type_annotation_chunks.add("step")
            continue
        for kind in allowed_reference.kind:
            relative_link = f"/workflows/kinds/{slugify_kind_name(kind_name=kind.name)}"
            type_string = f"[`{kind.name}`]({relative_link})"
            type_annotation_chunks.add(type_string)
    type_annotation_str = ", ".join(type_annotation_chunks)
    if len(type_annotation_chunks) > 1:
        return f"Union[{type_annotation_str}]"
    return type_annotation_str


def format_block_outputs(outputs_manifest: List[OutputDefinition]) -> str:
    rows = []

    for output in outputs_manifest:
        if len(output.kind) == 1:
            relative_link = (
                f"/workflows/kinds/{slugify_kind_name(kind_name=output.kind[0].name)}"
            )
            kind = output.kind[0].name
            description = output.kind[0].description
            rows.append(
                f"        - `{output.name}` ([`{kind}`]({relative_link})): {description}."
            )
        else:
            kind = ", ".join(
                [
                    f"[`{k.name}`](/workflows/kinds/{slugify_kind_name(kind_name=k.name)})"
                    for k in output.kind
                ]
            )
            description = " or ".join(
                [f"{k.description} if `{k.name}`" for k in output.kind]
            )
            rows.append(f"        - `{output.name}` (*Union[{kind}]*): {description}.")

    return "\n".join(rows)


def format_block_connections(
    connections: Set[Type[WorkflowBlock]],
    block_type2manifest_type_identifier: Dict[Type[WorkflowBlock], str],
) -> str:
    if len(connections) == 0:
        return "None"
    connections = [
        (
            f"[`{block_type2manifest_type_identifier[connection]}`]"
            f"(/workflows/blocks/{camel_to_snake(block_type2manifest_type_identifier[connection])})"
        )
        for connection in connections
    ]
    return ", ".join(connections)


def generate_example_step_definition(block: BlockDescription) -> dict:
    result = {
        "name": "<your_step_name_here>",
        "type": block.manifest_type_identifier,
    }
    for property_name, property_definition in block.block_schema["properties"].items():
        if property_name in result:
            continue
        examples = property_definition.get("examples", [])
        if len(examples) == 0:
            example = "<block_do_not_provide_example>"
        else:
            example = examples[0]
        result[property_name] = example
    return result


if __name__ == "__main__":
    main()
