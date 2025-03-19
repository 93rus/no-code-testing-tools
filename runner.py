from copy import deepcopy

import yaml
import requests


def run_api_test(test_config):
    response = requests.request(
        test_config['request']['method'],
        test_config['request']['url']
    )
    results = []

    context = {
        'status': response.status_code,
        'body': response.json()
    }

    def change_values(data):
        if isinstance(data, dict):
            return {k: change_values(v) for k, v in data.items()}
        if isinstance(data, str) and data.startswith('{{') and data.endswith('}}'):
            path = data[2:-2].strip().split('.')
            value = context
            try:
                for p in path:
                    value = value[p] if isinstance(value, dict) else value[int(p)]
                return value
            except (KeyError, IndexError, TypeError):
                return None
        return data

    for assertion in test_config['assertions']:
        assertion_copy = deepcopy(assertion)
        assertion_type = list(assertion.keys())[0]
        assertion_data = assertion_copy[assertion_type]

        resolved_data = change_values(assertion_data)

        result = {
                'endpoint': test_config['name'],
                'type': assertion_type,
                'expected': resolved_data['expected_result'],
                'actual': resolved_data['actual_result'],
                'passed': resolved_data['actual_result'] == resolved_data['expected_result']
        }

        results.append(result)

    return results


def running_test_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    results = []
    for test in config.get('tests'):
        if test.get('type') == 'rest_api':
            results.extend(run_api_test(test))
    return {'tests': results}
