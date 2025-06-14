# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/000_core.ipynb.

# %% auto 0
__all__ = ['logger', 'cache_location', 'cache_dir', 'disk_cache', 'P', 'R', 'get_git_root', 'load_env', 'merge_list_dicts',
           'new_combinations', 'dict_cartesian_product', 'NamedLambda', 'maybe_await', 'get_input_output_from_cache',
           'mock_from_dict', 'FlushingStreamHandler', 'checkLogs', 'jinja_undeclared_vars', 'jinja_render',
           'json_undeclared_vars', 'json_render', 'wrap_exception', 'is_valid_object', 'get_missing', 'has_missing']

# %% ../nbs/000_core.ipynb 3
import os
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

from itertools import count,product
from joblib import Memory
import stringdale
from typing import Dict, List, Iterator, Any

# %% ../nbs/000_core.ipynb 5
def get_git_root():
        return Path(stringdale.__file__).parent.parent


# %% ../nbs/000_core.ipynb 7
def load_env(path=None):
    if path is None:
        path = get_git_root() / '.env.dev'
    else:
        path = Path(path)
    return load_dotenv(path)

# %% ../nbs/000_core.ipynb 10
import os

# %% ../nbs/000_core.ipynb 12
# Create a cache directory in the user's home directory
cache_location = os.environ.get('DISKCACHE','.cache')
cache_dir = get_git_root() / cache_location
cache_dir.mkdir(parents=True, exist_ok=True)
# Initialize the Memory object for caching
disk_cache = Memory(cache_dir, verbose=0)

# %% ../nbs/000_core.ipynb 14
def _count_multiplicity(sets):
    """Count how many times each unique item appears across multiple sets.
    """
    # Combine all sets and count frequencies
    counter = Counter()
    for s in sets:
        counter.update(s)
    return counter

def _duplicates(sets):
    """Check if any item appears in more than one set.
    """
    counts = _count_multiplicity(sets)
    return [item for item,count in counts.items() if count > 1]

def merge_list_dicts(dict1, dict2):
    """Merge two dictionaries with list values by concatenating their lists.
    
    Args:
        dict1: defaultdict(list) or dict with list values
        dict2: dict with list values
    
    Returns:
        defaultdict(list) with concatenated lists
    """
    result = defaultdict(list, dict1)
    for k, v in dict2.items():
        result[k].extend(v)
    return result

# %% ../nbs/000_core.ipynb 17
from itertools import product

# %% ../nbs/000_core.ipynb 18
def new_combinations(
    new_params: Dict[str, List],
    old_params: Dict[str, List]
) -> Iterator[Dict[str,Any]]:
    """
    Generate cartesian product of parameters by first choosing new/old for each parameter.
    Skip combinations that only use old parameters.
    
    Args:
        new_params: Dictionary of new parameter values to try
        old_params: Dictionary of previously tried parameter values
    """
    # Get all parameter names
    param_names = list(set(new_params) | set(old_params))
    
    # Generate all possible new/old choices for each parameter (True=new, False=old)
    for choices in product([True, False], repeat=len(param_names)):
        # Skip if all choices are old
        if not any(choices):
            continue
        
        # For each parameter, use either new or old values based on choice
        param_values = []
        for param_name, use_new in zip(param_names, choices):
            if use_new:
                values = new_params.get(param_name, [])
            else:
                values = old_params.get(param_name, [])
            param_values.append(values)
        
        # Generate combinations for this new/old choice pattern
        yield dict(zip(param_names, param_values))


# %% ../nbs/000_core.ipynb 22
def dict_cartesian_product(input_dict, keys):
    """
    Generate cartesian products of dictionary values for specified keys while preserving other keys.
    
    Args:
        input_dict (dict): Input dictionary with list values
        keys (list): List of keys to generate products from
        
    Returns:
        list[dict]: List of dictionaries containing all possible combinations
    """
    # Get the lists of values for the specified keys
    value_lists = [input_dict[key] for key in keys]
    
    # Generate cartesian product of the values
    products = product(*value_lists)
    
    # Create dictionaries for each product combination
    result = []
    for values in products:
        # Start with a copy of the original dict
        new_dict = input_dict.copy()
        # Update only the specified keys with their new values
        for key, value in zip(keys, values):
            new_dict[key] = value
        result.append(new_dict)
    
    return result


# %% ../nbs/000_core.ipynb 26
class NamedLambda():
    def __init__(self,name,func):
        self.name = name
        self.func = func

    def __call__(self,*args,**kwargs):
        return self.func(*args,**kwargs)

    def __repr__(self):
        return f'{self.name}'

# %% ../nbs/000_core.ipynb 28
from typing import Union,Awaitable,Callable,Any
import inspect
import asyncio

# %% ../nbs/000_core.ipynb 29
async def maybe_await(func_or_coro: Any, args, kwargs) -> Any:
    """
    Prefer __acall__ if it exists, otherwise try normal async/sync calling patterns
    """
    if hasattr(func_or_coro, '__call__'):
        if inspect.iscoroutinefunction(func_or_coro.__call__):
            return await func_or_coro.__call__(*args, **kwargs)
        else:
            return func_or_coro.__call__(*args, **kwargs)
    elif inspect.iscoroutinefunction(func_or_coro):
        return await func_or_coro(*args, **kwargs)
    elif inspect.iscoroutine(func_or_coro):
        return await func_or_coro
    elif callable(func_or_coro):
        return func_or_coro(*args, **kwargs)
    else:
        return func_or_coro

# %% ../nbs/000_core.ipynb 30
async def maybe_await(func_or_coro: Any, args, kwargs) -> Any:
    """
    Prefer __acall__ if it exists, otherwise try normal async/sync calling patterns
    """
    if inspect.iscoroutinefunction(func_or_coro):
        # print('iscoroutinefunction')
        coro = func_or_coro(*args, **kwargs)  # Get the coroutine object
        res = await coro  # Await it before returning
        return res
    elif hasattr(func_or_coro, '__call__'):
        if inspect.iscoroutinefunction(func_or_coro.__call__):
            return await func_or_coro.__call__(*args, **kwargs)
        else:
            return func_or_coro.__call__(*args, **kwargs)
    elif inspect.iscoroutine(func_or_coro):
        return await func_or_coro  # Already a coroutine, just await it
    elif callable(func_or_coro):
        return func_or_coro(*args, **kwargs)
    else:
        return func_or_coro

# %% ../nbs/000_core.ipynb 36
import pickle
from typing import Dict, Any, Tuple
import inspect
from joblib.memory import MemorizedFunc
import json
from pydantic import BaseModel

# %% ../nbs/000_core.ipynb 37
def get_input_output_from_cache(func) -> Dict[Tuple, Any]:
    """Extracts input/output pairs from a joblib Memory cache
    
    Args:
        func: The cached function (must be decorated with joblib.Memory.cache)
        
    Returns:
        Dict[Tuple, Any]: Dictionary mapping input tuples (args, kwargs) to outputs
    """
    # Check if function is a MemorizedFunc type
    if not isinstance(func, MemorizedFunc):
        raise ValueError(f"Function {func.__name__} doesn't appear to be cached with joblib.Memory")
    
    # Get all cache directories for this function
    backend_path = Path(func.store_backend.location)
    func_name = func.func.__name__
    func_cache_dirs = list(backend_path.glob(f"*/{func_name}"))
    
    if not func_cache_dirs:
        raise ValueError(f"No cache found for function {func_name} in {func.store_backend.location}")
    
    cache_dict = {}
    for func_cache_dir in func_cache_dirs:
        for output_file in func_cache_dir.glob('**/output.pkl'):
            # Get output from output.pkl
            with open(output_file, 'rb') as f:
                output = pickle.load(f)
            
            # Get inputs from metadata.json
            metadata_file = output_file.parent / 'metadata.json'
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                input_args = metadata.get('input_args', {})
                # Create a hashable key from the input args
                cache_key = frozenset(input_args.items())
                cache_dict[cache_key] = output
        
    return cache_dict

# %% ../nbs/000_core.ipynb 38
def mock_from_dict(func, cache_dict: Dict[Tuple, Any], call_on_missing: bool = True):
    """Creates a mock function that uses cached results from a dictionary,
    optionally calling the original function for missing inputs
    
    Args:
        func: The original function to mock
        cache_dict: Dictionary mapping input tuples (args, kwargs) to outputs
        call_on_missing: If True, calls original function when input not in cache
        
    Returns:
        callable: A function that returns cached results or calls the original
    """
    # Get the original function's signature
    sig = inspect.signature(func.func if isinstance(func, MemorizedFunc) else func)
    
    def mocked_func(*args, **kwargs):
        # Convert args to kwargs using the function signature
        bound_args = sig.bind(*args, **kwargs)
        all_kwargs = bound_args.arguments
        
        # Create cache key from kwargs
        cache_key = frozenset(all_kwargs.items())
        
        if cache_key in cache_dict:
            return cache_dict[cache_key]
        elif call_on_missing:
            return func(**all_kwargs)
        else:
            raise KeyError(f"No cached result for inputs: {all_kwargs}")
    
    return mocked_func

# %% ../nbs/000_core.ipynb 42
from contextlib import contextmanager
import logging

# Create a handler that flushes after each write
class FlushingStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

@contextmanager
def checkLogs(level: int=logging.DEBUG, name :str='__main__', toFile: str|Path=None,format="%(message)s"):
    """context manager for temporarily changing logging levels. used for debugging purposes

    Args:
        level (logging.Level: optional): logging level to change the logger to. Defaults to logging.DEBUG.
        name (str: optional): module name to raise logging level for. Defaults to root logger
        toFile (Path: optional): File to output logs to. Defaults to None
        

    Yields:
        [logging.Logger]: the logger object that we raised the level of
    """
    logger = logging.getLogger(name)
    current_level = logger.getEffectiveLevel()
    format = "%(name)s - %(levelname)s - %(message)s"
    logger.setLevel(level)
    if len(logger.handlers) == 0:
        pass
        sh = FlushingStreamHandler()
        sh.setFormatter(logging.Formatter(format))
        logger.addHandler(sh)
    if toFile != None:
        fh = logging.FileHandler(toFile)
        fh.setFormatter(logging.Formatter(format))
        logger.addHandler(fh)
    try:
        yield logger
    finally:
        logger.setLevel(current_level)
        if toFile != None:
            logger.removeHandler(fh)
        if len(logger.handlers) == 1:
            logger.handlers= []

# %% ../nbs/000_core.ipynb 44
from jinja2 import Template, Environment, PackageLoader, meta

def jinja_undeclared_vars(template):
    """Computes all undeclared vars in a jinja template

    Args:
        template (Path or str): Path to file of template or string with the template content

    Returns:
        set: set of all undeclared vars
    """
    if isinstance(template, Path):
        template = template.read_text()
    env = Environment()
    parsed_content = env.parse(template)
    return meta.find_undeclared_variables(parsed_content)


# %% ../nbs/000_core.ipynb 45
def jinja_render(template, params: dict, silent=True, to_file: Path = None):
    """renders a jinja template

    Args:
        template (Path or str): Path to file of template or string with the template content
        params (Dict): parameter dictionary with the variables to render into the template
        silent (Bool, Optional): Whether to print the rendered template to screen, defaults to False
        to_file (Path, Optional): If a path is supplied, prints the template to the file of said path

    Returns:
        set: set of all undeclared vars
    """
    if isinstance(template, Path):
        template = template.read_text()
    instance_str = Template(template).render(**params)

    if not silent:
        print(instance_str)

    if to_file:
        to_file.write_text(instance_str)
        return None
    else:
        return instance_str

# %% ../nbs/000_core.ipynb 46
from typing import Any,Dict
from copy import deepcopy
from textwrap import dedent


# %% ../nbs/000_core.ipynb 47
def _clean_whitespace(content: str) -> str:
    """Clean whitespace in content by removing empty lines at start/end and dedenting.
    
    Args:
        content: String content to clean
        
    Returns:
        Cleaned content string
    """
    if not isinstance(content, str):
        return content
    return dedent(content).strip()

def json_undeclared_vars(data: Any) -> set:
    """Recursively traverse a JSON-like object and collect all undeclared Jinja variables.
    
    Args:
        data: JSON-like object to analyze
        
    Returns:
        set: Set of all undeclared variables found in the structure
        
    Examples:
        >>> data = {
        ...     "user_{{name}}": {
        ...         "age": "{{age}} years old",
        ...         "greeting": "Hello {{name}}!"
        ...     }
        ... }
        >>> json_undeclared_vars(data)
        {'name', 'age'}
    """
    undeclared = set()
    
    if isinstance(data, dict):
        # Check keys and values
        for k, v in data.items():
            if isinstance(k, str):
                undeclared.update(jinja_undeclared_vars(k))
            undeclared.update(json_undeclared_vars(v))
    elif isinstance(data, list):
        # Check list elements
        for item in data:
            undeclared.update(json_undeclared_vars(item))
    elif isinstance(data, str):
        # Check string for variables
        undeclared.update(jinja_undeclared_vars(data))
    
    return undeclared

def json_render(data: Any, context: Dict[str, Any],clean_whitespace: bool = True) -> Any:
    """Recursively traverse a JSON-like object and render all strings using Jinja.
    
    Args:
        data: JSON-like object to render
        context: Dictionary of variables to use for rendering
        
    Returns:
        Rendered copy of the input data structure
        
    Examples:
        >>> context = {"name": "Alice", "age": 30}
        >>> data = {
        ...     "user_{{name}}": {
        ...         "age": "{{age}} years old",
        ...         "greeting": "Hello {{name}}!"
        ...     }
        ... }
        >>> json_render(data, context)
        {
            "user_Alice": {
                "age": "30 years old",
                "greeting": "Hello Alice!"
            }
        }
    """
    # Deep copy to avoid modifying original
    data = deepcopy(data)
    
    if isinstance(data, dict):
        # Create new dict with rendered keys and recursively rendered values
        return {
            jinja_render(str(k), context): json_render(v, context,clean_whitespace) 
            for k, v in data.items()
        }
    elif isinstance(data, list):
        # Recursively render list elements
        return [json_render(item, context,clean_whitespace) for item in data]
    elif isinstance(data, str):
        # Render string values
        if clean_whitespace:
            return _clean_whitespace(jinja_render(data, context))
        else:
            return jinja_render(data, context)
    else:
        # Return non-string values unchanged
        return data

# %% ../nbs/000_core.ipynb 50
from functools import wraps
import inspect
from typing import Callable, TypeVar, ParamSpec
from .core import jinja_render


# %% ../nbs/000_core.ipynb 51
P = ParamSpec("P")
R = TypeVar("R")

def wrap_exception(template: str, verbose: bool = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that adds context to exceptions using a template string.
    
    Args:
        template: A jinja template string that can reference function kwargs
        verbose: If True, includes all local variables in error message
    
    Example:
        @helpful_context("Failed to process {{filename}}")
        def process_file(filename: str):
            ...
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        required_vars = jinja_undeclared_vars(template)
        if 'self' in required_vars:
            raise ValueError("self is not allowed in template strings")
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get bound arguments
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Get local variables at time of error
                frame = inspect.trace()[-2][0]
                local_vars = {k:v for k,v in frame.f_locals.items() 
                            if not k.startswith('__')}
                
                # Combine args and locals for template rendering
                template_vars = {**bound_args.arguments, **local_vars}
                template_vars = {k:repr(v) for k,v in template_vars.items()}

                # cant render self since it clashes with the render class of jinja
                if 'self' in template_vars:
                    template_vars.pop('self')
                                
                # Render template with combined context
                context_msg = jinja_render(template, template_vars)
                
                # Build error message
                error_parts = [
                    f"{context_msg}",
                ]
                
                # Add locals if verbose
                if verbose:
                    error_parts.extend([
                        f"\nLocal variables in {func.__name__}() at time of error:",
                        *[f"  {k} = {repr(v)}" for k,v in local_vars.items()]
                    ])
                
                # Add original error at the end
                error_parts.append(f"{str(e)}")
                
                raise type(e)("\n".join(error_parts)) from e
                
        return wrapper
    return decorator

# %% ../nbs/000_core.ipynb 55
def is_valid_object(obj, model):
    try:
        model.model_validate(obj)
        return True
    except Exception as e:
        return False

# %% ../nbs/000_core.ipynb 58
from enum import Enum
from pydantic import Field
from typing import Union

#| export
def get_missing(model, keys=None):
    """
    Recursively check a model for Missing or None values and return a list of keys with Missing/None values.
    
    Args:
        model: A pydantic model instance or dict
        keys: Optional list of specific keys to check. If None, checks all keys.
    
    Returns:
        list: List of keys (as strings) that have Missing or None values
    """
    missing_keys = []
    
    # Convert BaseModel to dict if needed
    if isinstance(model, BaseModel):
        model = model.model_dump()
    
    # If keys is provided, only check those specific keys
    items_to_check = model.items()
    if keys is not None:
        items_to_check = [(k, model.get(k)) for k in keys if k in model]

    for key, value in items_to_check:
        # Check for Missing enum or None
        if value is None:
            missing_keys.append(key)
        # Recursively check nested structures
        elif isinstance(value, (dict, BaseModel)):
            nested_keys = None if keys is None else [
                k.split('.', 1)[1] for k in (keys or [])
                if k.startswith(f"{key}.") and '.' in k
            ]
            if nested_keys != []:  # Only recurse if we have nested keys to check or keys is None
                nested_missing = get_missing(value, nested_keys)
                missing_keys.extend(f"{key}.{k}" for k in nested_missing)
                
    return missing_keys

def has_missing(model, keys=None):
    return len(get_missing(model, keys)) > 0


# %% ../nbs/000_core.ipynb 59
from sqlmodel import Field,SQLModel
from typing import Optional
