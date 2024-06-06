import abc
from string import Formatter
from typing import Any, Collection, Dict

import requests


class Endpoint(abc.ABC):
    def __init__(self, url: str, param_names: Collection[str] = None):
        if param_names is not None:
            param_names = tuple(param_names)
        self.url = url
        self.param_names = param_names
        self.url_params = (fname for _, fname, _,
                           _ in Formatter().parse(self.url) if fname)

    def _check_params(self, params: Dict[str, Any]) -> None:
        if self.param_names is None:
            return

        missing_params = set(self.param_names).difference(set(params))
        extra_params = set(params).difference(set(self.param_names))

        error_msg = f'{self.__class__.__name__} {self.url}.'
        is_error = False

        if missing_params:
            error_msg += f'\nMissing params: ({", ".join(missing_params)}).'
            is_error = True

        if extra_params:
            error_msg += f'\nUnexpected params: ({", ".join(extra_params)}).'
            is_error = True

        if is_error:
            raise ValueError(error_msg)

    def _parse_url_params(self, params):
        url_params = {fname: params.pop(fname) for fname in self.url_params}
        url = self.url
        if url_params:
            url = self.url.format(**url_params)
        return url, params

    def __call__(self, **params) -> Any:
        self._check_params(params)
        url, params = self._parse_url_params(params)
        result = self._execute_request(url, params)
        if result.status_code != 200:
            raise ValueError(result.status_code)
        return result.json()

    @abc.abstractmethod
    def _execute_request(url: str, params: Dict[str, Any]) -> requests.Request:
        raise NotImplementedError()


class GetEndpoint(Endpoint):
    def _execute_request(self, url: str, params: Dict[str, Any]) -> requests.Request:
        return requests.get(url, params=params, headers={'accept': 'application/json'})


class PostEndpoint(Endpoint):
    def _execute_request(self, url: str, params: Dict[str, Any]) -> requests.Request:
        return requests.post(url, json=params, headers={'accept': 'application/json'})