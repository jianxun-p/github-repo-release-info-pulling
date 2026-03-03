import inspect
import functools
import unittest


FUNCTION_CALLING_TOOL_ATTR = "_tool_schema"
CLASS_TOOL_ATTR = "_tools"
CLASS_TOOL_MAP_ATTR = "_tools_map"


def function_calling_tool(func):
    """
    Decorator that creates a function definition schema for OpenAI function calling.
    It inspects the function signature and docstring to build the schema.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Get the function signature
    sig = inspect.signature(func)
    
    # Get the docstring for description
    doc = inspect.getdoc(func) or ""
    description = doc.split("\n")[0].strip(" \r\n\t") if doc else ""

    # Prepare parameters schema
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }

    # Parse docstring for parameter descriptions
    param_docs = {}
    if doc:
        for line in doc.split("\n"):
            line = line.strip()
            if line.startswith("@param"):
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    param_name = parts[1].rstrip(":")
                    param_desc = parts[2]
                    param_docs[param_name] = param_desc

    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for name, param in sig.parameters.items():
        if name == "self":  # Skip 'self' for methods
            continue
            
        # Determine the JSON type
        json_type = "string"  # Default
        if param.annotation != inspect.Parameter.empty:
            json_type = type_mapping.get(param.annotation, "string")
        
        # Build property definition
        prop_def = {"type": json_type}
        if name in param_docs:
            prop_def["description"] = param_docs[name]
        
        parameters["properties"][name] = prop_def
        
        # Add to required if no default value
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(name)

    # Attach the schema to the wrapper function
    setattr(
        wrapper,
        FUNCTION_CALLING_TOOL_ATTR, 
        {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": parameters
            }
        }
    )
    
    return wrapper

def class_tool(cls):
    """
    Decorator to mark a class as a tool. It can be used to identify tool classes.
    """
    setattr(cls, CLASS_TOOL_ATTR, [
        getattr(getattr(cls, attr), FUNCTION_CALLING_TOOL_ATTR, None) 
        for attr in dir(cls) 
        if hasattr(getattr(cls, attr), FUNCTION_CALLING_TOOL_ATTR)
    ])
    setattr(cls, CLASS_TOOL_MAP_ATTR, {
        getattr(getattr(cls, attr), FUNCTION_CALLING_TOOL_ATTR, {}).get("function", {}).get("name", ""): getattr(cls, attr)
        for attr in dir(cls) 
        if hasattr(getattr(cls, attr), FUNCTION_CALLING_TOOL_ATTR)
    })
    return cls


class TestFunctionCallingTool(unittest.TestCase):

    def test_class_tool(self):

        @class_tool
        class ExampleClass:

            @function_calling_tool
            def example_method(self, x: int, y: str = "default"):
                """
                This is an example method.
                
                @param x: The integer parameter.
                @param y: The string parameter with a default value.
                """
                return f"x: {x}, y: {y}"
            
            @function_calling_tool
            def example_method2(self, x: int, y: str):
                """
                This is second example method.
                
                @param x: The integer parameter.
                @param y: The string parameter.
                """
                return f"x: {x}, y: {y}"

        self.assertTrue(hasattr(ExampleClass, CLASS_TOOL_ATTR))
        self.assertTrue(hasattr(ExampleClass, CLASS_TOOL_MAP_ATTR))
        self.assertEqual(len(getattr(ExampleClass, CLASS_TOOL_ATTR)), 2)
        self.assertEqual(len(getattr(ExampleClass, CLASS_TOOL_MAP_ATTR)), 2)
        self.assertEqual(getattr(ExampleClass, CLASS_TOOL_ATTR), [
            {
                "type": "function",
                "function": {
                    "name": "example_method",
                    "description": "This is an example method.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "The integer parameter."},
                            "y": {"type": "string", "description": "The string parameter with a default value."}
                        },
                        "required": ["x"],
                        "additionalProperties": False
                    }
                }
            }, {
                "type": "function",
                "function": {
                    "name": "example_method2",
                    "description": "This is second example method.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "The integer parameter."},
                            "y": {"type": "string", "description": "The string parameter."}
                        },
                        "required": ["x", "y"],
                        "additionalProperties": False
                    }
                }
            }
        ])
        self.assertEqual(getattr(ExampleClass, CLASS_TOOL_MAP_ATTR), {
            "example_method": ExampleClass.example_method,
            "example_method2": ExampleClass.example_method2
        })
        

    def test_function_calling_tool(self):
        @function_calling_tool
        def example_function(x: int, y: str = "default"):
            """
            This is an example function.
            
            @param x: The integer parameter.
            @param y: The string parameter with a default value.
            """
            return f"x: {x}, y: {y}"
        
        expected_schema = {
            "type": "function",
            "function": {
                "name": "example_function",
                "description": "This is an example function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "The integer parameter."},
                        "y": {"type": "string", "description": "The string parameter with a default value."}
                    },
                    "required": ["x"],
                    "additionalProperties": False
                }
            }
        }
        
        self.assertEqual(example_function._tool_schema, expected_schema)

if __name__ == "__main__":
    unittest.main()


