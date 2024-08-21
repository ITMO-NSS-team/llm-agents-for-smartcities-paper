import os
from pathlib import Path
from typing import List, Dict

from utils.logging_config import PATH_TO_LOGS, CORR_ID_LENGTH


def get_records_by_id(corr_id: str) -> List[str]:
    """
    Finds log entries for the corresponding CorrelationID
    Args:
        corr_id: correlation id for the request
    Returns:
        List of all log records for passed CorrelationID
    """
    result_logs = []

    with open(PATH_TO_LOGS) as f:
        for line in f:
            if corr_id[:CORR_ID_LENGTH] in line:
                result_logs.append(line)

    return result_logs


def filter_records(records_to_filter: List[str]) -> str:
    """
    Filters and removes unnecessary information from log entries
    Args:
        records_to_filter: raw log entries from app
    Returns:
        Clean log records to be sent with the response
    """
    filtered_logs = []
    keywords_to_keep = [
        'Territory name',
        'Territory type',
        # 'Selected zone',
        'Selected pipeline',
        'Selected functions',
        'Chunk metadata'
    ]
    for record in records_to_filter:
        record = ' '.join(record.strip().split(' ')[5:])
        if any(keyword in record for keyword in keywords_to_keep):
            filtered_logs.append(record)
    return '\n'.join(filtered_logs)


def get_records_by_query(query: str) -> Dict[str, str]:
    """
    Finds log entries by specified word/phrase/question and prints them to
    stdout
    Args:
        query: word/phrase/question for which records should be searched
    Returns:
        Returns a dictionary with id as keys and logs as values or empty
        dictionary if no records were found
    """
    result_logs_dict = {}
    logs_dir = Path(PATH_TO_LOGS).parent

    for filename in os.listdir(logs_dir):
        corr_ids = set()
        with open(Path(logs_dir, filename)) as f:
            for line in f:
                corr_id = line.strip().split(' ')[4][1:-1]
                if query in line:
                    corr_ids.add(corr_id)
        for corr_id in corr_ids:
            with open(Path(logs_dir, filename)) as f:
                for line in f:
                    if (corr_id in line) and (result_logs_dict.get(corr_id) is
                                              not None):
                        result_logs_dict[corr_id] += line
                    elif corr_id in line:
                        result_logs_dict[corr_id] = line

    if not result_logs_dict:
        print('No records were found')
    else:
        for k in result_logs_dict.keys():
            print(f'Logs for request {k}:\n{result_logs_dict[k]}')

    return result_logs_dict


if __name__ == '__main__':
    phrase_to_search = input('Enter a phrase to search for logs: ')
    res = get_records_by_query(phrase_to_search)
