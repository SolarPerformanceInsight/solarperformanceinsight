from typing import Dict, Any, Union


default_get_responses: Dict[Union[int, str], Dict[str, Any]] = {
    401: {},
    403: {},
    404: {},
}
