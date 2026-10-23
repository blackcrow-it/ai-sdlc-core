"""Minimal JSON Schema subset validator (type, enum, required, properties,
additionalProperties, items, min/maxItems, uniqueItems, minLength, pattern, minimum/maximum).
Not a complete JSON Schema implementation; core schemas only use this subset."""
import json
import re

_PY_TYPES = {'string': str, 'object': dict, 'array': list, 'boolean': bool, 'null': type(None)}


def _is_type(value, name):
    if name == 'integer':
        return type(value) is int
    if name == 'number':
        return type(value) in (int, float)
    return isinstance(value, _PY_TYPES[name])


def validate(value, schema, where='$'):
    types = schema.get('type')
    if types is not None:
        names = types if isinstance(types, list) else [types]
        if not any(_is_type(value, n) for n in names):
            return [f'{where}: expected {"|".join(names)}']
    errors = []
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{where}: must be one of {schema["enum"]}')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{where}: must have at least {schema["minLength"]} characters')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            errors.append(f'{where}: does not match pattern {schema["pattern"]}')
    if type(value) in (int, float):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{where}: must be >= {schema["minimum"]}')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{where}: must be <= {schema["maximum"]}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{where}: needs at least {schema["minItems"]} item(s)')
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            errors.append(f'{where}: allows at most {schema["maxItems"]} item(s)')
        if schema.get('uniqueItems'):
            seen = [json.dumps(item, sort_keys=True) for item in value]
            if len(seen) != len(set(seen)):
                errors.append(f'{where}: items must be unique')
        if 'items' in schema:
            for index, item in enumerate(value):
                errors += validate(item, schema['items'], f'{where}[{index}]')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for name in schema.get('required', []):
            if name not in value:
                errors.append(f'{where}: missing required field "{name}"')
        extra = schema.get('additionalProperties', True)
        for name, item in value.items():
            if name in props:
                errors += validate(item, props[name], f'{where}.{name}')
            elif extra is False:
                errors.append(f'{where}: unexpected field "{name}"')
            elif isinstance(extra, dict):
                errors += validate(item, extra, f'{where}.{name}')
    return errors
